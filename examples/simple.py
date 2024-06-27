from root import RootSignals

# Connect to the Root Signals API
client = RootSignals()

# Create a skill
skill = client.skills.create(
    name="My cooking assistant",
    intent="This skill will find you a recipe for a specific type of food.",
    prompt="Find me good recipes for {{food_type}} food that are {{cuisine}}.",
    model="gpt-4",
)

# Run it
response = skill.run({"food_type": "spicy", "cuisine": "Korean"})
print(response)
# llm_output='1. Spicy Korean Chicken Stew ..'
# validation={'validator_results': [], 'is_valid': True}
# model='gpt-4' engine='gpt-4'
# execution_log_id='102fcb9b-c692-48c6-adc4-c0c729d8b360'
# rendered_prompt='Find me good recipes for spicy food that are Korean.'

# We can retrieve the skill by id
skill_2 = client.skills.get(skill_id=skill.id)
response = skill_2.run({"food_type": "spicy", "cuisine": "Korean"})

# We can also retrieve it by name
# (the list result is an iterator, so we just take first one)
#
# The name is not an unique identifier. Consequently, the .run method is not
# intentionally available. However, you can circumvent this restriction if you
# wish by using:
skill_3 = next(client.skills.list(name="My cooking assistant"))
response = client.skills.run(
    skill_3.id, {"food_type": "spicy", "cuisine": "Korean"}
)
