import inspect
from functools import partial

import pytest

from root.execution_logs import ExecutionLogs
from root.judges import AJudge, Judge, Judges
from root.models import Models
from root.objectives import AObjective, Objective, Objectives
from root.skills import AEvaluator, Evaluator, Evaluators


def _get_method_info(method):
    original_method = method

    while hasattr(method, "__wrapped__"):
        method = method.__wrapped__

    if hasattr(original_method, "__closure__") and original_method.__closure__:
        for cell in original_method.__closure__:
            if isinstance(cell.cell_contents, (partial, type(lambda: None))):
                method = cell.cell_contents
                break

    if isinstance(method, partial):
        method = method.func

    sig = inspect.signature(method)
    docs = inspect.getdoc(method) or ""
    params = [(name, param.default) for name, param in sig.parameters.items() if name not in ("_client", "self")]
    return {
        "params": params,
        "doc": docs,
    }


@pytest.mark.parametrize(
    "class_type",
    [Models, ExecutionLogs, Objectives, Evaluators, Judges],
)
def test_sync_async_methods_match(class_type):
    """Test that sync and async versions of methods have matching signatures and docs."""

    ignored_methods = {"from_response", "__init__", "__getattr__"}
    instance = class_type(client_context=lambda: None)

    # Get all methods that start with 'a' and their sync counterparts
    async_methods = [
        method
        for method in dir(instance)
        if method.startswith("a") and method[1:] in dir(instance) and method[1:] not in ignored_methods
    ]

    for async_method in async_methods:
        sync_method = async_method[1:]

        sync_fn = getattr(instance, sync_method)
        async_fn = getattr(instance, async_method)

        sync_info = _get_method_info(sync_fn)
        async_info = _get_method_info(async_fn)

        assert sync_info["params"] == async_info["params"], (
            # fmt: off
            f"Parameters don't match for {sync_method}/{async_method}:\n"
            f"Sync: {sync_info['params']}\n"
            f"Async: {async_info['params']}"
            # fmt: on
        )

        sync_doc = sync_info["doc"].lower()
        async_doc = async_info["doc"].replace("Asynchronously ", "").lower()
        assert sync_doc
        assert async_doc

        assert sync_doc == async_doc, (
            f"Docstrings don't match for {sync_method}/{async_method}:\nSync: {sync_doc}\nAsync: {async_doc}"
        )


@pytest.mark.parametrize(
    "sync_class,async_class",
    [
        (Objective, AObjective),
        (Evaluator, AEvaluator),
        (Judge, AJudge),
    ],
)
def test_wrapper_classes_sync_async_methods_match(sync_class, async_class):
    """Test that sync and async versions of wrapper classes have matching signatures and docs."""
    included_methods = {"run", "get", "versions", "evaluate"}  # List of methods we want to verify

    sync_methods = {name for name in dir(sync_class) if name in included_methods}

    for method_name in sync_methods:
        async_name = f"a{method_name}"
        assert async_name in dir(async_class), f"Missing async version of {method_name}"

        sync_method = getattr(sync_class, method_name)
        async_method = getattr(async_class, async_name)

        sync_info = _get_method_info(sync_method)
        async_info = _get_method_info(async_method)

        assert sync_info["params"] == async_info["params"], (
            f"Parameters don't match for {method_name}/{async_name}:\n"
            f"Sync: {sync_info['params']}\n"
            f"Async: {async_info['params']}"
        )

        sync_doc = sync_info["doc"].lower()
        async_doc = async_info["doc"].replace("Asynchronously ", "").lower()
        assert sync_doc
        assert async_doc

        assert sync_doc == async_doc, (
            f"Docstrings don't match for {method_name}/{async_name}:\nSync: {sync_doc}\nAsync: {async_doc}"
        )
