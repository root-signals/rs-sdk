# Quickstart #

Install root-signals Python SDK from PyPI:

```bash
# pip install root-signals
```

Once it has been installed, please create an API key from the user interface ( https://app.rootsignals.ai/settings/api-keys ), and set it to your environment variable:

```bash
export ROOTSIGNALS_API_KEY=somethingreallysecretyougotfromtheweb
```

After that, you can create a new skill and execute it.

```
# python3
>>> from root import RootSignals

>>> response = RootSignals().skills.create("Find me good recipes for {{food_type}} food that are {{cuisine}}.").run({"food_type": "spicy", "cuisine": "Korean"})

>>> print(response)
#llm_output="1. Kimchi Jjigae (Kimchi Stew): This spicy and flavorful
#stew is made with fermented kimchi, pork, tofu, and vegetables. ..."
#validation={'validator_results': [], 'is_valid': True}
#model='gpt-3.5-turbo' engine='gpt-3.5-turbo'
#execution_log_id='181eb95b-b972-4e96-8e30-ca7d3447d4fe'
#rendered_prompt='Find me good recipes for spicy food that are Korean.'
```
