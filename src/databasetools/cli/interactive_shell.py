from prompt_toolkit import PromptSession
from prompt_toolkit.history import InMemoryHistory

from .cli_main import cli


def start_interactive_shell():
    session = PromptSession(history=InMemoryHistory())
    while True:
        try:
            command = session.prompt("sgt>> ", completer=None)  # Add a completer for better UX
            if command in ["exit", "quit"]:
                break
            if command:
                cli.main(args=command.split(), prog_name="sgt")
        except KeyboardInterrupt:
            continue  # Ctrl-C pressed, loop again
        except EOFError:
            break  # Ctrl-D pressed, exit
    print("Exiting SERGEANT interactive shell.")


def run_interactive_shell():
    session = PromptSession()
    while True:
        try:
            user_input = session.prompt("sgt> ")
            if user_input in ["exit", "quit"]:
                break
            # Parsing the command line arguments as Click would do
            command = cli.make_context("sgt", user_input.split(), parent=None)
            cli.invoke(command)
        except EOFError:
            break  # Handle Ctrl+D
        except KeyboardInterrupt:
            continue  # Handle Ctrl+C
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    run_interactive_shell()
