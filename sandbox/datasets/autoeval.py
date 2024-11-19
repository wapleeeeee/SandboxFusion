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
import re
from enum import Enum
from string import Template
from typing import Any, Dict, List

from sandbox.database import get_row_by_id_in_table, get_rows_in_table
from sandbox.datasets.natural_code_bench import extract_java_code, get_java_test_assets
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
from sandbox.utils.common import ensure_json, generate_random_string
from sandbox.utils.extraction import extract_code_from_freeform_completion
from sandbox.utils.sandbox_client import run_code_in_sandbox


class ExtractCodeMode(Enum):
    """ Extract code mode.
    """
    FIRST_BLOCK_ONLY = 'first'
    MERGE_ALL_BLOCKS = 'all'

    @classmethod
    def is_valid(cls, value) -> bool:
        return value in [e.value for e in cls]


def append_test(code: str, test: str, repr_code=False):
    insert_token = '#<INSERT>'

    if insert_token in test:
        parts = test.split(insert_token)
        if repr_code:
            code = repr(code)
        full_code = parts[0] + code + parts[1]
    else:
        if 'if __name__ ==' in code:
            code = code[:code.index('if __name__ ==')]
        if repr_code:
            code = repr(code)
        full_code = code + '\n' + test

    return full_code


def postprocess_full_code(code, language):
    if language in ['go', 'go_test']:
        packages = set(re.findall(r'package\s+(\w+)', code))
        code = re.sub(r'package\s+(\w+)', '', code)
        # combine all imports
        single_imports = re.findall(r'import\s+("\w+")', code)
        multi_imports = sum([x.split('\n') for x in re.findall(r'import\s+\((.*?)\)', code, flags=re.DOTALL)], [])
        multi_imports = [x.strip() for x in multi_imports]
        imports = set(single_imports + multi_imports) - {""}
        code = re.sub(r'import\s+("\w+")', '', code)
        code = re.sub(r'import\s+\((.*?)\)', '', code, flags=re.DOTALL)
        # add all packages and imports
        code = '\n'.join([f'package {p}' for p in packages]) + '\n\n' + '\n'.join([f'import {imp}' for imp in imports
                                                                                  ]) + '\n\n' + code  # add all packages
    return code


