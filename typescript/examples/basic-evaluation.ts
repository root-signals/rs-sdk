/**
 * Basic Evaluation Example
 *
 * This example demonstrates the fundamental usage of Scorable evaluators:
 * - Connecting to the API
 * - Listing available evaluators
 * - Executing evaluations
 * - Handling results and errors
 */

import { Scorable } from '../src/index.js';

// Connect to the Scorable API
const client = new Scorable({ apiKey: process.env.SCORABLE_API_KEY! });

// Example usage: Execute an evaluator by name
const result = await client.evaluators.executeByName('Helpfulness', {
  response: 'You can find the instructions from our Careers page.',
});

console.log(`Score: ${result.score} / 1.0`); // A normalized score between 0 and 1
console.log(result.justification); // The reasoning for the score
