from root import RootSignals
from root.validators import Validator

client = RootSignals()

evaluator_skill = client.skills.create(
    name="Cooking recipe evaluator",
    intent="This skill will evaluate if the answer is a cooking recipe.",
    prompt="Is the following a cooking recipe: {{output}}",
    model="gpt-3.5-turbo",
    is_evaluator=True,
)

cooking_skill = client.skills.create(
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

# {'validator_results': [{'evaluator_name': 'Cooking recipe
# evaluator', 'evaluator_id': '...', 'threshold': 0.1, 'is_valid':
# True, 'result': 0.9, 'status': 'finished'}], 'is_valid': True}
