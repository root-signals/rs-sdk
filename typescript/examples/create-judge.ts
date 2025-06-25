import { RootSignals } from '../src/index.js';

// Connect to the Root Signals API
const client = new RootSignals({ apiKey: process.env.ROOTSIGNALS_API_KEY! });

const evaluatorReferences = [
  { id: 'truthfulness-evaluator-id' },
  { id: 'relevance-evaluator-id' }
];

const judge = await client.judges.create({
  name: "Custom Returns Policy Judge",
  intent: "Evaluate customer service responses about return policies",
  evaluator_references: evaluatorReferences
});

const results = await client.judges.execute(
  judge.id,
  {
    request: "What's your return policy?",
    response: "We have a 30-day return policy. If you're not satisfied with your purchase, " +
      "you can return it within 30 days for a full refund.",
    contexts: [
      "Returns are accepted within thirty (30) calendar days of the delivery date. " +
      "Eligible items accompanied by valid proof of purchase will receive a full refund, issued via the original method of payment."
    ]
  }
);
console.log(results);