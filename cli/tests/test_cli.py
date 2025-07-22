import json
import pytest
from unittest.mock import Mock, patch
from click.testing import CliRunner
from cli import cli, _request, Judge, JudgeListResponse, EvaluatorReference


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def mock_api_key():
    with patch.dict("os.environ", {"ROOTSIGNALS_API_KEY": "test-api-key"}):
        yield


@pytest.fixture
def sample_judge():
    return Judge(
        id="judge-123",
        name="Test Judge",
        intent="Test intent",
        created_at="2024-01-01T12:00:00Z",
        status="active",
        evaluator_references=[EvaluatorReference(id="eval-123")],
    )


@pytest.fixture
def sample_judge_list():
    judges = [
        Judge(
            id="judge-123",
            name="Test Judge 1",
            intent="Test intent 1",
            created_at="2024-01-01T12:00:00Z",
            status="active",
        ),
        Judge(
            id="judge-456",
            name="Test Judge 2",
            intent="Test intent 2",
            created_at="2024-01-02T12:00:00Z",
            status="inactive",
        ),
    ]
    return JudgeListResponse(results=judges, next=None)


class TestJudgeList:
    def test_list_judges_success(self, runner, mock_api_key, sample_judge_list):
        with patch("cli._request", return_value=sample_judge_list):
            result = runner.invoke(cli, ["judge", "list"])
            assert result.exit_code == 0
            assert "Test Judge 1" in result.output
            assert "Test Judge 2" in result.output

    def test_list_judges_with_filters(self, runner, mock_api_key, sample_judge_list):
        with patch("cli._request", return_value=sample_judge_list) as mock_req:
            result = runner.invoke(
                cli,
                [
                    "judge",
                    "list",
                    "--page-size",
                    "10",
                    "--search",
                    "test",
                    "--name",
                    "Test Judge",
                    "--is-preset",
                ],
            )
            assert result.exit_code == 0
            mock_req.assert_called_once()

    def test_list_judges_empty(self, runner, mock_api_key):
        empty_list = JudgeListResponse(results=[], next=None)
        with patch("cli._request", return_value=empty_list):
            result = runner.invoke(cli, ["judge", "list"])
            assert result.exit_code == 0
            assert "No judges found" in result.output

    def test_list_judges_with_pagination(self, runner, mock_api_key, sample_judge_list):
        sample_judge_list.next = "cursor=next_page_token"
        with patch("cli._request", return_value=sample_judge_list):
            result = runner.invoke(cli, ["judge", "list"])
            assert result.exit_code == 0
            assert "Next page available" in result.output


class TestJudgeGet:
    def test_get_judge_success(self, runner, mock_api_key, sample_judge):
        with patch("cli._request", return_value=sample_judge):
            result = runner.invoke(cli, ["judge", "get", "judge-123"])
            assert result.exit_code == 0
            assert "Test Judge" in result.output

    def test_get_judge_not_found(self, runner, mock_api_key):
        with patch("cli._request", return_value=None):
            result = runner.invoke(cli, ["judge", "get", "nonexistent"])
            assert result.exit_code == 0


class TestJudgeCreate:
    def test_create_judge_basic(self, runner, mock_api_key, sample_judge):
        with patch("cli._request", return_value=sample_judge):
            result = runner.invoke(
                cli,
                ["judge", "create", "--name", "New Judge", "--intent", "New intent"],
            )
            assert result.exit_code == 0
            assert "Judge created successfully" in result.output

    def test_create_judge_with_stage(self, runner, mock_api_key, sample_judge):
        with patch("cli._request", return_value=sample_judge) as mock_req:
            result = runner.invoke(
                cli,
                [
                    "judge",
                    "create",
                    "--name",
                    "New Judge",
                    "--intent",
                    "New intent",
                    "--stage",
                    "production",
                ],
            )
            assert result.exit_code == 0
            mock_req.assert_called_once()

    def test_create_judge_with_evaluator_references(
        self, runner, mock_api_key, sample_judge
    ):
        with patch("cli._request", return_value=sample_judge) as mock_req:
            result = runner.invoke(
                cli,
                [
                    "judge",
                    "create",
                    "--name",
                    "New Judge",
                    "--intent",
                    "New intent",
                    "--evaluator-references",
                    '[{"id": "eval-123"}]',
                ],
            )
            assert result.exit_code == 0
            mock_req.assert_called_once()

    def test_create_judge_invalid_json(self, runner, mock_api_key):
        result = runner.invoke(
            cli,
            [
                "judge",
                "create",
                "--name",
                "New Judge",
                "--intent",
                "New intent",
                "--evaluator-references",
                "invalid-json",
            ],
        )
        assert result.exit_code == 0
        assert "Invalid JSON format" in result.output

    def test_create_judge_missing_required_args(self, runner, mock_api_key):
        result = runner.invoke(cli, ["judge", "create", "--name", "Test"])
        assert result.exit_code == 2

        result = runner.invoke(cli, ["judge", "create", "--intent", "Test"])
        assert result.exit_code == 2


