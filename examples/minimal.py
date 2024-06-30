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
    "categories": "Finance, Sports, Politics"
    }
)

print(response)

# "llm_output": "Finance",
# "validation": Validation(is_valid=True, validator_results=[]),
# "model": "gpt-3.5-turbo",
# "execution_log_id": "9b3c713d-7bdc-4f7d-a85c-ed7d92ff4a56",
# "rendered_prompt": (
#     "Classify this text into one of the following: Finance, Sports, Politics\n"
#     "Text: The expectation for rate cuts has been steadily declining."
# ),
# "cost": 5.6e-05,