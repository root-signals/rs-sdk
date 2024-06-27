import tempfile

from root import RootSignals
from root.skills import ReferenceVariable
from root.validators import Validator

client = RootSignals()

with tempfile.NamedTemporaryFile(suffix=".csv", mode="w") as fp:
    fp.write("short@example.com\nlonger-email@example.com\n")
    fp.flush()
    dataset = client.datasets.create(
        name="List of email addresses", path=fp.name, type="reference"
    )

skill = client.skills.create(
    reference_variables=[
        ReferenceVariable(dataset_id=dataset.id, name="email_dataset")
    ],
    intent="Email address list assistant.",
    name="Email address dataset chatbot",
    prompt="{{email_dataset}}",
    model="gpt-4",
    validators=[
        Validator(
            evaluator_name="Email address checker",
            prompt="Is it an email address?",
            threshold=0.6,
        )
    ],
)

response = skill.run(
    {
        "email_dataset": (
            "Which email has the longest domain name?"
            "Respond with just the email address."
        )
    },
)
print(response.llm_output)
# longer-email@example.com
print(response.validation)
# {'validator_results': [{'cost': 0.000608, 'evaluator_name': 'Email
# address checker', 'threshold': 0.6,
# 'is_valid': True, 'result': 1.0, 'status': 'finished'}], 'is_valid':
# True}

# Run it with something that is not related to the dataset
blocked_response = skill.run({"email_dataset": "How can I cook Korean food?"})
# See that the response is blocked
print(blocked_response.llm_output)
# This message is not available.
print(blocked_response.validation.is_valid)
# False
