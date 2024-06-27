from openai import OpenAI
from root import RootSignals
from root.validators import Validator

# Connect to the Root Signals API
rs_client = RootSignals()

model = "gpt-3.5-turbo"
another_model = "gpt-4"

skill = rs_client.skills.create(
    name="My chatbot",
    intent="Simple Q&A chatbot",
    system_message="You are a helpful assistant.",
    model=model,
    fallback_models=[another_model],
    validators=[Validator(evaluator_name="Truthfulness", threshold=0.8)],
)

# Start chatting with the skill (non-streaming)
client = OpenAI(base_url=skill.openai_base_url, api_key=rs_client.api_key)

messages = [
    # {"role": "system", "content": "You are a helpful assistant."},
    # ^ implicit in skill
    {"role": "user", "content": "Why is the sky blue?"},
]
completion = client.chat.completions.create(model=model, messages=messages)
print(completion.choices[0].message.content)
# The sky appears blue because of the way sunlight interacts ...


# We can use either the model, or one of the fallback models defined for the
# skill. We will use the fallback model here.
messages = [
    {"role": "user", "content": "Why is the sky blue?"},
]
completion = client.chat.completions.create(
    model=another_model, messages=messages
)
print(completion.choices[0].message.content)
# The sky appears blue because of the way sunlight interacts ...


# We can get the full execution details, including the validation results
log = rs_client.execution_logs.get(log_id=completion.id)
print(log.validation_results)
# [
#   evaluator_name: Truthfulness
#   result: 0.9
#   is_valid: true
#   ...
# ]
