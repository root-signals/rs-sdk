import pytest

from root.client import RootSignals


@pytest.mark.asyncio
async def test_throws_exception_when_sync_methods_used_with_async_client__fails():
    with pytest.raises(Exception) as e:
        aclient = RootSignals(api_key="fake", run_async=True)

        aclient.evaluators.get_by_name("Whoops, this is a sync method")
    assert str(e.value) == "This method is not available in asynchronous mode"
