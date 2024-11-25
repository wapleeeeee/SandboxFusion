import { constants } from '@site/src/constants';
import CodeBlock from '@theme/CodeBlock';

export const docWithType = ({selectedDataset, datasetType, config, generatePythonDict}) => {
    config.dataset_type = datasetType;
    const pythonConfig = generatePythonDict(config);
    let load_stmt = `load_dataset("${selectedDataset.huggingFace.id}", split="${selectedDataset.huggingFace.split}")`
    if (selectedDataset.huggingFace.subset) {
      load_stmt = `load_dataset("${selectedDataset.huggingFace.id}", "${selectedDataset.huggingFace.subset}", split="${selectedDataset.huggingFace.split}")`
    }
    return  <>
      <p>
        Get prompts:
      </p>
      <CodeBlock language="python">
        {`from datasets import load_dataset
import requests

config = ${pythonConfig}

# Get dataset data in sandbox format
data = list(${load_stmt})

config['provided_data'] = data
prompts = requests.post('${constants.host}/get_prompts', json={
  'dataset': '${selectedDataset.id}',
  'config': config
})`}
      </CodeBlock>
      <p>
        Get results after model inference:
      </p>
      <CodeBlock language="python">
        {`config['provided_data'] = data[0]
res = requests.post('${constants.host}/submit', json={
  'dataset': '${selectedDataset.id}',
  'id': data[0]['id'],
  'completion': completion,
  'config': config
})

print(f'result: {res.json()}')`}
      </CodeBlock>
      <p>
        Note: always put raw completion in the request, Sandbox will handle the extraction of code according to different modes.
      </p>
    </>
  };
  