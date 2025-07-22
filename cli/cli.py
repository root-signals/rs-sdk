#!/usr/bin/env -S uv run --quiet --script
# /// script
# dependencies = [
#   "click",
#   "requests",
#   "pydantic",
#   "rich"
# ]
# ///

import json
import os
import sys
from typing import List, Optional, Union

import click
import requests
from pydantic import BaseModel
from rich.console import Console
from rich.syntax import Syntax
from rich.table import Table

console = Console()


# --- Pydantic Models for API Responses ---


class EvaluatorReference(BaseModel):
    """Model for evaluator reference objects."""

    id: str


class Judge(BaseModel):
    """Model for individual judge response."""

    id: str
    name: str
    intent: str
    created_at: str
    status: Optional[str] = None
    stage: Optional[str] = None
    evaluator_references: Optional[List[EvaluatorReference]] = None


class JudgeListResponse(BaseModel):
    """Model for paginated judge list response."""

    results: List[Judge]
    next: Optional[str] = None


class JudgeExecutionResponse(BaseModel):
    """Model for judge execution response."""

    # Using a flexible model since execution responses can vary significantly
    model_config = {"extra": "allow"}


class ApiResponse(BaseModel):
    """Generic API response model that allows any additional fields."""

    model_config = {"extra": "allow"}


# --- Helper Functions ---


def print_json(data):
    console.print(
        Syntax(json.dumps(data, indent=2), "json", theme="native", line_numbers=False)
    )


def print_message(msg, style=""):
    console.print(msg, style=style)


def print_error(msg):
    console.print(f"[bold red]Error:[/bold red] {msg}")


def print_success(msg):
    console.print(f"[bold green]Success:[/bold green] {msg}")


def print_info(msg):
    console.print(f"[bold blue]Info:[/bold blue] {msg}")


def print_warning(msg):
    console.print(f"[bold yellow]Warning:[/bold yellow] {msg}")


API_KEY = os.getenv("ROOTSIGNALS_API_KEY")
BASE_URL = "https://api.app.rootsignals.ai"

session = requests.Session()

# --- API Helper Functions ---


def _request(  # noqa: C901
    method: str,
    endpoint_segment: str,
    data: Optional[dict] = None,
    params: Optional[dict] = None,
    response_model: Optional[type[BaseModel]] = None,
) -> Union[BaseModel, str, None]:
    """A centralized function to handle all API requests with typed responses."""
    # Ensure the session is configured before the first request
    if not session.headers.get("Authorization"):
        if not API_KEY:
            import sys

            print_error("ROOTSIGNALS_API_KEY environment variable not set.")
            print_info(
                "Please set it and try again. E.g., export ROOTSIGNALS_API_KEY='your_key'"
            )
            sys.exit(1)  # Exit if API key is not configured
        session.headers.update(
            {
                "Authorization": f"Api-Key {API_KEY}",
                "Content-Type": "application/json",
                "Accept": "application/json",
                "User-Agent": "root-signals-cli/1.0",
            }
        )

    if not endpoint_segment.endswith("/"):
        endpoint_segment += "/"

    url = f"{BASE_URL}/{endpoint_segment}"

    try:
        response = session.request(method, url, params, json=data, timeout=60)
        response.raise_for_status()
        if response.status_code == 204:  # No Content
            return None

        # Parse JSON response
        json_data = response.json()

        try:
            # If a specific response model is provided, use it
            if response_model:
                return response_model.model_validate(json_data)

            # Auto-detect response type based on endpoint and data structure
            if endpoint_segment.strip("/") == "judges" and method == "GET":
                return JudgeListResponse.model_validate(json_data)
            elif (
                endpoint_segment.startswith("judges/")
                and endpoint_segment.count("/") == 2
                and method == "GET"
            ):
                return Judge.model_validate(json_data)
            elif "/execute/" in endpoint_segment and method == "POST":
                return JudgeExecutionResponse.model_validate(json_data)
            elif (
                endpoint_segment.startswith("judges/") and method in ["POST", "PATCH"]
            ) or endpoint_segment.endswith("/duplicate"):
                return Judge.model_validate(json_data)
            else:
                # Generic response for other endpoints
                return ApiResponse.model_validate(json_data)
        except Exception as validation_error:
            print_warning(
                f"Failed to validate response with Pydantic model: {validation_error}"
            )
            print_info("Returning raw JSON data as fallback.")
            return json_data

    except requests.exceptions.HTTPError as e:
        print_error(
            f"API Error: {e.response.status_code} for {e.request.method} {e.request.url}"
        )
        try:
            print_json(e.response.json())
        except json.JSONDecodeError:
            print_error(f"Response content: {e.response.text}")
        return None
    except requests.exceptions.RequestException as e:
        print_error(f"Request failed: {e}")
        return None
    except json.JSONDecodeError:
        print_error(f"Failed to decode JSON response from API for {url}.")
        return None


