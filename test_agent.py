from app.agent import run_agent

print("========================================")
print("   College Lab Equipment AI Agent")
print("========================================")
print("Type your request below.")
print("Type 'exit' to stop.\n")

while True:
    question = input("You: ").strip()

    if not question:
        continue

    if question.lower() == "exit":
        print("Exiting agent...")
        break

    try:
        response = run_agent(question)

        print("\nAI:")
        print(response)
        print()

    except Exception as e:
        print("\nError:", e)
        print()