from root import RootSignals

# Connect to the Root Signals API
client = RootSignals()

evaluator = client.evaluators.create(
    name="My evaluator",
    intent="Asses the response",
    predicate="Is this a integer in the range 0-100: {{request}}",
    model="gemini-2.0-flash",
)

# Execute the evaluator
response = evaluator.run(response="99")


# Get the execution details
log = client.execution_logs.get(execution_result=response)
print(log)

# List all execution logs
iterator = client.execution_logs.list(limit=10)
print(next(iterator))
