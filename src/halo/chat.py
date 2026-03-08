#!/usr/bin/env python3
"""
Halo Chat CLI - Console chat using the Halo API.
"""

import argparse
import json
from prompt_toolkit import PromptSession
from prompt_toolkit.history import InMemoryHistory
from halo.cli import HaloClient, HomeAssistantClient


def chat_mode(client: HaloClient, args):
    """Conversational chat mode - maintains full conversation history."""
    session = PromptSession(history=InMemoryHistory())
    messages = []

    print("Chat Mode - Type 'exit' to quit")
    print(f"Max tokens: {args.max_tokens}")
    print("=" * 40)

    while True:
        try:
            user_input = session.prompt("You: ")
            if user_input.lower() in ["exit", "quit"]:
                break
            messages.append({"role": "user", "content": user_input})
            prompt = "\n".join([f"{msg['role']}: {msg['content']}" for msg in messages])
            response = client.generate(prompt, max_new_tokens=args.max_tokens)
            if args.debug:
                print(f"\n[DEBUG]\n{json.dumps(client.get_debug_info(), indent=2)}\n")
            print(f"Halo: {response}")
            messages.append({"role": "assistant", "content": response})
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")

    print("Goodbye!")


def command_mode(client: HomeAssistantClient, args):
    """Task-oriented command mode - smart context for home assistant."""
    session = PromptSession(history=InMemoryHistory())

    print("Home Assistant Mode - Smart context, type 'exit' to quit")
    print(f"Max tokens: {args.max_tokens}")
    print(f"Current context: {client.context}")
    print("=" * 40)

    while True:
        try:
            user_input = session.prompt("> ")
            if user_input.lower() in ["exit", "quit"]:
                break
            if user_input.lower() == "reset":
                client.reset_context()
                print("Context reset!")
                continue
            response, context = client.command(user_input, args.max_tokens)
            if args.debug:
                print(f"\n[DEBUG]\n{json.dumps(client.get_debug_info(), indent=2)}\n")
            print(f"{response}")
            if context:
                print(f"[Context: {context}]")
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")

    print("Goodbye!")


def main():
    parser = argparse.ArgumentParser(description="Halo Chat CLI")
    parser.add_argument(
        "--base-url", default="http://localhost:8000", help="Base URL of the API"
    )
    parser.add_argument(
        "--max-tokens", type=int, default=50, help="Maximum tokens for generation"
    )
    parser.add_argument(
        "--mode",
        choices=["chat", "command"],
        default="chat",
        help="Chat mode: 'chat' for conversational (with history), 'command' for home assistant (smart context)",
    )
    parser.add_argument(
        "--debug", action="store_true", help="Show debug info (request/response)"
    )
    args = parser.parse_args()

    if args.mode == "chat":
        client = HaloClient(args.base_url)
        chat_mode(client, args)
    else:
        client = HomeAssistantClient(args.base_url)
        command_mode(client, args)


if __name__ == "__main__":
    main()
