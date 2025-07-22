from unittest.mock import AsyncMock, patch

import pytest

from root.client import RootSignals


@pytest.mark.asyncio
@patch("root.judges.JudgesApi")
async def test_run_judge_by_name(mock_judges_api):
    client = RootSignals(api_key="fake")
    instance = mock_judges_api.return_value
    instance.judges_execute_by_name_create.return_value = "mock_success"

    result = client.judges.run_by_name("test_judge", response="test_response")

    assert result == "mock_success"
    mock_judges_api.assert_called_once()
    instance.judges_execute_by_name_create.assert_called_once()
    call_args = instance.judges_execute_by_name_create.call_args
    assert call_args.kwargs["name"] == "test_judge"
    assert call_args.kwargs["judge_execution_request"].response == "test_response"


@pytest.mark.asyncio
@patch("root.judges.AJudgesApi")
async def test_arun_judge_by_name(mock_ajudges_api):
    client = RootSignals(api_key="fake", run_async=True)
    instance = mock_ajudges_api.return_value
    instance.judges_execute_by_name_create = AsyncMock(return_value="mock_success")

    result = await client.judges.arun_by_name("test_judge", response="test_response")

    assert result == "mock_success"
    mock_ajudges_api.assert_called_once()
    instance.judges_execute_by_name_create.assert_called_once()
    call_args = instance.judges_execute_by_name_create.call_args
    assert call_args.kwargs["name"] == "test_judge"
    assert call_args.kwargs["judge_execution_request"].response == "test_response"
