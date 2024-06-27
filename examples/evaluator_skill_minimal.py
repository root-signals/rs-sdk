from root import RootSignals
from root.validators import Validator

client = RootSignals()

cooking_skill = client.skills.create(
    prompt="Find me a good recipe for Italian food.",
    validators=[
        Validator(
            evaluator_name="Cooking recipe evaluator",
            prompt="Is it a cooking recipe",
            threshold=0.1,
        ),
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
# evaluator', 'evaluator_id': ..., 'threshold': 0.1, 'is_valid': True,
# 'result': 0.8, 'status': 'finished'}], 'is_valid': True}
