import asyncio

from scorable import Scorable

# Connect to the Scorable API
aclient = Scorable(run_async=True)


async def main():
    response = "This is polite and clear."

    tasks = [
        aclient.evaluators.Politeness(response),
        aclient.evaluators.Clarity(response),
    ]

    response = await asyncio.gather(*tasks)

    for future in response:
        print(f"Evaluation result for {future.evaluator_name}: {future}")
