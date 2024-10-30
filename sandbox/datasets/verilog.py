# Copyright 2024 Bytedance Ltd. and/or its affiliates
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import base64
import json
from typing import Any, Dict, List, Optional

from sandbox.database import get_row_by_id_in_table, get_rows_in_table
from sandbox.datasets.types import (
    CodingDataset,
    EvalResult,
    EvalTestCase,
    GetPromptByIdRequest,
    GetPromptsRequest,
    Prompt,
    RunCodeRequest,
    RunStatus,
    SubmitRequest,
    TestConfig,
)
from sandbox.utils.common import ensure_json
from sandbox.utils.extraction import extract_code_from_freeform_completion_v2
from sandbox.utils.sandbox_client import run_code_in_sandbox


class VerilogDataset(CodingDataset, dataset_ids=['verilogeval_human', 'verilogeval_machine']):
    table_names = {
        'verilogeval_human': 'code_eval_verilogeval_human',
        'verilogeval_machine': 'code_eval_verilogeval_machine'
    }

    @classmethod
    async def get_num_problems(cls, dataset_id: str) -> int:
        return {'verilogeval_human': 156, 'verilogeval_machine': 143}[dataset_id]

    @classmethod
    async def get_prompts(cls, request: GetPromptsRequest) -> List[Prompt]:
        rows = await get_rows_in_table(
            request,
            cls.get_table_name(request.dataset),
            columns=['id', 'code_preface', 'description', "labels"],
        )
        for row in rows:
            ensure_json(row, 'labels')
        return [cls._generate_single_prompt(r, request.config) for r in rows]

    @classmethod
    async def get_prompt_by_id(cls, request: GetPromptByIdRequest) -> Prompt:
        row = await get_row_by_id_in_table(request,
                                           cls.get_table_name(request.dataset),
                                           columns=['id', 'code_preface', 'description', "labels"])
        ensure_json(row, 'labels')
        return cls._generate_single_prompt(row, request.config)

    @staticmethod
    def _build_prompt(code_preface: str, description: str, system_prompt: str, question_prompt: str,
                      fewshot: Optional[str]) -> str:
        if fewshot:
            sep = '----------------'
            prompt = f"{fewshot}\n\n{sep}\n\nQuestion:\n{system_prompt}\n{question_prompt}\n{description}\n```verilog\n{code_preface}```\n\nAnswer:"
        else:
            prompt = f"{system_prompt}\n{question_prompt}\n{description}\n```verilog\n{code_preface}```"
        return prompt

    @classmethod
    def _generate_single_prompt(cls, row: Dict[str, Any], config: TestConfig) -> Prompt:
        code_preface = row['code_preface']
        description = row['description']
        system_prompt = row['labels']['system_prompt']
        question_prompt = row['labels']['question_prompt']
        fewshot = row['labels']['fewshot'] if config.is_fewshot else None
        prompt = cls._build_prompt(code_preface, description, system_prompt, question_prompt, fewshot)
        return Prompt(id=row['id'], prompt=prompt)

    @classmethod
    async def evaluate_single(cls, request: SubmitRequest) -> EvalResult:
        row = await get_row_by_id_in_table(request,
                                           cls.get_table_name(request.dataset),
                                           columns=['task_id', 'code_preface', 'canonical_solution', "test"])

        task_id = row['task_id']
        code_preface = row['code_preface']
        canonical_solution = row['canonical_solution']
        test = row['test']
        completion, _ = extract_code_from_freeform_completion_v2(request.completion,
                                                                 language='verilog',
                                                                 first_block_only=True)
        full_code = code_preface + completion
        # save the result in the following JSON Lines (jsonl) format,
        # where each sample is formatted into a single line like so:
        # {"task_id": "Corresponding VerilogEval task ID", "completion": "Completion only without the prompt"}
        samples = json.dumps({"task_id": task_id, "completion": completion}).encode("utf-8")
        problem_file = json.dumps({
            "task_id": task_id,
            "prompt": code_preface,
            "canonical_solution": canonical_solution,
            "test": test
        }).encode("utf-8")
        files = {'samples.jsonl': samples, "problem_file.jsonl": problem_file}
        files = {key: base64.b64encode(value).decode('utf-8') for key, value in files.items()}
        result = await run_code_in_sandbox(
            RunCodeRequest(
                code='',
                files=files,
                language='verilog',
                compile_timeout=request.config.compile_timeout or 60,
                run_timeout=request.config.run_timeout or 30,
            ))
        accepted = result.status == RunStatus.Success
        if accepted:
            # if result.status == RunStatus.Success, we should check run_result for detailed stdout info
            stdout = result.run_result.stdout
            try:
                # check if the last line of standard output is {'pass@1': 1}
                # (Jing): Maybe we should try a more elegant manner
                info = json.loads(
                    stdout.strip('\n').split('\n')[-1].replace("\'", "\"").replace('np.float64(', '').replace(')', ''))
                accepted = info["pass@1"] == 1
            except Exception as e:
                accepted = False

        return EvalResult(id=request.id,
                          accepted=accepted,
                          extracted_code=completion,
                          full_code=full_code,
                          tests=[EvalTestCase(
                              passed=accepted,
                              exec_info=result,
                          )])