class AutoEvalDataset(CodingDataset):
    class_aliases = ['AutoEvalV4Dataset', 'AutoEvalV5Dataset', 'AutoEvalV6Dataset']

    @classmethod
    async def get_prompts(cls, request: GetPromptsRequest) -> List[Prompt]:
        rows = await get_rows_in_table(request,
                                       cls.get_table_name(request.dataset),
                                       columns=['id', 'labels', 'content'])
        return [cls._generate_single_prompt(request.dataset, r, request.config) for r in rows]

    @classmethod
    async def get_prompt_by_id(cls, request: GetPromptByIdRequest) -> Prompt:
        row = await get_row_by_id_in_table(request,
                                           cls.get_table_name(request.dataset),
                                           columns=['id', 'labels', 'content'])
        return cls._generate_single_prompt(request.dataset, row, request.config)

    @classmethod
    def _generate_single_prompt(cls, dataset: str, row: Dict[str, Any], config: TestConfig) -> Prompt:
        ensure_json(row, 'labels')
        question = row['content']

        # Use config.extra values if available, otherwise use row['labels']
        context = config.extra.get('context', row['labels'].get('context'))
        fewshot = config.extra.get('fewshot', row['labels'].get('fewshot')) if config.is_fewshot else None
        template = config.extra.get('prompt_template', row['labels'].get('prompt_template'))

        if config.is_fewshot and fewshot is None:
            raise ValueError(f"Missing fewshot for id {row['id']}")

        if template:
            # Use the provided template if available
            prompt = Template(template).safe_substitute(question=question,
                                                        fewshot=fewshot or '',
                                                        context=context or '',
                                                        locale=config.locale)
        else:
            # Default logic if no template is provided
            if config.locale == 'zh':
                q_hint = '问题：'
                a_hint = '答案：'
            elif config.locale == 'en':
                q_hint = 'Question:'
                a_hint = 'Answer:'

            sep = '----------------'
            if context and fewshot:
                prompt = f'{context}\n\n{sep}\n\n{fewshot}\n\n{q_hint}{question}\n\n{a_hint}\n'
            elif context:
                prompt = f'{context}\n\n{q_hint}{question}\n\n{a_hint}\n'
            elif fewshot:
                prompt = f'{fewshot}\n\n{q_hint}{question}\n\n{a_hint}\n'
            else:
                prompt = question

        return Prompt(id=row['id'], prompt=prompt, labels=row['labels'])

    @classmethod
    async def evaluate_single(cls, request: SubmitRequest) -> EvalResult:
        row = await get_row_by_id_in_table(request, cls.get_table_name(request.dataset), columns=['test', 'labels'])

        ensure_json(row, 'labels')
        ensure_json(row, 'test')

        asset = row['test'].get('asset')
        if isinstance(asset, dict):
            asset = asset
        elif isinstance(asset, str):
            asset = json.loads(asset)
        else:
            asset = {}

        extract_code_mode = request.config.extra.get('autoeval_extract_code_mode',
                                                     ExtractCodeMode.FIRST_BLOCK_ONLY.value)
        assert ExtractCodeMode.is_valid(extract_code_mode), f'Invalid autoeval_extract_code_mode: {extract_code_mode}'
        first_block_only = extract_code_mode == ExtractCodeMode.FIRST_BLOCK_ONLY.value
        programming_language = row['labels']['programming_language']
        execution_language = row['labels'].get('execution_language', programming_language)
        append_flag = request.config.extra.get('append_flag') and execution_language == 'python'

        if programming_language == 'java':
            # same as NCB
            codes = extract_java_code(request.completion)
            code = '\n\n'.join(codes)
            test_code = row["test"]["code"]
            files = get_java_test_assets(codes, test_code)
            full_code = ''
            for f, c in files.items():
                decoded_code = base64.b64decode(c.encode('utf-8')).decode('utf-8')
                full_code += f'// {f}\n\n{decoded_code}\n\n'

            result = await run_code_in_sandbox(
                RunCodeRequest(code='',
                               language='junit',
                               compile_timeout=request.config.compile_timeout or 40,
                               run_timeout=request.config.run_timeout or 20,
                               files={
                                   **asset,
                                   **files
                               }))
        else:
            code, _ = extract_code_from_freeform_completion(request.completion,
                                                            programming_language,
                                                            first_block_only,
                                                            code_block_idx=request.config.extra.get('code_block_idx'))

            repr_code = request.config.extra.get('repr_code', False)

            if programming_language == 'html' and '#<INSERT>' not in row['test']['code']:
                # in this case, we just put html content into index.html to avoid escaping
                asset['index.html'] = base64.b64encode(code.encode('utf-8')).decode('utf-8')
                full_code = row['test']['code']
            else:
                full_code = append_test(code, row['test']['code'], repr_code)

            full_code = postprocess_full_code(full_code, execution_language)

            if append_flag:
                flag = generate_random_string(20)
                full_code += f'\n\nprint("{flag}")'

            result = await run_code_in_sandbox(
                RunCodeRequest(
                    code=full_code,
                    language=execution_language,
                    compile_timeout=request.config.compile_timeout or 40,
                    run_timeout=request.config.run_timeout or 20,
                    files=asset,
                ))

        accepted = result.status == RunStatus.Success

        if append_flag and flag not in result.run_result.stdout:
            accepted = False

        return EvalResult(id=request.id,
                          accepted=accepted,
                          extracted_code=code,
                          full_code=full_code,
                          tests=[EvalTestCase(
                              passed=accepted,
                              exec_info=result,
                          )])