# --- Core API Logic Functions ---
# These functions contain the primary logic and are called by the click commands.


def _list_judges(
    page_size, cursor, search, name, ordering, is_preset, is_public, show_global
):
    """Lists judges based on provided query parameters."""
    params = {
        "page_size": page_size,
        "cursor": cursor,
        "search": search,
        "name": name,
        "ordering": ordering,
        "is_preset": is_preset,
        "is_public": is_public,
        "show_global": show_global,
    }
    # Filter out None values so they aren't sent as query params
    actual_params = {k: v for k, v in params.items() if v is not None}

    print_info(f"Fetching judges with params: {actual_params}...")
    response_data = _request("GET", "judges", params=actual_params)

    if isinstance(response_data, JudgeListResponse):
        if not response_data.results:
            print_message("No judges found.")
            return

        table = Table(title="Judges")
        table.add_column("ID", style="cyan", no_wrap=True)
        table.add_column("Name", style="magenta")
        table.add_column("Intent", style="green", overflow="fold")
        table.add_column("Created At", style="blue")
        table.add_column("Status", style="yellow")

        for judge in response_data.results:
            table.add_row(
                judge.id, judge.name, judge.intent, judge.created_at, judge.status or ""
            )
        console.print(table)

        if response_data.next:
            print_info(
                f'Next page available. Use --cursor "{response_data.next.split("cursor=")[-1]}"'
            )
    elif response_data:
        print_json(
            response_data.model_dump()
            if isinstance(response_data, BaseModel)
            else response_data
        )


def _get_judge(judge_id):
    """Gets a specific judge by ID."""
    print_info(f"Fetching judge with ID: {judge_id}...")
    judge = _request("GET", f"judges/{judge_id}")
    if isinstance(judge, Judge):
        print_success(f"Judge '{judge.name}' details:")
        print_json(judge.model_dump())
    elif judge:
        print_json(judge.model_dump() if isinstance(judge, BaseModel) else judge)


def _create_judge(name, intent, stage, evaluator_references_json):
    """Creates a new judge."""
    payload = {"name": name, "intent": intent}
    if stage:
        payload["stage"] = stage
    if evaluator_references_json:
        try:
            payload["evaluator_references"] = json.loads(evaluator_references_json)
        except json.JSONDecodeError:
            print_error("Invalid JSON format for --evaluator-references.")
            return

    print_info("Attempting to create judge with payload:")
    print_json(payload)
    new_judge = _request("POST", "judges", data=payload)
    if isinstance(new_judge, Judge):
        print_success("Judge created successfully!")
        print_json(new_judge.model_dump())
    elif new_judge:
        print_json(
            new_judge.model_dump() if isinstance(new_judge, BaseModel) else new_judge
        )


def _update_judge(judge_id, name, stage, evaluator_references_json):
    """Updates an existing judge."""
    payload = {}
    if name is not None:
        payload["name"] = name
    if stage is not None:
        payload["stage"] = stage
    if evaluator_references_json is not None:
        try:
            # An empty list `[]` clears the references.
            payload["evaluator_references"] = json.loads(evaluator_references_json)
        except json.JSONDecodeError:
            print_error("Invalid JSON format for --evaluator-references.")
            return

    if not payload:
        print_info("No update parameters provided. Aborting.")
        return

    print_info(f"Attempting to update judge {judge_id} with PATCH payload:")
    print_json(payload)
    updated_judge = _request("PATCH", f"judges/{judge_id}", data=payload)
    if isinstance(updated_judge, Judge):
        print_success(f"Judge {judge_id} updated successfully!")
        print_json(updated_judge.model_dump())
    elif updated_judge:
        print_json(
            updated_judge.model_dump()
            if isinstance(updated_judge, BaseModel)
            else updated_judge
        )


def _delete_judge(judge_id):
    """Deletes a judge by ID."""
    print_info(f"Deleting judge {judge_id}...")
    response = _request("DELETE", f"judges/{judge_id}")
    if response is None:
        print_success(f"Judge {judge_id} deleted successfully.")


