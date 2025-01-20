<!-- the image cannot be within pypi, so we get it from the sdk website -->
<h1 align="center">
  <img width="600" alt="Root Signals logo" src="https://app.rootsignals.ai/images/root-signals-color.svg" loading="lazy">
</h1>

  <!-- This is commented so it is easier to sync with the docs/index.rst -->

<p align="center">
  <i>Control and Measurement for LLM automations</i>
</p>


Root Signals SDK streamlines the evaluation of your LLM pipelines, to yield insights about their effectiveness. While many tools exist for building the pipelines themselves, quantifying their performance can be challenging.

Root Signals addresses this gap with carefully crafted universal evaluators based on cutting edge LLM research, as well as a framework for systematically adding your own.

Easily integrate with your CI/CD process for continuous monitoring to ensure the performance stays within acceptable limits.

## Install

```bash
pip install root-signals
```

## Quickstart

Before you begin, you'll need to set up your API key. You can either:
1. Set it as an environment variable `ROOTSIGNALS_API_KEY`
2. Add it to a local `.env` file

Get your API key from:
- https://app.rootsignals.ai/settings/api-keys
- Or [create a temporary key](https://app.rootsignals.ai/demo-user)

Example setup:

```bash
# Option 1: Environment variable
export ROOTSIGNALS_API_KEY=your-Root-API-key

# Option 2: .env file
echo ROOTSIGNALS_API_KEY=your-Root-API-key >> .env
```

### Run a Root evaluator
```python
from root import RootSignals

# Connect to the Root Signals API
client = RootSignals()

# Run a politeness evaluator
response = client.evaluators.Politeness(
    response="You can find the instructions from our Careers page."
)
print(response)
# {score=0.7, justification='The response is st...', execution_log_id=...}
```

Check the full list of Root evaluators from the [Root evaluators documentation](https://docs.rootsignals.ai/quick-start/usage/evaluators#list-of-evaluators-maintained-by-root-signals). You can also [add your own evaluators](https://sdk.rootsignals.ai/en/latest/examples.html#custom-evaluator).

# Documentation

For more details, please see [the main SDK documentation](https://sdk.docs.rootsignals.ai).

# Miscellaneous notes

## Versioning policy

We follow [semantic versioning](https://semver.org); to
point, major versions are not guaranteed to be backwards compatible, minor
versions are, and patch versions only fix bugs.
