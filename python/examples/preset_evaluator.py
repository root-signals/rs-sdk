from scorable import Scorable

# Connect to the Scorable API
client = Scorable()

result = client.evaluators.Helpfulness(
    request="Where can I find the application instructions?",
    response="You can find the instructions from our Careers page.",
)

print(f"Score: {result.score} / 1.0")  # A normalized score between 0 and 1
print(result.justification)  # The reasoning for the score