class TestJudgeUpdate:
    def test_update_judge_name(self, runner, mock_api_key, sample_judge):
        with patch("cli._request", return_value=sample_judge) as mock_req:
            result = runner.invoke(
                cli, ["judge", "update", "judge-123", "--name", "Updated Judge"]
            )
            assert result.exit_code == 0
            assert "Judge judge-123 updated successfully" in result.output
            mock_req.assert_called_once()

    def test_update_judge_stage(self, runner, mock_api_key, sample_judge):
        with patch("cli._request", return_value=sample_judge) as mock_req:
            result = runner.invoke(
                cli, ["judge", "update", "judge-123", "--stage", "production"]
            )
            assert result.exit_code == 0
            mock_req.assert_called_once()

    def test_update_judge_evaluator_references(
        self, runner, mock_api_key, sample_judge
    ):
        with patch("cli._request", return_value=sample_judge) as mock_req:
            result = runner.invoke(
                cli,
                [
                    "judge",
                    "update",
                    "judge-123",
                    "--evaluator-references",
                    '[{"id": "eval-456"}]',
                ],
            )
            assert result.exit_code == 0
            mock_req.assert_called_once()

    def test_update_judge_clear_evaluator_references(
        self, runner, mock_api_key, sample_judge
    ):
        with patch("cli._request", return_value=sample_judge) as mock_req:
            result = runner.invoke(
                cli, ["judge", "update", "judge-123", "--evaluator-references", "[]"]
            )
            assert result.exit_code == 0
            mock_req.assert_called_once()

    def test_update_judge_invalid_json(self, runner, mock_api_key):
        result = runner.invoke(
            cli,
            ["judge", "update", "judge-123", "--evaluator-references", "invalid-json"],
        )
        assert result.exit_code == 0
        assert "Invalid JSON format" in result.output

    def test_update_judge_no_params(self, runner, mock_api_key):
        result = runner.invoke(cli, ["judge", "update", "judge-123"])
        assert result.exit_code == 0
        assert "No update parameters provided" in result.output


class TestJudgeDelete:
    def test_delete_judge_success(self, runner, mock_api_key):
        with patch("cli._request", return_value=None):
            result = runner.invoke(cli, ["judge", "delete", "judge-123"], input="y\n")
            assert result.exit_code == 0
            assert "Judge judge-123 deleted successfully" in result.output

    def test_delete_judge_with_yes_flag(self, runner, mock_api_key):
        with patch("cli._request", return_value=None):
            result = runner.invoke(cli, ["judge", "delete", "judge-123", "--yes"])
            assert result.exit_code == 0
            assert "Judge judge-123 deleted successfully" in result.output

    def test_delete_judge_abort(self, runner, mock_api_key):
        result = runner.invoke(cli, ["judge", "delete", "judge-123"], input="n\n")
        assert result.exit_code == 1


class TestJudgeExecute:
    def test_execute_judge_with_request(self, runner, mock_api_key):
        mock_response = {"result": "success", "score": 0.95}
        with patch("cli._request", return_value=mock_response):
            result = runner.invoke(
                cli, ["judge", "execute", "judge-123", "--request", "Test request"]
            )
            assert result.exit_code == 0
            assert "Judge execution successful" in result.output

    def test_execute_judge_with_response(self, runner, mock_api_key):
        mock_response = {"result": "success", "score": 0.85}
        with patch("cli._request", return_value=mock_response):
            result = runner.invoke(
                cli, ["judge", "execute", "judge-123", "--response", "Test response"]
            )
            assert result.exit_code == 0
            assert "Judge execution successful" in result.output

    def test_execute_judge_with_all_params(self, runner, mock_api_key):
        mock_response = {"result": "success", "score": 0.90}
        with patch("cli._request", return_value=mock_response) as mock_req:
            result = runner.invoke(
                cli,
                [
                    "judge",
                    "execute",
                    "judge-123",
                    "--request",
                    "Test request",
                    "--response",
                    "Test response",
                    "--contexts",
                    '["context1", "context2"]',
                    "--functions",
                    '[{"name": "test_func"}]',
                    "--expected-output",
                    "Expected output",
                    "--tag",
                    "tag1",
                    "--tag",
                    "tag2",
                ],
            )
            assert result.exit_code == 0
            assert "Judge execution successful" in result.output
            mock_req.assert_called_once()

    def test_execute_judge_no_request_or_response(self, runner, mock_api_key):
        result = runner.invoke(cli, ["judge", "execute", "judge-123"])
        assert result.exit_code == 0
        assert "Either --request or --response must be provided" in result.output

    def test_execute_judge_invalid_contexts_json(self, runner, mock_api_key):
        result = runner.invoke(
            cli,
            [
                "judge",
                "execute",
                "judge-123",
                "--request",
                "Test request",
                "--contexts",
                "invalid-json",
            ],
        )
        assert result.exit_code == 0
        assert "Invalid JSON for --contexts" in result.output

    def test_execute_judge_invalid_functions_json(self, runner, mock_api_key):
        result = runner.invoke(
            cli,
            [
                "judge",
                "execute",
                "judge-123",
                "--request",
                "Test request",
                "--functions",
                "invalid-json",
            ],
        )
        assert result.exit_code == 0
        assert "Invalid JSON for --functions" in result.output


