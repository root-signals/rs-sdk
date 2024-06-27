from root import RootSignals
from root.validators import Validator

# Connect to the Root Signals API
client = RootSignals()

# Create an objective which describes what we are trying to do
objective_id = client.objectives.create(
    intent="Child-safe clear response",
    validators=[
        Validator(evaluator_name="Clarity", threshold=0.2),
        Validator(evaluator_name="Safety for Children", threshold=0.3),
    ],
)

# Create a skill which identifies only this particular LLM pipeline
skill = client.skills.create(name="My pipeline", objective_id=objective_id)

# Run your LLM pipeline and use the skill to evaluate the LLM output...
# llm_response = run_my_pipeline()

# Evaluate the result
llm_response = "Some LLM response I got from my custom LLM pipeline."
response = skill.evaluate(response=llm_response)

print(response)
# validation:
#   validation_results: [
#     evaluator_name: Clarity
#     result: 0.5
#     is_valid: true
#     ...
#   ]
