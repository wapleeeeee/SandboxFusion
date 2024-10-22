import React, { useState, useEffect } from 'react';
import { constants } from '@site/src/constants';
import CodeBlock from '@theme/CodeBlock';
import {
  Box,
  Typography,
  FormControl,
  InputLabel,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Switch,
  TextField,
  RadioGroup,
  FormControlLabel,
  Radio,
  Select,
  MenuItem,
} from '@mui/material';

interface Dataset {
  id: string;
  huggingFace: {
    id: string;
    subset?: string;
    split: string;
  }
}

interface ConfigField {
  name: string;
  type: string;
  description: string;
}

interface GenerateContext {
  selectedDataset: Dataset,
  config: Record<string, any>,
  pythonConfig: string,
  generatePythonDict: any,
}

interface DatasetSelectorProps {
  datasetKey: keyof typeof constants.datasets;
  generateDocFunc?: (context: GenerateContext) => string;
}

const generatePythonDict = (obj: Record<string, any>, indent: number = 2): string => {
  const spaces = ' '.repeat(indent);
  const entries = Object.entries(obj).map(([key, value]) => {
    if (typeof value === 'object' && value !== null) {
      return `${spaces}'${key}': ${generatePythonDict(value, indent + 2)}`;
    } else if (typeof value === 'boolean') {
      return `${spaces}'${key}': ${value ? 'True' : 'False'}`;
    } else {
      return `${spaces}'${key}': ${JSON.stringify(value)}`;
    }
  });
  return `{\n${entries.join(',\n')}\n${' '.repeat(indent - 2)}}`;
};