def _execute_judge(
    judge_id, request, response, contexts_json, functions_json, expected_output, tags
):  # noqa: C901
    """Executes a judge."""
    if not response and not sys.stdin.isatty():
        response = sys.stdin.read().strip()

    if not request and not response:
        print_error("Either --request or --response must be provided.")
        return

    payload = {}
    if request:
        payload["request"] = request
    if response:
        payload["response"] = response
    if expected_output:
        payload["expected_output"] = expected_output
    if tags:
        payload["tags"] = tags

    if contexts_json:
        try:
            payload["contexts"] = json.loads(contexts_json)
        except json.JSONDecodeError:
            print_error("Invalid JSON for --contexts. Skipping.")
            return

    if functions_json:
        try:
            payload["functions"] = json.loads(functions_json)
        except json.JSONDecodeError:
            print_error("Invalid JSON for --functions. Skipping.")
            return

    print_info(f"Attempting to execute judge {judge_id} with payload:")
    print_json(payload)
    result = _request("POST", f"judges/{judge_id}/execute", data=payload)
    if result:
        print_success("Judge execution successful!")
        print_json(result.model_dump() if isinstance(result, BaseModel) else result)


def _execute_judge_by_name(
    judge_name, request, response, contexts_json, functions_json, expected_output, tags
):  # noqa: C901
    """Executes a judge by name."""
    if not response and not sys.stdin.isatty():
        response = sys.stdin.read().strip()

    if not request and not response:
        print_error("Either --request or --response must be provided.")
        return

    payload = {}
    if request:
        payload["request"] = request
    if response:
        payload["response"] = response
    if expected_output:
        payload["expected_output"] = expected_output
    if tags:
        payload["tags"] = tags

    if contexts_json:
        try:
            payload["contexts"] = json.loads(contexts_json)
        except json.JSONDecodeError:
            print_error("Invalid JSON for --contexts. Skipping.")
            return

    if functions_json:
        try:
            payload["functions"] = json.loads(functions_json)
        except json.JSONDecodeError:
            print_error("Invalid JSON for --functions. Skipping.")
            return

    print_info(f"Attempting to execute judge '{judge_name}' with payload:")
    print_json(payload)
    result = _request(
        "POST", "judges/execute/by-name", data=payload, params={"name": judge_name}
    )
    if result:
        print_success("Judge execution by name successful!")
        print_json(result.model_dump() if isinstance(result, BaseModel) else result)


def _duplicate_judge(judge_id):
    """Duplicates an existing judge."""
    print_info(f"Duplicating judge ID: {judge_id}...")
    duplicated_judge = _request("POST", f"judges/{judge_id}/duplicate")
    if isinstance(duplicated_judge, Judge):
        print_success(f"Judge {judge_id} duplicated successfully!")
        print_json(duplicated_judge.model_dump())
    elif duplicated_judge:
        print_json(
            duplicated_judge.model_dump()
            if isinstance(duplicated_judge, BaseModel)
            else duplicated_judge
        )


def _execute_openai_judge(judge_id_in_path, model, messages_json, extra_body_json):
    """Executes a judge via OpenAI compatible endpoint."""
    payload = {}

    if judge_id_in_path:
        endpoint_path = f"judges/{judge_id_in_path}/openai/chat/completions"
        payload["model"] = model
        print_info(
            f"Executing Judge ID (via path): {judge_id_in_path} using OpenAI chat completions format."
        )
    else:
        endpoint_path = "judges/openai/chat/completions"
        payload["model"] = model
        print_info(
            f"Executing a Judge using generic OpenAI endpoint. Judge ID/Name: {model}"
        )

    try:
        payload["messages"] = json.loads(messages_json)
    except json.JSONDecodeError:
        print_error("Invalid JSON for --messages. Aborting.")
        return

    if extra_body_json:
        try:
            payload["extra_body"] = json.loads(extra_body_json)
        except json.JSONDecodeError:
            print_warning("Invalid JSON for --extra-body. Skipping.")

    print_info("Attempting to execute with OpenAI compatible payload:")
    print_json(payload)
    result = _request("POST", endpoint_path, data=payload)
    if result:
        print_success("OpenAI compatible execution successful!")
        print_json(result.model_dump() if isinstance(result, BaseModel) else result)


# --- Click CLI Definition ---


@click.group()
def cli():
    """A CLI tool to interact with the Root Signals API."""
    pass


@cli.group()
def judge():
    """Judge management commands."""
    pass


@judge.command("list")
@click.option("--page-size", type=int, help="Number of results to return per page.")
@click.option("--cursor", help="The pagination cursor value.")
@click.option("--search", help="A search term to filter by.")
@click.option("--name", help="Filter by exact judge name.")
@click.option("--ordering", help="Which field to use for ordering the results.")
@click.option(
    "--is-preset/--not-is-preset", default=None, help="Filter by preset status."
)
@click.option(
    "--is-public/--not-is-public", default=None, help="Filter by public status."
)
@click.option(
    "--show-global/--not-show-global", default=None, help="Filter by global status."
)
def list_cmd(**kwargs):
    """List judges with optional filters."""
    _list_judges(**kwargs)


