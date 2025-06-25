# Root Signals SDK Examples

This directory contains practical examples for the Root Signals TypeScript SDK.

## Available Examples

### Basic Examples
- [**basic-evaluation.ts**](./basic-evaluation.ts) - Simple evaluator execution and basic API usage
- [**custom-evaluator.ts**](./custom-evaluator.ts) - Creating and using custom evaluators
- [**batch-evaluation.ts**](./batch-evaluation.ts) - Efficient batch processing of multiple evaluations

## Running Examples

### Prerequisites

1. Install dependencies:
```bash
npm install
```

2. Set your API key:
```bash
export ROOTSIGNALS_API_KEY="your-api-key-here"
```

3. Build the SDK:
```bash
npm run build
```

4. Run any example:
```bash
node dist/examples/basic-evaluation.js
```

### Using Example Code

Each example is self-contained and includes:
- Complete TypeScript implementation
- Error handling best practices
- Performance considerations
- Production-ready patterns

Copy and adapt the examples for your specific use cases.

## Example Categories

### 🎯 Basic Evaluation
Learn the fundamentals of using Root Signals evaluators:
- Connecting to the API
- Listing available evaluators
- Executing simple evaluations
- Handling responses and errors

### 🔧 Custom Evaluators
Create domain-specific evaluation logic:
- Defining custom evaluation criteria
- Creating reusable evaluators
- Managing evaluator lifecycle
- Testing with various inputs

### 📊 Batch Processing
Efficiently process multiple evaluations:
- Sequential vs parallel processing
- Rate limiting and retry logic
- Performance optimization
- Progress monitoring

## Best Practices

Each example demonstrates:
- **Type Safety**: Full TypeScript types for all operations
- **Error Handling**: Robust error handling and recovery
- **Performance**: Efficient API usage patterns
- **Monitoring**: Comprehensive logging and feedback

## Getting Help

If you have questions about any example:
1. Check the inline comments in the example code
2. Review the main [README](../README.md) for SDK documentation
3. Visit our [documentation](https://docs.rootsignals.ai)
4. Contact support at support@rootsignals.ai