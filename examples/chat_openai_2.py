from openai import OpenAI
from root import RootSignals
from root.validators import Validator

# Connect to the Root Signals API
rs_client = RootSignals()

model = "gpt-3.5-turbo"
skill = rs_client.skills.create(
    name="My chatbot",
    intent="Simple Q&A chatbot",
    system_message="You are a helpful assistant.",
    model=model,
    validators=[Validator(evaluator_name="Truthfulness", threshold=0.8)],
)

# Start chatting with the skill
client = OpenAI(base_url=skill.openai_base_url, api_key=rs_client.api_key)
messages = [
    {"role": "user", "content": "Why is the sky blue?"},
]
completion = client.chat.completions.create(
    model=model, messages=messages, stream=True
)
for chunk in completion:
    print(chunk.choices[0].delta.content)
# The sky appears blue because of the way sunlight interacts ...
