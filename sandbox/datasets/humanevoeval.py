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

import inspect

from sandbox.datasets import HumanEvalDataset
from sandbox.datasets.types import SubmitRequest
from sandbox.utils.extraction import extract_code_from_freeform_completion


def get_categories(results):
    import re
    from collections import defaultdict
    categories_counts = defaultdict(list)
    for r in results:
        task_id = r.id
        cate_pattern = r'EvoEval_(.*)_EvoEval'
        cate = re.findall(cate_pattern, task_id)[0]
        categories_counts[cate].append(r)

    return categories_counts


class EvoEvalDataset(HumanEvalDataset, dataset_ids=['evoeval']):
    table_names = {'evoeval': 'code_eval_EvoEval'}

    @classmethod
    def _gen_pretrain_code(cls, request: SubmitRequest, row) -> str:
        completion = request.completion
        prompt = cls._generate_single_prompt(row, request.dataset, request.config).prompt
        code, _ = extract_code_from_freeform_completion(f'{prompt}\n{completion}',
                                                        cls.extract_lang_map[request.dataset],
                                                        first_block_only=True)
        full_code = f"{code}\n{row['test']}"
        return completion, full_code

    @classmethod
    def get_metrics_function(cls) -> str:
        source = f'''
{inspect.getsource(get_categories)}

def get_metrics(results):
    categories = get_categories(results)
    performance = {{}}
    for cat, samples in categories.items():
        for k in k_targets:
            if repeats < k:
                continue
            pak = utils_coding.pass_at_k_v2([(s.id, s.accepted) for s in samples], repeats, k)
            performance[f'{{cat}}/Pass@k={{k}}'] = pak
    return performance
'''
        return source
