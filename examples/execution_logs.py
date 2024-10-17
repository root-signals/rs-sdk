from root import RootSignals
from root.validators import Validator

# Connect to the Root Signals API
client = RootSignals()

skill = client.skills.create(
    name="My strict chatbot",
    intent="Simple Q&A chatbot",
    prompt="Provide a clear answer to the question: {{question}}",
    model="gpt-4",
    validators=[Validator(evaluator_name="Clarity", threshold=0.6)],
)

# Execute the skill
response = skill.run({"question": "What is the capital of France?"})

# Get the validation results
print(response.validation)

# Get the execution details
log = client.execution_logs.get(execution_result=response)
print(log)

# List all execution logs
iterator = client.execution_logs.list(limit=10)
print(next(iterator))
