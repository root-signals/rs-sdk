from root import RootSignals

# Connect to the Root Signals API
client = RootSignals()

# Create a skill
skill = client.skills.create(
    """
    Classify this text into one of the following: {{categories}}
    Text: {{text}}
    """
)

# Execute it
response = skill.run(
    {
        "text": "The expectation for rate cuts has been steadily declining.",
        "categories": "Finance, Sports, Politics",
    }
)

print(response)
