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
                id: 'code_contests_train',
                huggingFace: {
                    id: 'sine/FusedCodeContests',
                    split: 'train',
                },
            },
            {
                id: 'code_contests_valid',
                huggingFace: {
                    id: 'sine/FusedCodeContests',
                    split: 'valid',
                },
            },
            {
                id: 'code_contests_test',
                huggingFace: {
                    id: 'sine/FusedCodeContests',
                    split: 'test',
                },
            },
        ]
    },
}

export const constants = {
    image: 'vemlp-cn-beijing.cr.volces.com/preset-images/code-sandbox:opensource_20241022',
    host: 'http://localhost:8080',
    datasets,
}