from root import RootSignals

# Connect to the Root Signals API
client = RootSignals()

# Run an evaluator with tags to track the execution.
result = client.evaluators.Clarity(
    response="Sure, let me help you to fix your issue with your network connection. Start by...",
    tags=["production", "v1.23"],
)

# Get the execution log for the evaluator run.
log = client.execution_logs.get(result)
print(log)


# And get all the logs with the same tags.
logs = client.execution_logs.list(tags=["production"])
for log in logs:
    print(log.score)
