# Scorable SDK Examples

This directory contains practical examples for the Scorable TypeScript SDK.

## Available Examples

### 🎯 Basic Examples
- [**basic-evaluation.ts**](./basic-evaluation.ts) - Fundamental evaluator usage with comprehensive error handling
- [**custom-evaluator.ts**](./custom-evaluator.ts) - Creating and using custom evaluators
- [**batch-evaluation.ts**](./batch-evaluation.ts) - Efficient batch processing with performance optimization

### 🔧 Advanced Examples  
- [**advanced-judges.ts**](./advanced-judges.ts) - AI-generated judges, custom judge creation, and refinement
- [**real-world-integration.ts**](./real-world-integration.ts) - Production-ready integration patterns and A/B testing
- [**error-handling-patterns.ts**](./error-handling-patterns.ts) - Comprehensive error handling and resilience patterns

### 🚀 Specialized Examples
- [**simple-judge.ts**](./simple-judge.ts) - Basic judge creation and execution
- [**create-judge.ts**](./create-judge.ts) - Detailed judge creation with evaluator references
- [**execution-logs.ts**](./execution-logs.ts) - Working with evaluation history and analytics

## Running Examples

### Prerequisites

1. Install dependencies:
```bash
npm install
```

2. Set your API key:
```bash
export SCORABLE_API_KEY="your-api-key-here"
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
Learn the fundamentals of using Scorable evaluators:
- Connecting to the API with proper configuration
- Listing and exploring available evaluators
- Executing evaluations with comprehensive error handling
- Understanding response formats and scoring

### 🔧 Advanced Judges & Custom Logic
Master sophisticated evaluation workflows:
- AI-generated judges for complex scenarios
- Custom judge creation with multiple evaluators
- Judge refinement and iterative improvement
- Multi-dimensional evaluation strategies

### 📊 Production Integration
Real-world usage patterns for production systems:
- Comprehensive monitoring and analytics
- A/B testing evaluation workflows
- Performance optimization and benchmarking
- Integration with logging and alerting systems

### 🛡️ Error Handling & Resilience
Robust error handling for production environments:
- Circuit breaker patterns for API protection
- Retry strategies with exponential backoff
- Graceful degradation and fallback mechanisms
- Partial failure handling in batch operations

### 📈 Performance & Scalability
Optimize for high-throughput scenarios:
- Efficient batch processing strategies
- Rate limiting and concurrency control
- Memory-efficient data handling
- Performance monitoring and optimization

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
3. Visit our [documentation](https://docs.scorable.ai)
4. Contact support at support@scorable.ai