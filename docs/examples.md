# SDK features using concrete examples #

These examples walk through some features of the platform in more detail.

## Minimal skill

Just like the quickstart example, but broken into multiple lines for readability. The APIs typically respond with Python objects that can be used to chain requests or alternatively reuse previous calls' results.

```{literalinclude} ../examples/minimal.py
```
```json
// print(response)

"llm_output": "Finance",
"validation": "Validation(is_valid=True, validator_results=[])",
"model": "gpt-4o",
"execution_log_id": "9b3c713d-7bdc-4f7d-a85c-ed7d92ff4a56",
"rendered_prompt": "Classify this text into ...",
"cost": "5.6e-05",
```

## Simple skill

The simple skill example adds some more metadata to the skill. It specifies explicitly the model to use, the descriptive intent, and the input variables that are referred to in the prompt.

```{literalinclude} ../examples/simple.py
```
```json
// print(response)

"llm_output": "Finance",
"validation": "Validation(is_valid=True, validator_results=[])",
"model": "gpt-4",
"execution_log_id": "1181e790-7b87-457f-a2cb-6b1dfc1eddf4",
"rendered_prompt": "Classify this text into ...",
"cost": "0.00093",
```

## Skill with a validator

In order to ensure the results of skill execution remain within acceptable guardrails, we can add a validator. In this example, the validator scores the results by the clarity of the model output.

```{literalinclude} ../examples/execution_logs.py
```
```json
// print(response.validation)

"validator_results": [
  {
    "cost": "0.000...",
    "evaluator_name": "Clarity",
    "threshold": "0.6",
    "is_valid": "True",
    "result": "0.xy"
  }
]
```
```json
// print(log)

"cost": "0.000...",
"skill": {
  "name": "My Q&A chatbot",
  "..."
},
"llm_output": "The capital of France is Paris.",
"rendered_prompt": "Provide a clear answer to the question: What is ...",
"validation_results": [
  "evaluator_name": "Clarity",
  "result": "0.9",
  "is_valid": "true",
  "..."
],
"..."
```
```json
// print(next(iterator))

// Note that the list result does not contain the full execution details

{
  "cost": "0.000..."
  "skill": {
    "name": "My Q&A chatbot"
  }
 "..."
```


## Skill with reference data

Skills can leverage reference data, such as a document, to provide additional context to the model.

```{literalinclude} ../examples/reference_variable.py
```
```shell
# print(response.llm_output)

longer-email@example.com
```

## Evaluator skill and minimal version of it

We can also create an evaluator skill. Evaluator skills return only floating point values between 0 and 1, based on how well the received output (of a skill) matches what the evaluator is described to look for.

```{literalinclude} ../examples/evaluator_skill.py
```
```json
// print(response.validation)

{
  "validator_results": [
    {
      "evaluator_name": "Cooking recipe evaluator",
      "evaluator_id": "...",
      "threshold": "0.1",
      "is_valid": "True",
      "result": "0.9",
      "status": "finished"
    }
  ],
  "is_valid": "True"}
```

The evaluator skill can be also created implicitly by supplying evaluator_name and a prompt:

```{literalinclude} ../examples/evaluator_skill_minimal.py
```
```json
// print(response.validation)

"validator_results": [
  {
    "evaluator_name": "Cooking recipe evaluator",
    "evaluator_id": "...",
    "threshold": "0.1",
    "is_valid": "True",
    "result": "0.8",
    "status": "finished"
  }
],
"is_valid": "True"}
```

## Adjust evaluator behavior

An evaluator can be calibrated to adjust its behavior

```{literalinclude} ../examples/calibration.py
```
```json
// print(test_result[0].result)

"score": "0.5",
"expected_score": "0.1",
```
```json
// print(test_result[0].result)

"score": "0.1",
"expected_score": "0.1",
```



## Use Retrieval Augmented Generation (RAG) evaluator

For RAG, there are special evaluators that can separately measure the different intermediate components of a RAG pipeline, in addition to the final output.

```{literalinclude} ../examples/run_rag.py
```
```json
// print(result.score)

"0.0"
```

## Use OpenAI client for chat completions

Evaluators and monitoring can be added to your existing codebase using OpenAI client. To do this, retrieve `base_url` from the Root Signals SDK Skill, and then use the normal `openai` API client with it. There are two ways to do it:

Without streaming, the API returns whole response to the call:

```{literalinclude} ../examples/chat_openai.py
```
```shell
# print(completion.choices[0].message.content)

The sky appears blue because of the way sunlight interacts ...
```
```shell
# print(completion.choices[0].message.content)

The sky appears blue because of the way sunlight interacts ...
```
```json
// print(log.validation_results)
[
  "evaluator_name": "Truthfulness"
  "result": "0.9"
  "is_valid": "true"
  "..."
]
```

Do note that only models specified as either `model` or
`fallback_models` to the created Skill are accepted by the API. Trying
to use other model names will result in an error.

When streaming (`stream=True`), the API response will be provided as a generator which will provide a set of chunks over time:chunks :

```{literalinclude} ../examples/chat_openai_2.py
```
```shell
# print(chunk.choices[0].delta.content)

The sky appears blue because of the way sunlight interacts ...
```

Do note that if validators are in use, it is not possible to stream the response as the response must be validated before returning it to the caller. In that case (and possibly for other reasons too), the platform will just return the final full response after validators are done evaluating it as a single chunk.

## Evaluate your LLM pipeline by grouping validators to a skill

We can group and track any LLM pipeline results using a skill.


```{literalinclude} ../examples/pipeline.py
```
```json
// print(response)

"validation":
  "validation_results": [
    "evaluator_name": "Clarity"
    "result": "0.5"
    "is_valid": "true"
    "..."
  ]
```

Alternatively, we can just execute the objective.

```{literalinclude} ../examples/objective.py
```
```json
// print(response)

"validation":
  "validation_results": [
    "evaluator_name": "Clarity"
    "result": "0.5"
    "is_valid": "true"
    "..."
  ]
```


## Add a model

Adding a model is as simple as specifying the model name and an endpoint. The model can be a local model or a model hosted on a cloud service.

```{literalinclude} ../examples/model.py
```


## Skill with a data loader

In this example, we add a data loader which loads the contents of a data loader variable called kimchi_ingredients from Wikipedia, and then uses that to populate the prompt.

```{literalinclude} ../examples/data_loader.py
```
```json
// print(response)

"llm_output":"Kimchi, a traditional Korean side dish, is renowned for
its unique taste and health benefits. Made from salted and fermented
vegetables, it uses seasonings such as gochugaru (Korean chili
powder), ... Here are a few recipes for you to try at
home:\n\n1. Traditional Napa Cabbage Kimchi:\n\nIngredients:..."
```
