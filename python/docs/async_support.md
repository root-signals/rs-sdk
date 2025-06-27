# Asynchronous support

## *`run_async`* flag

Each synchronous method has its asynchronous equivalent. The SDK exposes asynchronous functionality through methods that are named the same way as their synchronous counterparts but with an *"a"* prefix, indicating they are asynchronous coroutines.

To use these methods, create your SDK client with the *`run_async=True`* argument. The default value for the *`run_async`* argument is *`False`*.

This sets the SDK in an asynchronous-ready environment, allowing you to benefit from asynchronous execution.

> #### Note
>
> Synchronous methods are not available in an asynchronous environment and vice versa.
> Attempting to use them interchangeably will result in an error.
>

## Examples

### Evaluator with ThreadPoolExecutor (sync)
```{literalinclude} ../examples/thread_pool.py
```
```json
// print(f"Evaluation result for {future}: {result}")

"Politeness": {
    "score": "0.7", 
    "cost": "None",
    "justification": "The response \"This is polite and clear.\" is neutral and 
    lacks any negative or aggressive language. It is concise and straightforward, 
    which can be seen as polite in its simplicity..."
}

"Clarity": {
    "score": "0.95", 
    "cost": "None",
    "justification": "The response \"This is polite and clear.\" is straightforward 
    and easy to understand at first read. The ideas are presented in a logical and concise manner,
    with sufficient detail..."
}
```

### Evaluator with Asyncio
```{literalinclude} ../examples/async_evaluation.py
```
```json
// print(f"Evaluation result for {eval}: {future.get(eval)}")

"Politeness": {
    "score": "0.7",
    "cost": "None",
    "justification": "The response \"This is polite and clear.\" is neutral and
    lacks any negative or aggressive language. It is concise and straightforward,
    which can be seen as polite in its simplicity..."
}

"Clarity": {
    "score": "0.95",
    "cost": "None",
    "justification": "The response \"This is polite and clear.\" is straightforward
    and easy to understand at first read. The ideas are presented in a logical and concise manner,
    with sufficient detail..."
}
```

