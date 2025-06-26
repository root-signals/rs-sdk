/**
 * Basic Evaluation Example
 * 
 * This example demonstrates the fundamental usage of Root Signals evaluators:
 * - Connecting to the API
 * - Listing available evaluators
 * - Executing evaluations
 * - Handling results and errors
 */

import { RootSignals, RootSignalsError } from '../src/index.js';

async function main() {
  try {
    // Connect to the Root Signals API
    const client = new RootSignals({ 
      apiKey: process.env.ROOTSIGNALS_API_KEY!,
      // Optional: Configure timeout and retry behavior
      timeout: 30000,
      retry: {
        maxRetries: 3,
        baseDelay: 1000
      }
    });

    console.log('🚀 Starting basic evaluation example...\n');

    // 1. List available evaluators
    console.log('📋 Listing available evaluators:');
    const evaluators = await client.evaluators.list({ limit: 5 });
    evaluators.results.forEach(evaluator => {
      console.log(`  - ${evaluator.name}: ${evaluator.description || 'No description'}`);
    });
    console.log();

    // 2. Execute a preset evaluator by name
    console.log('🎯 Executing Helpfulness evaluator:');
    const helpfulnessResult = await client.evaluators.executeByName('Helpfulness', {
      request: "Where can I find the application instructions?",
      response: "You can find the instructions from our Careers page."
    });

    console.log(`  Score: ${helpfulnessResult.score} / 1.0`);
    console.log(`  Justification: ${helpfulnessResult.justification}`);
    console.log();

    // 3. Execute another evaluator with more context
    console.log('🎯 Executing Politeness evaluator:');
    const politenessResult = await client.evaluators.executeByName('Politeness', {
      request: "I'm having trouble with my account",
      response: "I'd be happy to help you with your account issue. Could you please provide more details about what specific problem you're experiencing?",
      context: "Customer support interaction"
    });

    console.log(`  Score: ${politenessResult.score} / 1.0`);
    console.log(`  Justification: ${politenessResult.justification}`);
    console.log();

    // 4. Get specific evaluator details
    if (evaluators.results.length > 0) {
      const firstEvaluator = evaluators.results[0];
      console.log(`📖 Getting details for evaluator: ${firstEvaluator.name}`);
      const evaluatorDetails = await client.evaluators.get(firstEvaluator.id);
      console.log(`  ID: ${evaluatorDetails.id}`);
      console.log(`  Name: ${evaluatorDetails.name}`);
      console.log(`  Intent: ${evaluatorDetails.intent}`);
      console.log();
    }

    console.log('✅ Basic evaluation example completed successfully!');

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