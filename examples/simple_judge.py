from root import RootSignals

# Connect to the Root Signals API
client = RootSignals()

# Generate a judge by describing your application and the stage you want to evaluate.
judge_definition = client.judges.generate(
    intent="I'm building a returns handler and want to evaluate how it explains our 30-day policy, "
    "handles discount offers, and guides through the return process. Our policy is that we offer "
    "a 30-day return policy with a 20% discount on the next purchase.",
    stage="Explanation of the 30 day return policy",
)

# You can check the full definition, including the evaluators, by getting the judge.
judge = client.judges.get(judge_definition.judge_id)
print(judge)

# Run the judge and get the results. Results are a list of evaluator executions.
results = client.judges.run(
    judge_definition.judge_id,
    request="Can I return my order? I bought a pair of shoes and they don't fit.",
    response="Yes, you can return your order for a 20% discount on the next purchase.",
    # The signature of the run method is the same as the evaluator run method. You can pass in
    # contexts, tags etc...
)

print(results)
