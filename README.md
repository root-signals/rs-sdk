<h1 align="center">
  <img width="600" alt="Root Signals logo" src="https://app.rootsignals.ai/images/root-signals-color.svg" loading="lazy">
</h1>

  <!-- This is commented so it is easier to sync with the docs/index.rst -->

<p align="center" class="large-text">
  <i><strong>Measurement & Control for LLM Automations</strong></i>
</p>

<p align="center">
    <a href="https://pypi.org/project/root-signals/">
      <img alt="Supported Python versions" src="https://img.shields.io/badge/Python-3.10%20to%203.13-yellow?style=for-the-badge&logo=python&logoColor=yellow">
    </a>
</p>

<p align="center">
  <a href="https://pypi.org/project/root-signals">
    <img src="https://img.shields.io/pypi/v/root-signals" alt="PyPI">
  </a>
  <img src="https://img.shields.io/pypi/dm/root-signals?color=orange" alt="Downloads">
  <a href="https://github.com/root-signals/rs-python-sdk/blob/main/LICENSE">
    <img src="https://img.shields.io/github/license/root-signals/rs-python-sdk.svg" alt="License">
  </a>
</p>

<p align="center">
  <a href="https://app.rootsignals.ai/register">
    <img src="https://img.shields.io/badge/Get_Started-2E6AFB?style=for-the-badge&logo=rocket&logoColor=white&scale=2" />
  </a>

  <a href="https://huggingface.co/root-signals">
    <img src="https://img.shields.io/badge/HuggingFace-FF9D00?style=for-the-badge&logo=huggingface&logoColor=white&scale=2" />
  </a>

  <a href="https://discord.gg/QbDAAmW9yz">
    <img src="https://img.shields.io/badge/Discord-5865F2?style=for-the-badge&logo=discord&logoColor=white&scale=2" />
  </a>

  <a href="https://sdk.rootsignals.ai/en/latest/">
    <img src="https://img.shields.io/badge/Documentation-E53935?style=for-the-badge&logo=readthedocs&logoColor=white&scale=2" />
  </a>

  <a href="https://app.rootsignals.ai/demo-user">
    <img src="https://img.shields.io/badge/Temporary_API_Key-15a20b?style=for-the-badge&logo=keycdn&logoColor=white&scale=2" />
  </a>
</p>


**Root Signals** streamlines the evaluation of your LLM and agentic pipelines. We provide a holistic approach to GenAI measurability & observability with **carefully-crafted ready-to-use evaluators** based on cutting-edge LLM research as well as a framework for systematically adding **your own custom evaluators**.

With Root Signals you can develop your LLM application reliably, deploy them in confidence, and ensure optimal performance with continuous monitoring.

## 📦 Install

```bash
pip install root-signals
```


## ⚡ Quickstart

</p>
    <a href="https://colab.research.google.com/drive/1ztDFIItKGEruDD2SOiixatm4klxpT6Of?usp=sharing">
        <img alt="Quickstart in Colab" src="https://colab.research.google.com/assets/colab-badge.svg">
    </a>
</p>



#### 🔑 Get Your API Key
- [Sign up & create a key](https://app.rootsignals.ai/settings/api-keys)
- Or [generate a temporary key](https://app.rootsignals.ai/demo-user)

**Setup Option 1: Environment Variable**
```bash
export ROOTSIGNALS_API_KEY=your-Root-API-key
```

**Setup Option 2: `.env` File**
```bash
echo ROOTSIGNALS_API_KEY=your-Root-API-key >> .env
```

### *Root* Evaluators
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


## 📖 Documentation

| Resource | Link |
|----------|------|
| 🐍 Python SDK | [View Documentation](https://sdk.rootsignals.ai) |
| 📘 Product Docs | [View Documentation](https://docs.rootsignals.ai) |


## 🌍 Community

💬 Join our [Discord Server](https://discord.gg/EhazTQsFnj)! It's a great place to ask questions, get help, and discuss ideas.

