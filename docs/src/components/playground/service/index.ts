import axios from 'axios';

import {
  OnlineJudgeSubmitRequest,
  OnlineJudgeSubmitResponse,
  PromptByIdRequest,
  PromptRes,
  QuestionIdListRequest,
  RunCodeRequest,
  RunCodeResponse,
} from '../types';
// https://bytedance.larkoffice.com/wiki/SR7XwD1MGiOwOhkEq0HcbRjHnXe
const domain = 'https://faas-code-sandbox.bytedance.net';

export const onlineJudgeService = {
  // 获取数据集列表
  listDatasets(): Promise<string[]> {
    return axios
      .request({
        baseURL: domain,
        url: '/online_judge/list_datasets',
        method: 'GET',
      })
      .then(res => res.data);
  },
  // 获取问题列表
  getQuestionIdList(data: QuestionIdListRequest): Promise<string[]> {
    return axios
      .request({
        baseURL: domain,
        url: '/online_judge/list_ids',
        method: 'POST',
        data,
      })
      .then(res => res.data);
  },
  // 根据问题id获取prompt
  getPromptById(data: PromptByIdRequest): Promise<PromptRes> {
    return axios
      .request({
        baseURL: domain,
        url: '/online_judge/get_prompt_by_id',
        method: 'POST',
        data,
      })
      .then(res => res.data);
  },
  // 提交答案
  submit(data: OnlineJudgeSubmitRequest): Promise<OnlineJudgeSubmitResponse> {
    return axios
      .request({
        baseURL: domain,
        url: '/online_judge/submit',
        method: 'POST',
        data,
      })
      .then(res => res.data);
  },
};

export const sandboxService = {
  // 执行代码
  runCode(data: RunCodeRequest): Promise<RunCodeResponse> {
    return axios
      .request({
        baseURL: domain,
        url: '/run_code',
        method: 'POST',
        data,
      })
      .then(res => res.data);
  },
};