const DatasetSelector: React.FC<DatasetSelectorProps> = ({ datasetKey, generateDocFunc }) => {
  const datasets = constants.datasets[datasetKey].datasets;
  const [selectedDataset, setSelectedDataset] = useState<Dataset>(datasets[0]);
  const [config, setConfig] = useState<Record<string, any>>({
    locale: 'en',
    compile_timeout: 20,
    run_timeout: 20,
    extra: { is_freeform: true },
  });

  const getConfigFields = (): ConfigField[] => {
    if (datasetKey === 'HumanEval') {
      return [
        { name: 'extra.is_freeform', type: 'boolean', description: 'Use freeform mode for instruction finetuned models' },
        { name: 'locale', type: 'select', description: 'Locale of freeform prompts' },
        { name: 'compile_timeout', type: 'number', description: 'Compilation timeout in seconds' },
        { name: 'run_timeout', type: 'number', description: 'Execution timeout in seconds' },
      ];
    } else if (datasetKey === 'AutoEval') {
      return [
        { name: 'compile_timeout', type: 'number', description: 'Compilation timeout in seconds' },
        { name: 'run_timeout', type: 'number', description: 'Execution timeout in seconds' },
      ];
    } else if (datasetKey === 'CommonOJ') {
      return [
        { name: 'language', type: 'select', description: 'Programming language' },
        { name: 'locale', type: 'select', description: 'Locale of prompts' },
        { name: 'compile_timeout', type: 'number', description: 'Compilation timeout in seconds' },
        { name: 'run_timeout', type: 'number', description: 'Execution timeout in seconds' },
      ];
    }
    return [];
  };

  useEffect(() => {
    if (datasetKey === 'AutoEval') {
      setConfig({
        compile_timeout: 40,
        run_timeout: 20,
      });
    } else if (datasetKey === 'CommonOJ') {
      setConfig({
        language: 'cpp',
        locale: 'en',
        compile_timeout: 20,
        run_timeout: 20,
      });
    } else {
      setConfig({
        locale: 'en',
        compile_timeout: 20,
        run_timeout: 20,
        extra: { is_freeform: true },
      });
    }
  }, [selectedDataset, datasetKey]);

  const handleDatasetChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const datasetId = event.target.value;
    const dataset = datasets.find(d => d.id === datasetId) || datasets[0];
    setSelectedDataset(dataset);
  };

  const handleConfigChange = (field: string, value: any) => {
    if (field.startsWith('extra.')) {
      const extraField = field.split('.')[1];
      setConfig(prev => ({ ...prev, extra: { ...prev.extra, [extraField]: value } }));
    } else {
      setConfig(prev => ({ ...prev, [field]: value }));
    }
  };

  const generateCode = () => {
    const pythonConfig = generatePythonDict(config);
  
    return `from datasets import load_dataset
import requests

config = ${pythonConfig}

# Get dataset data in sandbox format
ds = load_dataset("${selectedDataset.huggingFace.id}")

config['provided_data'] = list(ds['train'])
prompts = requests.post('${constants.host}/get_prompts', json={
  'dataset': '${selectedDataset.id}',
  'config': config
})`;
  };

  const generateSubmitCode = () => {
    return `config['provided_data'] = list(ds['train'])[0]
res = requests.post('${constants.host}/submit', json={
  'dataset': '${selectedDataset.id}',
  'id': sample_id,
  'completion': completion,
  'config': config
})

print(f'result: {res.json()}')`;
  };

  const renderConfigInput = (field: ConfigField) => {
    const value = field.name.startsWith('extra.') 
      ? config.extra[field.name.split('.')[1]] 
      : config[field.name];

    switch (field.type) {
      case 'number':
        return (
          <TextField
            type="number"
            value={value}
            onChange={(e) => handleConfigChange(field.name, parseInt(e.target.value, 10))}
            fullWidth
          />
        );
      case 'boolean':
        return (
          <Switch
            checked={value}
            onChange={(e) => handleConfigChange(field.name, e.target.checked)}
            color="primary"
          />
        );
      case 'select':
        if (field.name === 'locale') {
          return (
            <RadioGroup
              value={value}
              onChange={(e) => handleConfigChange(field.name, e.target.value)}
              row
            >
              <FormControlLabel value="en" control={<Radio />} label="English" />
              <FormControlLabel value="zh" control={<Radio />} label="Chinese" />
            </RadioGroup>
          );
        } else if (field.name === 'language') {
          return (
            <Select
              value={value}
              onChange={(e) => handleConfigChange(field.name, e.target.value)}
              fullWidth
            >
              <MenuItem value="cpp">C++</MenuItem>
              <MenuItem value="python">Python</MenuItem>
              <MenuItem value="java">Java</MenuItem>
            </Select>
          );
        } else if (field.name === 'extra.autoeval_extract_code_mode') {
          return (
            <Select
              value={value}
              onChange={(e) => handleConfigChange(field.name, e.target.value)}
              fullWidth
            >
              <MenuItem value="FIRST_BLOCK_ONLY">First Block Only</MenuItem>
              <MenuItem value="ALL_BLOCKS">All Blocks</MenuItem>
            </Select>
          );
        }
        return null;
      case 'text':
        return (
          <TextField
            value={value}
            onChange={(e) => handleConfigChange(field.name, e.target.value)}
            fullWidth
            multiline
            rows={3}
          />
        );
      default:
        return (
          <TextField
            value={value}
            onChange={(e) => handleConfigChange(field.name, e.target.value)}
            fullWidth
          />
        );
    }
  };

  return (
    <Box sx={{ margin: 'auto', padding: 3 }}>
      <Typography variant="h4" gutterBottom>
        Dataset
      </Typography>
      <FormControl component="fieldset">
        <RadioGroup
          value={selectedDataset.id}
          onChange={handleDatasetChange}
        >
          {datasets.map(dataset => (
            <FormControlLabel key={dataset.id} value={dataset.id} control={<Radio />} label={dataset.id} />
          ))}
        </RadioGroup>
      </FormControl>

      <Box sx={{ my: 2 }}>
        <Typography variant="h4" gutterBottom>
          Configuration
        </Typography>
        <TableContainer component={Paper} sx={{ mb: 3 }}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Field</TableCell>
                <TableCell>Value</TableCell>
                <TableCell>Description</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {getConfigFields().map(field => (
                <TableRow key={field.name}>
                  <TableCell>{field.name}</TableCell>
                  <TableCell>{renderConfigInput(field)}</TableCell>
                  <TableCell>{field.description}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </Box>

      <Typography variant="h4" gutterBottom>
        Usage
      </Typography>
      {generateDocFunc ? generateDocFunc({
        selectedDataset,
        config,
        pythonConfig: generatePythonDict(config),
        generatePythonDict: generatePythonDict,
      }) : (
        <>
          <Typography variant="body1" gutterBottom>
            Get prompts:
          </Typography>
          <CodeBlock language="python">
            {generateCode()}
          </CodeBlock>
    
          <Typography variant="body1" sx={{ my: 2 }}>
            Perform inference on the prompts, and submit the results with:
          </Typography>
    
          <CodeBlock language="python">
            {generateSubmitCode()}
          </CodeBlock>
        </>
      )
      }

    </Box>
  );
};

export default DatasetSelector;
