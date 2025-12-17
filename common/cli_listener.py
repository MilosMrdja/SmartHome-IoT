from prompt_toolkit import PromptSession
from prompt_toolkit.patch_stdout import patch_stdout
from simulators.dl_simulator import set_led_state

def run_console_listener(stop_event):
    session = PromptSession()
    print("Type: LED ON, LED OFF or EXIT")

    while not stop_event.is_set():
        
        with patch_stdout():
            try:
                cmd = session.prompt("> ").strip().lower()
            except (EOFError, KeyboardInterrupt):
                stop_event.set()
                break

        if cmd == "led on":
            set_led_state(True)
            print("LED set to ON")

        elif cmd == "led off":
            set_led_state(False)
            print("LED set to OFF")

        elif cmd == "exit":
            print("Stopping application...")
            stop_event.set()
            break

        else:
            print("Unknown command. Use LED ON / LED OFF / EXIT")
