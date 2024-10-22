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

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field

from sandbox.runners.types import CommandRunResult, CommandRunStatus, Language  # nopycln: import
from sandbox.server.sandbox_api import RunCodeRequest, RunCodeResponse, RunStatus  # nopycln: import

# OJ related


class Prompt(BaseModel):
    id: int | str
    prompt: str
    labels: Dict[str, Any] = {}


class TestConfig(BaseModel):
    '''
    custom_extract_logic: a piece of python code that calls `submit_code_blocks(cbs)` to extract custom code
                          cbs: List[CodeBlock], CodeBlock(priority=40, code='xxx', language='xxx')
                          priority: fenced = 30, incomplete fenced = 20, heuristic = 10
    '''
    __test__ = False
    dataset_type: Optional[str] = Field(
        None,
        examples=[None],
        description='the dataset class used to process, only works when the dataset id is not registered.')
    language: Optional[Language] = None
    locale: Optional[str] = None
    is_fewshot: Optional[bool] = None
    compile_timeout: Optional[float] = None
    run_timeout: Optional[float] = None
    custom_extract_logic: Optional[str] = None
    provided_data: Optional[List[Dict[str, Any]] | Dict[str, Any]] = None
    extra: Dict[str, Any] = {}


class GeneralStdioTest(BaseModel):
    # stdin / stdout for the standard streams, other names for files
    input: Dict[str, str]
    output: Dict[str, str]


class EvalTestCase(BaseModel):
    passed: bool
    exec_info: RunCodeResponse
    test_info: Optional[Dict[str, Any]] = None


class EvalResult(BaseModel):
    id: int | str
    accepted: bool
    extracted_code: str
    full_code: Optional[str] = None
    test_code: Optional[str] = None
    tests: List[EvalTestCase]
    extracted_type: Optional[Literal['fenced', 'incomplete_fenced', 'heuristic', 'empty']] = None
    extra: Optional[Dict] = None


class GetPromptsRequest(BaseModel):
    dataset: str
    config: TestConfig
    offset: int = 0
    limit: int = 1000000


class GetPromptByIdRequest(BaseModel):
    dataset: str
    config: TestConfig
    id: int | str


class SubmitRequest(BaseModel):
    dataset: str
    id: int | str
    completion: str
    config: TestConfig


class GetMetricsRequest(BaseModel):
    dataset: str
    config: TestConfig
    results: List[EvalResult]


class GetMetricsFunctionRequest(BaseModel):
    dataset: str
    config: TestConfig


class GetMetricsFunctionResult(BaseModel):
    function: Optional[str]


class CodingDataset(ABC):
    subclasses_by_dataset = {}

    def __init_subclass__(cls, dataset_ids: List[str], **kwargs):
        super().__init_subclass__(**kwargs)
        for dataset_id in dataset_ids:
            cls.subclasses_by_dataset[dataset_id] = cls

    @classmethod
    def get_subclass_by_dataset(cls, dataset_id) -> 'CodingDataset':
        return cls.subclasses_by_dataset.get(dataset_id)

    @classmethod
    def get_subclass_by_name(cls, class_name) -> 'CodingDataset':
        subclass_map = {}
        for subcls in cls.__subclasses__():
            subclass_map[subcls.__name__] = subcls
            if hasattr(subcls, 'class_aliases'):
                for name in subcls.class_aliases:
                    subclass_map[name] = subcls
        return subclass_map.get(class_name)

    @classmethod
    def get_table_name(cls, dataset_id: str) -> str:
        if hasattr(cls, 'table_names'):
            if dataset_id in cls.table_names:
                return cls.table_names[dataset_id]
        return f'code_eval_{dataset_id}'

    @classmethod
    async def get_ids(cls, request: GetPromptsRequest) -> List[int | str]:
        prompts = await cls.get_prompts(request)
        return [p.id for p in prompts]

    @classmethod
    async def get_num_problems(cls, dataset_id: str) -> int:
        raise NotImplementedError(f"get_num_problems method not implemented for {cls.__name__}")

    @classmethod
    @abstractmethod
    async def get_prompts(cls, request: GetPromptsRequest) -> List[Prompt]:
        ...

    @classmethod
    @abstractmethod
    async def get_prompt_by_id(cls, request: GetPromptByIdRequest) -> Prompt:
        ...

    @classmethod
    @abstractmethod
    async def evaluate_single(cls, request: SubmitRequest) -> EvalResult:
        ...
