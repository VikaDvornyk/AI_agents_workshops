"""Interactive chat with the coding agent."""

from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage

from prompts import SYSTEM_PROMPT
from solution_agent import graph

THREAD_ID = "1"
EXIT_COMMANDS = {"quit", "exit", "q"}


def chat() -> None:
    print("\nCoding Agent — type your questions, 'quit' to exit\n")

    config = {"configurable": {"thread_id": THREAD_ID}}
    is_first_turn = True

    while True:
        user_input = input("You: ").strip()
        if not user_input:
            continue
        if user_input.lower() in EXIT_COMMANDS:
            print("Bye!")
            break

        new_messages: list[BaseMessage] = []
        if is_first_turn:
            new_messages.append(SystemMessage(content=SYSTEM_PROMPT))
            is_first_turn = False
        new_messages.append(HumanMessage(content=user_input))

        try:
            result = graph.invoke({"messages": new_messages}, config=config)
            print(f"\nAgent: {result['messages'][-1].content}\n")
        except Exception as e:
            print(f"\nError: {e}\n")


if __name__ == "__main__":
    chat()
