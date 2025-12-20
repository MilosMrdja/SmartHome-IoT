from prompt_toolkit import PromptSession
from prompt_toolkit.patch_stdout import patch_stdout
from simulators.dl_simulator import set_led_state
from simulators.db_simulator import set_buzzer_state
from common.locks import print_lock

def run_console_listener(stop_event):
    session = PromptSession()
    print("Type: LED ON, LED OFF, BUZZER ON or EXIT")

    while not stop_event.is_set():
        
        with patch_stdout():
            try:
                cmd = session.prompt("Type: LED ON, LED OFF, BUZZER ON or EXIT\n> ").strip().lower()
            except (EOFError, KeyboardInterrupt):
                stop_event.set()
                break

        if cmd == "led on":
            set_led_state(True)
            with print_lock:
                print("="*50)
                print("LED set to ON")

        elif cmd == "led off":
            set_led_state(False)
            with print_lock:
                print("="*50)
                print("LED set to OFF")

        elif cmd == "buzzer on":
            set_buzzer_state(True)
            with print_lock:
                print("="*50)
                print("BUZZER set to ON")

        elif cmd == "exit":
            with print_lock:
                print("="*50)
                print("Stopping application...")
            stop_event.set()
            break

        else:
            with print_lock:
                print("="*50)
                print("Unknown command. Use LED ON / LED OFF / EXIT")
