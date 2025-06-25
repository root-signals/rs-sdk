import { RootSignals } from '../src/index.js';

const client = new RootSignals({ apiKey: process.env.ROOTSIGNALS_API_KEY! });

// Run a root evaluator by name using the executeByName method
const result = await client.evaluators.executeByName(
  'Helpfulness',
  {
    response: "You can find the instructions from our Careers page.",
    request: "Where can I find the application instructions?"
  }
);

console.log(`Score: ${result.score} / 1.0`);
console.log(`Justification: ${result.justification}`);

// Run a custom evaluator by name
// Assuming you have created a custom evaluator named "Network Troubleshooting"
try {
  const customResult = await client.evaluators.executeByName(
    'Network Troubleshooting',
    {
      request: "My internet is not working.",
      response: `
        I'm sorry to hear that your internet isn't working.
        Let's troubleshoot this step by step:
        1. Check if your router is powered on and all cables are properly connected
        2. Try restarting your router and modem
        3. Check if other devices can connect to the network
        4. Try connecting to a different network if available
      `
    }
  );

  console.log(`Score: ${customResult.score} / 1.0`);
  console.log(`Justification: ${customResult.justification}`);
} catch (error) {
  console.error(`Error: ${error}`);
  console.log(
    "Note: This example requires that you have previously created a custom evaluator named 'Network Troubleshooting'"
  );
}