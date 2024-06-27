from root import RootSignals
from root.data_loader import WebPageDataLoader

# Create a client
client = RootSignals()

# Create a skill
skill = client.skills.create(
    name="My kimchi cooking assistant",
    intent="This skill will find you a recipe for kimchi.",
    prompt=(
        "Find me good recipes for kimchi. "
        "Use this web page for ingredients {{kimchi_ingredients}}"
    ),
    model="gpt-3.5-turbo",
    fallback_models=["gpt-4"],
    data_loaders=[
        WebPageDataLoader(
            name="kimchi_ingredients",
            url="https://en.wikipedia.org/wiki/Kimchi",
        )
    ],
)
response = skill.run()
print(response)

# llm_output='Kimchi, a traditional Korean side dish, is renowned for
# its unique taste and health benefits. Made from salted and fermented
# vegetables, it uses seasonings such as gochugaru (Korean chili
# powder), ... Here are a few recipes for you to try at
# home:\n\n1. Traditional Napa Cabbage Kimchi:\n\nIngredients:...'
