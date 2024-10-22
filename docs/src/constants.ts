const datasets = {
    AutoEval: {
        datasets: [
            {
                id: 'leetcode_sample_python',
                huggingFace: {
                    id: 'sine/LeetCodeSample',
                    subset: 'python',
                    split: 'test',
                },
            },
        ]
    },
    HumanEval: {
        datasets: [
            {
                id: 'humaneval_python',
                huggingFace: {
                    id: 'sine/FusedHumanEvalPython',
                    split: 'test',
                },
            },
        ]
    },
    CommonOJ: {
        datasets: [
            {
                id: 'code_contests',
                huggingFace: {
                    id: 'sine/FusedHumanEvalPython',
                    split: 'test',
                },
            }
        ]
    },
}

export const constants = {
    image: 'vemlp-cn-beijing.cr.volces.com/preset-images/code-sandbox:opensource_20241022',
    host: 'http://localhost:8080',
    datasets,
}