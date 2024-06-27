from root import RootSignals

# Connect to the Root Signals API
client = RootSignals()

evaluator_id = list(
    client.skills.list(name="Truthfulness", only_evaluators=True)
)[0].id

result = client.evaluators.run(
    evaluator_id,
    request="Return a recipe for a sauce.",
    response="""Quarter peppers and slice onion.
    I used the seeds and ribs of the peppers for optimal heat.
    Sautee in a small sauce pan with oil on medium heat.
    Keep a lid on it but stir often.""",
    contexts=[
        "This is a cookbook with many cookies recipes such as: "
        "1) Recipe for a tomato sauce",
    ],
)
print(result.score)
# 0.0
