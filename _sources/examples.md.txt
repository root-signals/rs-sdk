# SDK features using concrete examples

These examples walk through some features of the platform in more detail.

## Root Signals evaluators

Root Signals provides [over 30 ready-made](https://docs.rootsignals.ai/quick-start/usage/evaluators#list-of-evaluators-maintained-by-root-signals) evaluators that can be used to validate any textual content.


```{literalinclude} ../examples/preset_evaluator.py
```
```shell
# Score: 0.1 / 1.0

# Clarity:
# The response is very brief and lacks detail. It simply directs the reader to another source without providing any specific information.
# The phrase "instructions from our Careers page" is vague and does not specify...
```


## Custom evaluator

We can also create a custom evaluator. Evaluators return only floating point values between 0 and 1, based on how well the received text matches what the evaluator is described to look for.

```{literalinclude} ../examples/custom_evaluator.py
```
```shell
# Score: 0.3

# METRIC: Technical Accuracy and Appropriateness
# 
# 1.  Relevance: The initial response is generic and lacks...
```


## Adjust evaluator behavior

An evaluator behaviour can be adjusted by providing demonstrations.

```{literalinclude} ../examples/calibration.py
```


## Retrieval Augmented Generation (RAG) evaluation

For RAG, there are special evaluators that can separately measure the different intermediate components of a RAG pipeline, in addition to the final output. 

```{literalinclude} ../examples/run_rag.py
```


## Monitoring LLM pipelines with tags

Evaluator runs can be tagged with free-form tags.

```{literalinclude} ../examples/run_tagging.py
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

## Evaluate your LLM pipeline by grouping validators to a *Objective*

We can group and track any LLM pipeline results using an *Objective*.

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

## Simple Skill

*Skills* are measurable units of automations powered by LLMs. The APIs typically respond with Python objects that can be used to chain requests or alternatively reuse previous calls' results. It specifies explicitly the model to use, the descriptive intent, and the input variables that are referred to in the prompt.

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