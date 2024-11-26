export const datasets = {
  AutoEval: {
    datasetType: "AutoEvalDataset",
    datasets: [
      {
        id: "leetcode_sample_python",
        huggingFace: {
          id: "sine/LeetCodeSample",
          subset: "python",
          split: "test",
        },
      },
    ],
  },
  HumanEval: {
    datasetType: "HumanEvalDataset",
    datasets: [
      {
        id: "humaneval_python",
        huggingFace: {
          id: "openai/openai_humaneval",
          split: "test",
        },
      },
    ],
  },
  MBPP: {
    datasetType: "MBPPDataset",
    datasets: [
      {
        id: "mbpp",
        huggingFace: {
          id: "laylarsssss/FusedMBPP",
          split: "test",
        },
      },
    ],
  },
  MHPP: {
    datasetType: "MHPPDataset",
    datasets: [
      {
        id: "mhpp",
        huggingFace: {
          id: "laylarsssss/FusedMHPP",
          split: "test",
        },
      },
    ],
  },
  MiniF2F: {
    datasetType: "MiniF2FLean4Dataset",
    datasets: [
      {
        id: "minif2f_lean4_test",
        huggingFace: {
          id: "laylarsssss/FusedMHPP",
          split: "test",
        },
      },
      {
        id: "minif2f_lean4_valid",
        huggingFace: {
          id: "laylarsssss/FusedMHPP",
          split: "test",
        },
      },
    ],
  },
  MultipleHumanEval: {
    datasetType: "HumanEvalDataset",
    datasets: [
      {
        id: "humaneval_cpp",
        huggingFace: {
          id: "nuprl/MultiPL-E",
          subset: "humaneval-cpp",
          split: "test",
        },
      },
      {
        id: "humaneval_typescript",
        huggingFace: {
          id: "nuprl/MultiPL-E",
          subset: "humaneval-ts",
          split: "test",
        },
      },
      {
        id: "humaneval_bash",
        huggingFace: {
          id: "nuprl/MultiPL-E",
          subset: "humaneval-sh",
          split: "test",
        },
      },
      {
        id: "humaneval_csharp",
        huggingFace: {
          id: "nuprl/MultiPL-E",
          subset: "humaneval-cs",
          split: "test",
        },
      },
      {
        id: "humaneval_go",
        huggingFace: {
          id: "nuprl/MultiPL-E",
          subset: "humaneval-go",
          split: "test",
        },
      },
      {
        id: "humaneval_java",
        huggingFace: {
          id: "nuprl/MultiPL-E",
          subset: "humaneval-java",
          split: "test",
        },
      },
      {
        id: "humaneval_lua",
        huggingFace: {
          id: "nuprl/MultiPL-E",
          subset: "humaneval-lua",
          split: "test",
        },
      },
      {
        id: "humaneval_javascript",
        huggingFace: {
          id: "nuprl/MultiPL-E",
          subset: "humaneval-js",
          split: "test",
        },
      },
      {
        id: "humaneval_php",
        huggingFace: {
          id: "nuprl/MultiPL-E",
          subset: "humaneval-php",
          split: "test",
        },
      },
      {
        id: "humaneval_perl",
        huggingFace: {
          id: "nuprl/MultiPL-E",
          subset: "humaneval-pl",
          split: "test",
        },
      },
      {
        id: "humaneval_racket",
        huggingFace: {
          id: "nuprl/MultiPL-E",
          subset: "humaneval-rkt",
          split: "test",
        },
      },
      {
        id: "humaneval_r",
        huggingFace: {
          id: "nuprl/MultiPL-E",
          subset: "humaneval-r",
          split: "test",
        },
      },
      {
        id: "humaneval_rust",
        huggingFace: {
          id: "nuprl/MultiPL-E",
          subset: "humaneval-rs",
          split: "test",
        },
      },
      {
        id: "humaneval_scala",
        huggingFace: {
          id: "nuprl/MultiPL-E",
          subset: "humaneval-scala",
          split: "test",
        },
      },
      {
        id: "humaneval_swift",
        huggingFace: {
          id: "nuprl/MultiPL-E",
          subset: "humaneval-swift",
          split: "test",
        },
      },
      {
        id: "humaneval_ruby",
        huggingFace: {
          id: "nuprl/MultiPL-E",
          subset: "humaneval-ruby",
          split: "test",
        },
      },
      {
        id: "humaneval_d",
        huggingFace: {
          id: "nuprl/MultiPL-E",
          subset: "humaneval-d",
          split: "test",
        },
      },
      {
        id: "humaneval_julia",
        huggingFace: {
          id: "nuprl/MultiPL-E",
          subset: "humaneval-jl",
          split: "test",
        },
      },
    ],
  },
  CommonOJ: {
    datasetType: "CommonOJDataset",
    datasets: [
      {
        id: "code_contests_train",
        huggingFace: {
          id: "sine/FusedCodeContests",
          split: "train",
        },
      },
      {
        id: "code_contests_valid",
        huggingFace: {
          id: "sine/FusedCodeContests",
          split: "valid",
        },
      },
      {
        id: "code_contests_test",
        huggingFace: {
          id: "sine/FusedCodeContests",
          split: "test",
        },
      },
    ],
  },
};

export const constants = {
  image: "volcengine/sandbox-fusion:20241104",
  host: "http://localhost:8080",
  datasets,
};
