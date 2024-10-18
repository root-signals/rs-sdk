from root import RootSignals

# Connect to the Root Signals API
client = RootSignals()

result = client.evaluators.Clarity(
    response="""I only use direct language without any weasel words.
                I am clear and concise.""",
)

print(result.score)
