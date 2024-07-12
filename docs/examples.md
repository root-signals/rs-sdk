# SDK features using concrete examples #

These examples walk through some features of the platform in more detail.

## Minimal skill

Just like the quickstart example, but broken into multiple lines for readability. The APIs typically respond with Python objects that can be used to chain requests or alternatively reuse previous calls' results.

```{literalinclude} ../examples/minimal.py
```

## Simple skill

The simple skill example adds some more metadata to the skill. It specifies explicitly the model to use, the descriptive intent, and the input variables that are referred to in the prompt.

```{literalinclude} ../examples/simple.py
```

## Skill with a validator

In order to ensure the results of skill execution remain within acceptable guardrails, we can add a validator. In this example, the validator scores the results by relevance of the answer to the input prompt. Relevance result less than the threshold 0.9 will block the skill execution.

```{literalinclude} ../examples/validator.py
```

The validation results can be retrieved from the execution logs for analysis and audit.

```{literalinclude} ../examples/execution_logs.py
```

## Evaluator skill and minimal version of it

We can also create an evaluator skill. Evaluator skills return only floating point values between 0 and 1, based on how well the received output (of a skill) matches what the evaluator is described to look for.

```{literalinclude} ../examples/evaluator_skill.py
```

The evaluator skill can be also created implicitly by supplying evaluator_name and a prompt:

```{literalinclude} ../examples/evaluator_skill_minimal.py
```

## Adjust evaluator behavior

An evaluator can be calibrated to adjust its behavior

```{literalinclude} ../examples/calibration.py
```


## Use Retrieval Augmented Generation (RAG) evaluator

For RAG, there are special evaluators that can separately measure the different intermediate components of a RAG pipeline, in addition to the final output.

```{literalinclude} ../examples/run_rag.py
```

## Use OpenAI client for chat completions

Evaluators and monitoring can be added to your existing codebase using OpenAI client. To do this, retrieve `base_url` from the Root Signals SDK Skill, and then use the normal `openai` API client with it. There are two ways to do it:

Without streaming, the API returns whole response to the call:

```{literalinclude} ../examples/chat_openai.py
```

Do note that only models specified as either `model` or
`fallback_models` to the created Skill are accepted by the API. Trying
to use other model names will result in an error.

When streaming (`stream=True`), the API response will be provided as a generator which will provide a set of chunks over time:chunks :

```{literalinclude} ../examples/chat_openai_2.py
```

Do note that if validators are in use, it is not possible to stream the response as the response must be validated before returning it to the caller. In that case (and possibly for other reasons too), the platform will just return the final full response after validators are done evaluating it as a single chunk.

## Evaluate your LLM pipeline by grouping validators to a skill

We can group and track any LLM pipeline results using a skill.


```{literalinclude} ../examples/pipeline.py
```

Alternatively, we can just execute the objective.

```{literalinclude} ../examples/objective.py
```


## Add a model

Adding a model is as simple as specifying the model name and an endpoint. The model can be a local model or a model hosted on a cloud service.

```{literalinclude} ../examples/model.py
```


## Skill with a data loader

In this example, we add a data loader which loads the contents of a reference variable called kimchi_ingredients from Wikipedia, and then uses that to populate the prompt.

```{literalinclude} ../examples/data_loader.py
```
