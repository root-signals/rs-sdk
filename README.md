# root-sdk

<!-- the image cannot be within pypi, so we get it from the sdk website -->
<h1 align="center">
  <img style="vertical-align:middle" height="200" src="https://sdk.rootsignals.ai/en/latest/_images/root_signals+bounding_box.svg">
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
{::comment}examples/minimal.py{:/comment}
```python
from root import RootSignals

# Connect to the Root Signals API
client = RootSignals()

# Create a skill
skill = client.skills.create(
    "Find me good recipes for {{food_type}} food that are {{cuisine}}."
)

# Run it
response = skill.run({"food_type": "spicy", "cuisine": "Korean"})

print(response)

# llm_output="1. Kimchi Jjigae (Kimchi Stew): This spicy and flavorful
# stew is made with fermented kimchi, pork, tofu, and vegetables. ..."
# validation={'validator_results': [], 'is_valid': True}
# model='gpt-3.5-turbo' engine='gpt-3.5-turbo'
# execution_log_id='181eb95b-b972-4e96-8e30-ca7d3447d4fe'
# rendered_prompt='Find me good recipes for spicy food that are
# Korean.'

```

# Documentation

For more details, please see [the main SDK documentation](https://sdk.docs.rootsignals.ai).

# Miscellaneous notes

## Versioning policy

We follow [semantic versioning](https://semver.org); to
point, major versions are not guaranteed to be backwards compatible, minor
versions are, and patch versions only fix bugs.
