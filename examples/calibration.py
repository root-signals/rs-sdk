from root import RootSignals
from root.skills import EvaluatorDemonstration

client = RootSignals()

# Create an evaluator
direct_language_evaluator = client.skills.create(
    name="Direct language",
    prompt="Does the {{ output }} contain weasel words?",
    intent="Is the language direct and unambiguous",
    model="gpt-3.5-turbo",
    is_evaluator=True,
)

# Run first calibration
test_result = client.evaluators.calibrate_existing(
    evaluator_id=direct_language_evaluator.id,
    test_data=[
        ["0.1", "There will probably be a meeting tomorrow"],
        ["0.1", "We probably won't need to make any major changes."],
    ],
)
print(test_result[0].result)
#  "score": 0.5,
#  "expected_score": 0.1,

# Improve the evaluator with demonstrations, penalize the "probably" weasel word
client.skills.update(
    skill_id=direct_language_evaluator.id,
    evaluator_demonstrations=[
        EvaluatorDemonstration(
            output="The project will probably be completed on time.",
            score=0.1,
        ),
        EvaluatorDemonstration(
            output="He probably knows the answer to your question.",
            score=0.1,
        ),
        EvaluatorDemonstration(
            output="It will probably rain later today.", score=0.1
        ),
    ],
)
# Run second calibration
test_result = client.evaluators.calibrate_existing(
    evaluator_id=direct_language_evaluator.id,
    test_data=[
        ["0.1", "There will probably be a meeting tomorrow"],
        ["0.1", "We probably won't need to make any major changes."],
    ],
)

# Check the results
print(test_result[0].result)
#  "score": 0.1,
#  "expected_score": 0.1,
