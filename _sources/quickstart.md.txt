# Quickstart

**1.** Install Scorable Python SDK [from PyPI](https://pypi.org/project/scorable/):

```bash
pip install scorable
```

**2.** Create your API key from [Scorable Application](https://scorable.ai/settings/api-keys) and add it as an environment variable:

```bash
export SCORABLE_API_KEY=SomethingReallySecret
```

**3.** Start evaluating with Scorable Evaluators:

```python
from scorable import Scorable

client = Scorable()
client.evaluators.Politeness(
    response="You can find the instructions from our Careers page."
)  # {score=0.7, justification='The response is st...', execution_log_id=...}
```
