from root import RootSignals

# Connect to the Root Signals API
client = RootSignals()

result = client.evaluators.Helpfulness(response="You can find the instructions from our Careers page.")

print(f"Score: {result.score} / 1.0")  # A normalized score between 0 and 1
print(result.justification)  # The reasoning for the score
