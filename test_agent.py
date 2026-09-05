from app.agent import run_agent


response = run_agent(
    "Do we have an oscilloscope?"
)


print()
print("AI:")
print(response)