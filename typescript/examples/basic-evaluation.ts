import { RootSignals } from '../src/index.js';

// Connect to the Root Signals API
const client = new RootSignals({ apiKey: process.env.ROOTSIGNALS_API_KEY! });

const result = client.evaluators.executeByName('Helpfulness', {
  response: "You can find the instructions from our Careers page."
});

console.log(`Score: ${result.score} / 1.0`);  // A normalized score between 0 and 1
console.log(result.justification);  // The reasoning for the score