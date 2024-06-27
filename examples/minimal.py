from root import RootSignals

# Connect to the Root Signals API
client = RootSignals()

# Create a skill
skill = client.skills.create(
    "Find me good recipes for {{food_type}} food that are {{cuisine}}."
)

# Run it
response = skill.run({"food_type": "spicy", "cuisine": "Korean"})

print(response)

# llm_output="1. Kimchi Jjigae (Kimchi Stew): This spicy and flavorful
# stew is made with fermented kimchi, pork, tofu, and vegetables. ..."
# validation={'validator_results': [], 'is_valid': True}
# model='gpt-3.5-turbo' engine='gpt-3.5-turbo'
# execution_log_id='181eb95b-b972-4e96-8e30-ca7d3447d4fe'
# rendered_prompt='Find me good recipes for spicy food that are
# Korean.'
