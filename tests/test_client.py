import pytest

from root.client import RootSignals
from root.skills import CalibrateBatchParameters


def test_throws_exception_when_sync_methods_used_with_async_client__fails():
    with pytest.raises(Exception) as e:
        aclient = RootSignals(api_key="fake", run_async=True)

        params = [
            CalibrateBatchParameters(
                name="With gpt-4",
                prompt="What is the weather today?",
                model="gpt-4",
                pii_filter=False,
                reference_variables=None,
                input_variables=None,
                data_loaders=None,
            ),
            CalibrateBatchParameters(
                name="With gpt-4-turbo",
                prompt="What is the weather today?",
                model="gpt-4-turbo",
                pii_filter=False,
                reference_variables=None,
                input_variables=None,
                data_loaders=None,
            ),
        ]

        aclient.evaluators.calibrate_batch(
            evaluator_definitions=params, test_data=[["0.4", "LLM output"], ["0.6", "LLM output 2"]]
        )
    assert str(e.value) == "This method is not available in asynchronous mode"