class TestJudgeExecuteByName:
    def test_execute_judge_by_name_success(self, runner, mock_api_key):
        mock_response = {"result": "success", "score": 0.88}
        with patch("cli._request", return_value=mock_response):
            result = runner.invoke(
                cli,
                ["judge", "execute-by-name", "Test Judge", "--request", "Test request"],
            )
            assert result.exit_code == 0
            assert "Judge execution by name successful" in result.output

    def test_execute_judge_by_name_no_request_or_response(self, runner, mock_api_key):
        result = runner.invoke(cli, ["judge", "execute-by-name", "Test Judge"])
        assert result.exit_code == 0
        assert "Either --request or --response must be provided" in result.output


class TestJudgeDuplicate:
    def test_duplicate_judge_success(self, runner, mock_api_key, sample_judge):
        duplicated_judge = sample_judge.model_copy()
        duplicated_judge.id = "judge-456"
        duplicated_judge.name = "Test Judge (Copy)"

        with patch("cli._request", return_value=duplicated_judge):
            result = runner.invoke(cli, ["judge", "duplicate", "judge-123"])
            assert result.exit_code == 0
            assert "Judge judge-123 duplicated successfully" in result.output


class TestApiRequest:
    def test_request_missing_api_key(self, runner):
        with patch.dict("os.environ", {}, clear=True):
            result = runner.invoke(cli, ["judge", "list"])
            assert result.exit_code == 1
            assert "ROOTSIGNALS_API_KEY environment variable not set" in result.output

    @patch("cli.session.request")
    @patch("cli.API_KEY", "test-key")
    def test_request_timeout(self, mock_request):
        import requests

        mock_request.side_effect = requests.exceptions.RequestException("Timeout")
        result = _request("GET", "judges")
        assert result is None

    @patch("cli.session.request")
    @patch("cli.API_KEY", "test-key")
    def test_request_http_error(self, mock_request):
        import requests

        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.json.return_value = {"error": "Not found"}
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
            response=mock_response
        )
        mock_response.request = Mock()
        mock_response.request.method = "GET"
        mock_response.request.url = "http://test.com"
        mock_request.return_value = mock_response

        result = _request("GET", "judges/nonexistent")
        assert result is None

    @patch("cli.session.request")
    @patch("cli.API_KEY", "test-key")
    def test_request_no_content_response(self, mock_request):
        mock_response = Mock()
        mock_response.status_code = 204
        mock_response.raise_for_status.return_value = None
        mock_request.return_value = mock_response

        result = _request("DELETE", "judges/123")
        assert result is None

    @patch("cli.session.request")
    @patch("cli.API_KEY", "test-key")
    def test_request_invalid_json(self, mock_request):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.raise_for_status.return_value = None
        mock_response.json.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)
        mock_request.return_value = mock_response

        result = _request("GET", "judges")
        assert result is None


class TestHelperFunctions:
    def test_print_functions(self, capsys):
        from cli import print_error, print_success, print_info, print_warning

        print_error("Test error")
        captured = capsys.readouterr()
        assert "Error:" in captured.out

        print_success("Test success")
        captured = capsys.readouterr()
        assert "Success:" in captured.out

        print_info("Test info")
        captured = capsys.readouterr()
        assert "Info:" in captured.out

        print_warning("Test warning")
        captured = capsys.readouterr()
        assert "Warning:" in captured.out
