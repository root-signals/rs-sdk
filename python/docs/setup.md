# Authentication and setup #

There are some other supported authentication and setup modes than those described in the quickstart.

## API key handling

The API key must be provided via one of the following methods - the code uses the first one that is found:

1. as an argument to RootSignals constructor (see below),
2. environment variable `ROOTSIGNALS_API_KEY` (see quickstart), or
3. .env file containing `ROOTSIGNALS_API_KEY=` (see below)

### Provide it in the code (highest priority)

In addition to the `ROOTSIGNALS_API_KEY` environment variable, you can also supply the API key directly from your code using either:

```
from root import RootSignals
client = RootSignals("my secret api key")
...
```

or

```
from root import RootSignals
client = RootSignals(api_key="my secret api key")
...
```

### .env file (lowest priority)

Current directory where the Python interpreter is being executed can be also used to find the `.env` file with `variable=value` definitions. In this case, if there is `ROOTSIGNALS_API_KEY=mysecretapikey` entry there, it is used.

## Local installation

In addition to the default `pip install` described in the quickstart, it is also possible to use the package from source. If you want to develop the SDK, it can be useful to make the package
locally installed:

```bash
pip install -e .
```

## Request timeout

Use the `_request_timeout` parameter to set the timeout for the API requests. The default is not set, which means that the requests will wait indefinitely. The value is in seconds.

