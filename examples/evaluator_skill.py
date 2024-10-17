from root import RootSignals
from root.validators import Validator

client = RootSignals()

evaluator_skill = client.skills.create(
    name="Cooking recipe",
    intent="This skill will evaluate if the answer is a cooking recipe.",
    prompt="Is the following a cooking recipe: {{output}}",
    model="gpt-4o",
    is_evaluator=True,
)

cooking_skill = client.skills.create(
    name="Cooking skill with a custom evaluator",
    prompt="Find me a good recipe for Italian food.",
    validators=[
        Validator(evaluator_id=evaluator_skill.id, threshold=0.1),
        Validator(
            evaluator_name="Truthfulness",
            threshold=0.5,
        ),
    ],
)
response = cooking_skill.run()

# Check if the recipe was about cooking
print(response.validation)
