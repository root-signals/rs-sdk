from concurrent.futures import ThreadPoolExecutor

from root import RootSignals

# Connect to the Root Signals API
client = RootSignals()


def main():
    response = "This is polite and clear."

    tasks = [
        (client.evaluators.Politeness, response),
        (client.evaluators.Clarity, response),
    ]

    with ThreadPoolExecutor() as executor:
        future_to_eval = {func.__name__: executor.submit(func, response) for func, response in tasks}
        for future in future_to_eval:
            result = future_to_eval[future].result()
            print(f"Evaluation result for {future}: {result}")
