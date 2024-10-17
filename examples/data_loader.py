from root import RootSignals
from root.data_loader import WebPageDataLoader

# Create a client
client = RootSignals()

# Create a skill
skill = client.skills.create(
    name="My kimchi cooking assistant",
    intent="This skill will find you a recipe for kimchi.",
    prompt=(
        "Help me prepare Kimchi. "
        "Use this web page for ingredients {{kimchi_ingredients}}"
    ),
    model="gpt-4o",
    fallback_models=["gpt-4"],
    data_loaders=[
        WebPageDataLoader(
            name="kimchi_ingredients",
            url="https://simple.wikipedia.org/wiki/Kimchi",
        )
    ],
)
response = skill.run()
print(response)
