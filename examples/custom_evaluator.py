from root import RootSignals

client = RootSignals()

direct_language_evaluator = client.evaluators.create(
    name="Direct language",
    predicate="Is the following text clear and has no weasel words: {{response}}",
    intent="Is the language direct and unambiguous",
    model="gpt-4o",
)

response = direct_language_evaluator.run(response="It will probably rain tomorrow.")

print(response.score)
print(response.justification)
