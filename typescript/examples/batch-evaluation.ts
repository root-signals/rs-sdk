/**
 * Batch Evaluation Example
 * 
 * This example demonstrates efficient batch processing of multiple evaluations:
 * - Sequential vs parallel processing
 * - Rate limiting and retry logic
 * - Performance optimization
 * - Progress monitoring
 */

import { RootSignals, RootSignalsError } from '../src/index.js';

interface EvaluationItem {
  id: string;
  request: string;
  response: string;
  expectedScore?: number;
}

async function main() {
  try {
    // Configure client with rate limiting and retry logic
    const client = new RootSignals({ 
      apiKey: process.env.ROOTSIGNALS_API_KEY!,
      rateLimit: {
        maxRequests: 10,  // 10 requests per window
        windowMs: 60000,  // 1 minute window
        strategy: 'queue' // Queue requests instead of dropping them
      },
      retry: {
        maxRetries: 3,
        baseDelay: 1000,
        maxDelay: 10000
      }
    });

    console.log('🚀 Starting batch evaluation example...\n');

    // Sample data for batch evaluation
    const evaluationData: EvaluationItem[] = [
      {
        id: 'eval-1',
        request: "How do I reset my password?",
        response: "You can reset your password by clicking the 'Forgot Password' link on the login page and following the instructions."
      },
      {
        id: 'eval-2', 
        request: "What are your business hours?",
        response: "We're open Monday through Friday, 9 AM to 6 PM EST."
      },
      {
        id: 'eval-3',
        request: "How can I contact customer support?",
        response: "You can reach our customer support team via email at support@company.com or call us at 1-800-SUPPORT."
      },
      {
        id: 'eval-4',
        request: "Do you offer refunds?",
        response: "Yes, we offer a 30-day money-back guarantee on all purchases."
      },
      {
        id: 'eval-5',
        request: "Where can I find the user manual?",
        response: "The user manual is available in the Downloads section of your account dashboard."
      }
    ];

    console.log(`📊 Processing ${evaluationData.length} evaluations...\n`);

    // Method 1: Sequential Processing (slower but safer)
    console.log('🔄 Method 1: Sequential Processing');
    const startSequential = Date.now();
    
    for (let i = 0; i < evaluationData.length; i++) {
      const item = evaluationData[i];
      console.log(`  Processing ${i + 1}/${evaluationData.length}: ${item.id}`);
      
      const result = await client.withRetryAndRateLimit(() =>
        client.evaluators.executeByName('Helpfulness', {
          request: item.request,
          response: item.response
        })
      );
      
      console.log(`    Score: ${result.score.toFixed(3)} - ${item.request.substring(0, 30)}...`);
    }
    
    const sequentialTime = Date.now() - startSequential;
    console.log(`  ⏱️  Sequential processing took: ${sequentialTime}ms\n`);

    // Method 2: Parallel Processing with Concurrency Control
    console.log('🚀 Method 2: Parallel Processing (Batched)');
    const startParallel = Date.now();
    const batchSize = 3; // Process 3 at a time to avoid overwhelming the API
    
    for (let i = 0; i < evaluationData.length; i += batchSize) {
      const batch = evaluationData.slice(i, i + batchSize);
      console.log(`  Processing batch ${Math.floor(i / batchSize) + 1}: items ${i + 1}-${Math.min(i + batchSize, evaluationData.length)}`);
      
      const batchPromises = batch.map(async (item) => {
        const result = await client.withRetryAndRateLimit(() =>
          client.evaluators.executeByName('Helpfulness', {
            request: item.request,
            response: item.response
          })
        );
        return { item, result };
      });
      
      const batchResults = await Promise.all(batchPromises);
      
      batchResults.forEach(({ item, result }) => {
        console.log(`    ${item.id}: Score ${result.score.toFixed(3)} - ${item.request.substring(0, 30)}...`);
      });
    }
    
    const parallelTime = Date.now() - startParallel;
    console.log(`  ⏱️  Parallel processing took: ${parallelTime}ms\n`);

    // Method 3: Multiple Evaluators on Same Data
    console.log('🎯 Method 3: Multiple Evaluators on Same Data');
    const sampleItem = evaluationData[0];
    const evaluators = ['Helpfulness', 'Politeness', 'Clarity'];
    
    console.log(`  Evaluating: "${sampleItem.request}" -> "${sampleItem.response}"`);
    
    const multiEvalPromises = evaluators.map(async (evaluatorName) => {
      try {
        const result = await client.withRetryAndRateLimit(() =>
          client.evaluators.executeByName(evaluatorName, {
            request: sampleItem.request,
            response: sampleItem.response
          })
        );
        return { evaluator: evaluatorName, result };
      } catch (error) {
        return { evaluator: evaluatorName, error: error instanceof Error ? error.message : 'Unknown error' };
      }
    });
    
    const multiEvalResults = await Promise.all(multiEvalPromises);
    
    multiEvalResults.forEach(({ evaluator, result, error }) => {
      if (error) {
        console.log(`    ${evaluator}: ❌ Error - ${error}`);
      } else if (result) {
        console.log(`    ${evaluator}: Score ${result.score.toFixed(3)}`);
      }
    });
    console.log();

    // Performance comparison
    const speedup = sequentialTime / parallelTime;
    console.log(`📈 Performance Summary:`);
    console.log(`  Sequential: ${sequentialTime}ms`);
    console.log(`  Parallel: ${parallelTime}ms`);
    console.log(`  Speedup: ${speedup.toFixed(2)}x faster`);
    console.log();

    console.log('✅ Batch evaluation example completed successfully!');

  } catch (error) {
    if (error instanceof RootSignalsError) {
      console.error(`❌ Root Signals API Error (${error.status}): ${error.detail}`);
      console.error(`Error Code: ${error.code}`);
    } else {
      console.error('❌ Unexpected error:', error);
    }
    process.exit(1);
  }
}

// Run the example
main().catch(console.error);