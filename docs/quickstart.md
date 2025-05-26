# Quickstart

**1.** Install Root Signals Python SDK [from PyPI](https://pypi.org/project/root-signals/):

```bash
pip install root-signals
```

**2.** Create your API key from [Root Signals Application](https://app.rootsignals.ai/settings/api-keys) and add it as an environment variable:

```bash
export ROOTSIGNALS_API_KEY=SomethingReallySecret
```

**3.** Start evaluating with Root Signals Evaluators:

```python
from root import RootSignals

client = RootSignals()
client.evaluators.Politeness(
    response="You can find the instructions from our Careers page."
)  # {score=0.7, justification='The response is st...', execution_log_id=...}
```
