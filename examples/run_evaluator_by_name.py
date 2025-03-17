from root import RootSignals

client = RootSignals()

# Run a root evaluator by name using the run_by_name method
result = client.evaluators.run_by_name(
    name="Helpfulness",
    response="You can find the instructions from our Careers page.",
    request="Where can I find the application instructions?",
)

print(f"Score: {result.score} / 1.0")
print(f"Justification: {result.justification}")

# Run a custom evaluator by name
# Assuming you have created a custom evaluator named "Network Troubleshooting"
try:
    custom_result = client.evaluators.run_by_name(
        name="Network Troubleshooting",
        request="My internet is not working.",
        response="""
        I'm sorry to hear that your internet isn't working.
        Let's troubleshoot this step by step:
        1. Check if your router is powered on and all cables are properly connected
        2. Try restarting your router and modem
        3. Check if other devices can connect to the network
        4. Try connecting to a different network if available
        """,
    )

    print(f"Score: {custom_result.score} / 1.0")
    print(f"Justification: {custom_result.justification}")
except Exception as e:
    print(f"Error: {e}")
    print(
        "Note: This example requires that you have previously created a custom evaluator named 'Network Troubleshooting'"
    )
