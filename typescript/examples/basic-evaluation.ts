/**
 * Basic Evaluation Example
 *
 * This example demonstrates the fundamental usage of Root Signals evaluators:
 * - Connecting to the API
 * - Listing available evaluators
 * - Executing evaluations
 * - Handling results and errors
 */

import { RootSignals } from '../src/index.js';

// Connect to the Root Signals API
const client = new RootSignals({ apiKey: process.env.ROOTSIGNALS_API_KEY! });

// Example usage: Execute an evaluator by name
const result = await client.evaluators.executeByName('Helpfulness', {
  response: 'You can find the instructions from our Careers page.',
});

console.log(`Score: ${result.score} / 1.0`); // A normalized score between 0 and 1
console.log(result.justification); // The reasoning for the score
