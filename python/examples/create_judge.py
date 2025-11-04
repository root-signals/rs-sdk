from scorable import Scorable
from scorable.generated.openapi_client.models.evaluator_reference_request import EvaluatorReferenceRequest
from scorable.skills import Evaluators

# Connect to the Scorable API
client = Scorable()

evaluator_references = [
    EvaluatorReferenceRequest(id=Evaluators.Eval.Truthfulness.value),
    EvaluatorReferenceRequest(id=Evaluators.Eval.Relevance.value),
]

judge = client.judges.create(
    name="Custom Returns Policy Judge",
    intent="Evaluate customer service responses about return policies",
    evaluator_references=evaluator_references,
)

results = client.judges.run(
    judge.id,
    request="What's your return policy?",
    response="We have a 30-day return policy. If you're not satisfied with your purchase, "
    "you can return it within 30 days for a full refund.",
    contexts=[
        "Returns are accepted within thirty (30) calendar days of the delivery date. "
        "Eligible items accompanied by valid proof of purchase will receive a full refund, issued via the original method of payment."
    ],
)
print(results)
