from root import RootSignals
from root.validators import Validator

# Connect to the Root Signals API
client = RootSignals()

skill = client.skills.create(
    name="My Q&A chatbot",
    intent="Simple Q&A chatbot",
    prompt="Provide a clear answer to the question: {{question}}",
    model="gpt-4",
    validators=[Validator(evaluator_name="Clarity", threshold=0.6)],
)

# Execute the skill
response = skill.run({"question": "What is the capital of France?"})

# Get the execution details
log = client.execution_logs.get(execution_result=response)
print(log)
# cost: 0.000...
# skill:
#   name: My Q&A chatbot
#   ...
# llm_output: "The capital of France is Paris."
# rendered_prompt: "Provide a clear answer to the question: What is ..."
# validation_results: [
#   evaluator_name: Clarity
#   result: 0.9
#   is_valid: true
#   ...
# ]
# ...

# List all execution logs
iterator = client.execution_logs.list(limit=10)
print(next(iterator))
# Note that the list result does not contain the full execution details

# cost: 0.000...
# skill:
#  name: My Q&A chatbot
#  ...
