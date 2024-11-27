import asyncio

from root import RootSignals

# Connect to the Root Signals API
aclient = RootSignals(run_async=True)


async def main():
    response = "This is polite and clear."

    tasks = [
        aclient.evaluators.Politeness(response),
        aclient.evaluators.Clarity(response),
    ]

    response = await asyncio.gather(*tasks)

    for future in response:
        print(f"Evaluation result for {future.evaluator_name}: {future}")