@judge.command("get")
@click.argument("judge_id")
def get_cmd(judge_id):
    """Get a specific judge by its ID."""
    _get_judge(judge_id)


@judge.command("create")
@click.option("--name", required=True, help="The name for the new judge.")
@click.option("--intent", required=True, help="The intent for the new judge.")
@click.option("--stage", help="The stage for the new judge.")
@click.option(
    "--evaluator-references",
    "evaluator_references_json",
    help="""'JSON string for evaluator references. E.g., '[{"id": "eval-id"}]""" "",
)
def create_cmd(name, intent, stage, evaluator_references_json):
    """Create a new judge."""
    _create_judge(name, intent, stage, evaluator_references_json)


@judge.command("update")
@click.argument("judge_id")
@click.option("--name", help="The new name for the judge.")
@click.option("--stage", help="The new stage for the judge.")
@click.option(
    "--evaluator-references",
    "evaluator_references_json",
    help="""'JSON string to update evaluator references. Use "[]" to clear.""" "",
)
def update_cmd(judge_id, name, stage, evaluator_references_json):
    """Update an existing judge (PATCH)."""
    _update_judge(judge_id, name, stage, evaluator_references_json)


@judge.command("delete")
@click.argument("judge_id")
@click.option(
    "--yes",
    is_flag=True,
    callback=lambda c, p, v: v or c.abort(),
    expose_value=False,
    prompt="Are you sure you want to delete this judge?",
)
def delete_cmd(judge_id):
    """Delete a judge by its ID."""
    _delete_judge(judge_id)


@judge.command("execute")
@click.argument("judge_id")
@click.option("--request", help="Request text.")
@click.option("--response", help="Response text to evaluate.")
@click.option(
    "--contexts",
    "contexts_json",
    help="""'JSON list of context strings. E.g., '["ctx1"]""" "",
)
@click.option(
    "--functions",
    "functions_json",
    help="""'JSON array for the "functions" field.""" "",
)
@click.option("--expected-output", help="Expected output text.")
@click.option("--tag", "tags", multiple=True, help="Add one or more tags.")
def execute_cmd(**kwargs):
    """Execute a judge with interaction details."""
    _execute_judge(**kwargs)


@judge.command("execute-by-name")
@click.argument("judge_name")
@click.option("--request", help="Request text.")
@click.option("--response", help="Response text to evaluate.")
@click.option(
    "--contexts",
    "contexts_json",
    help="""'JSON list of context strings. E.g., '["ctx1"]""" "",
)
@click.option(
    "--functions",
    "functions_json",
    help="""'JSON array for the "functions" field.""" "",
)
@click.option("--expected-output", help="Expected output text.")
@click.option("--tag", "tags", multiple=True, help="Add one or more tags.")
def execute_by_name_cmd(**kwargs):
    """Execute a judge by name with interaction details."""
    _execute_judge_by_name(**kwargs)


@judge.command("duplicate")
@click.argument("judge_id")
def duplicate_cmd(judge_id):
    """Duplicate an existing judge."""
    _duplicate_judge(judge_id)


@judge.command("exec-openai")
@click.argument("judge_id_in_path")
@click.option(
    "--model", required=True, help="LLM model for judge execution (e.g., gpt-4o)."
)
@click.option(
    "--messages",
    "messages_json",
    required=True,
    help="JSON string of the messages payload.",
)
@click.option(
    "--extra-body",
    "extra_body_json",
    help="Optional JSON string for extra_body parameters.",
)
def exec_openai_cmd(**kwargs):
    """Execute a specific judge via the OpenAI compatible API."""
    _execute_openai_judge(**kwargs)


@judge.command("exec-openai-generic")
@click.option(
    "--model",
    "model",
    required=True,
    help="Judge ID (or name) to use as the 'model' field.",
)
@click.option(
    "--messages",
    "messages_json",
    required=True,
    help="JSON string of the messages payload.",
)
@click.option(
    "--extra-body",
    "extra_body_json",
    help="Optional JSON string for extra_body parameters.",
)
def exec_openai_generic_cmd(model, messages_json, extra_body_json):
    """Execute a judge via the generic OpenAI API (judge is in the 'model' field)."""
    _execute_openai_judge(None, model, messages_json, extra_body_json)


if __name__ == "__main__":
    cli()
