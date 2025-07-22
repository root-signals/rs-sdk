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

The `roots` CLI is a powerful command-line tool for interacting with the Root Signals API. It provides a convenient way to manage and execute your Judges directly from the terminal.

## Installation

You can install the `roots` CLI using the following command, which downloads and installs the script to `/usr/local/bin`:

```bash
curl -sSL https://app.rootsignals.ai/cli/install.sh | sh
```

Alternatively, you can install and run the CLI using `uvx`:

```bash
uvx root-signals-cli judge list
```

## Authentication

Before using the CLI, you must set your Root Signals API key as an environment variable:

```bash
export ROOTSIGNALS_API_KEY="your-api-key"
```

## Usage

The CLI is organized into a main command, `roots`, with subcommands for different functionalities. The primary resource you'll interact with is the `judge`.

### Judge Management

All Judge-related commands are available under the `roots judge` subcommand.

#### `list`

List all available Judges, with options for filtering and pagination.

```bash
roots judge list
```

**Options:**

*   `--page-size`: Number of results to return per page.
*   `--cursor`: The pagination cursor value.
*   `--search`: A search term to filter by.
*   `--name`: Filter by exact judge name.
*   `--ordering`: Which field to use for ordering the results.
*   `--is-preset / --not-is-preset`: Filter by preset status.
*   `--is-public / --not-is-public`: Filter by public status.
*   `--show-global / --not-show-global`: Filter by global status.

#### `get`

Retrieve a specific Judge by its ID.

```bash
roots judge get <judge_id>
```

#### `create`

Create a new Judge.

```bash
roots judge create --name "My New Judge" --intent "To evaluate the quality of LLM responses."
```

**Options:**

*   `--name`: The name for the new judge (required).
*   `--intent`: The intent for the new judge (required).
*   `--stage`: The stage for the new judge.
*   `--evaluator-references`: JSON string for evaluator references. E.g., `'[{"id": "eval-id"}]'`

#### `update`

Update an existing Judge.

```bash
roots judge update <judge_id> --name "My Updated Judge Name"
```

**Options:**

*   `--name`: The new name for the judge.
*   `--stage`: The new stage for the judge.
*   `--evaluator-references`: JSON string to update evaluator references. Use `"[]"` to clear.

#### `delete`

Delete a Judge by its ID. You will be prompted for confirmation.

```bash
roots judge delete <judge_id>
```

#### `duplicate`

Duplicate an existing Judge.

```bash
roots judge duplicate <judge_id>
```

### Judge Execution

#### `execute`

Execute a Judge with specific inputs.

```bash
roots judge execute <judge_id> --request "What is the capital of France?" --response "Paris"
```

**Options:**

*   `--request`: Request text.
*   `--response`: Response text to evaluate.
*   `--contexts`: JSON list of context strings. E.g., `'["ctx1"]'`
*   `--functions`: JSON array for the "functions" field.
*   `--expected-output`: Expected output text.
*   `--tag`: Add one or more tags.

#### `execute-by-name`

Execute a Judge by its name.

```bash
roots judge execute-by-name "My New Judge" --request "What is the capital of France?" --response "Paris"
```


## Development

This project uses `uv` for dependency management. To set up the development environment, run:

```bash
. .venv/bin/activate
uv pip sync pyproject.toml
```
