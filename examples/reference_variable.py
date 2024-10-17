import tempfile

from root import RootSignals
from root.skills import ReferenceVariable

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
)

response = skill.run(
    {
        "email_dataset": (
            "Which email has the longest non-domain part?"
            "Respond with just the email address."
        )
    },
)
print(response.llm_output)
