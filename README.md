<!-- the image cannot be within pypi, so we get it from the sdk website -->
<h1 align="center">
  <img style="vertical-align:middle" height="200" src="https://cdn.prod.website-files.com/660f4bb4fb990316f902c545/66d83dd0ca040ea331127908_Logo%20-%20Blue%20-%20Root%20Signals%20(1).png">
</h1>

  <!-- This is commented so it is easier to sync with the docs/index.rst -->

  <p align="center">
    <i>Control and Measurement for LLM automations</i>
  </p>

  <p align="center">
      <a href="https://github.com/root-signals/root-python-sdk/releases">
          <img alt="GitHub release"   src="https://img.shields.io/github/release/root-signals/root-python-sdk.svg">
      </a>
      <a href="https://www.python.org/">
              <img alt="Build"   src="https://img.shields.io/badge/Made%20with-Python-1f425f.svg?color=purple">
      </a>
      <a   href="https://github.com/root-signals/root-python-sdk/blob/master/LICENSE">
          <img alt="License"   src="https://img.shields.io/github/license/rootsignals/roots.svg?color=green">
      </a>
  </p>


Root Signals SDK streamlines the evaluation of your LLM pipelines, to yield insights about their effectiveness. While many tools exist for building the pipelines themselves, quantifying their performance can be challenging.

Root Signals addresses this gap with carefully crafted universal evaluators based on cutting edge LLM research, as well as a framework for systematically adding your own.

Easily integrate with your CI/CD process for continuous monitoring to ensure the performance stays within acceptable limits.

## Install

### From pypi

The preferrable way of installing the SDK is from [PyPI](https://pypi.org). With pip:

```bash
pip install root-signals
```

## Quickstart

Please set your API key to environment variable `ROOTSIGNALS_API_KEY`, or to local .env file.

Retrieve an API key from https://app.rootsignals.ai/settings/api-keys

For example:

```bash
export ROOTSIGNALS_API_KEY=your-Root-API-key
```

or, if you prefer using .env file:

```bash
echo ROOTSIGNALS_API_KEY=your-Root-API-key >> .env
```

### Minimal skill
```python
from root import RootSignals

# Connect to the Root Signals API
client = RootSignals()

# Create a skill
skill = client.skills.create(
    """
    Classify this text into one of the following: {{categories}}
    Text: {{text}}
    """
)

# Execute it
response = skill.run(
    {
        "text": "The expectation for rate cuts has been steadily declining.",
        "categories": "Finance, Sports, Politics",
    }
)

print(response)

# "llm_output": "Finance",
# "validation": Validation(is_valid=True, validator_results=[]),
# "model": "gpt-4o",
# "execution_log_id": "9b3c713d-7bdc-4f7d-a85c-ed7d92ff4a56",
# "rendered_prompt": "Classify this text into ...",
# "cost": 5.6e-05,

```

# Documentation

For more details, please see [the main SDK documentation](https://sdk.docs.rootsignals.ai).

# Miscellaneous notes

## Versioning policy

We follow [semantic versioning](https://semver.org); to
point, major versions are not guaranteed to be backwards compatible, minor
versions are, and patch versions only fix bugs.
