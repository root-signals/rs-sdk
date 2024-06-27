from root import RootSignals
from root.validators import AValidator

aclient = RootSignals(run_async=True)


async def main():
    evaluator_skill = await aclient.evaluators.acreate(
        name="Cooking recipe",
        intent="This skill will evaluate if the answer is a cooking recipe.",
        predicate="Is the following a cooking recipe: {{output}}",
        model="gpt-4o",
    )

    cooking_skill = await aclient.skills.acreate(
        name="Cooking skill with a custom evaluator",
        prompt="Find me a good recipe for Italian food.",
        validators=[
            AValidator(evaluator_id=evaluator_skill.id, threshold=0.1),
            AValidator(
                evaluator_name="Truthfulness",
                threshold=0.5,
            ),
        ],
    )
    response = await cooking_skill.arun()

    # Check if the recipe was about cooking
    print(response.validation)
