from pynput import mouse, keyboard
import time
import threading
import tkinter as tk

actions = []
is_recording = False
is_replaying = False
is_terminated = False
start_time = None


def on_move(x, y):
    global is_recording, start_time
    if is_recording:
        if start_time is None:
            start_time = time.time()
        actions.append(('move', x, y, time.time() - start_time))


def on_click(x, y, button, pressed):
    global is_recording, start_time
    if is_recording:
        if start_time is None:
            start_time = time.time()
        actions.append(('click', x, y, button, pressed, time.time() - start_time))


def on_scroll(x, y, dx, dy):
    global is_recording, start_time
    if is_recording:
        if start_time is None:
            start_time = time.time()
        actions.append(('scroll', x, y, dx, dy, time.time() - start_time))


def on_press(key):
    global is_recording, start_time
    if is_recording:
        if start_time is None:
            start_time = time.time()
        actions.append(('keypress', key, time.time() - start_time))

    if key == keyboard.KeyCode.from_char('x'):  # Listen to 'x' key press and terminate the program
        terminate_program()


def on_release(key):
    global is_recording, start_time
    if is_recording:
        if start_time is None:
            start_time = time.time()
        actions.append(('keyrelease', key, time.time() - start_time))


def toggle_recording():
    global is_recording, is_replaying, start_time
    if not is_recording and not is_replaying:
        is_recording = True
        start_time = None
        start_button.config(text="Stop Recording")
        replay_button.config(state=tk.DISABLED)
        print("Recording started...")
    elif is_recording and not is_replaying:
        is_recording = False
        start_button.config(text="Start Recording")
        replay_button.config(state=tk.NORMAL)
        print("Recording stopped.")


def replay_func():
    global is_replaying, is_terminated
    is_replaying = True
    print("Replaying actions...")
    while not is_terminated:
        last_time = 0
        for action in actions:
            if is_terminated:
                break
            action_type = action[0]
            delay = action[-1] - last_time
            time.sleep(delay)
            if action_type == 'move':
                _, x, y, _ = action
                mouse.Controller().position = (x, y)
            elif action_type == 'click':
                _, x, y, button, pressed, _ = action
                if pressed:
                    mouse.Controller().press(button)
                else:
                    mouse.Controller().release(button)
            elif action_type == 'scroll':
                _, x, y, dx, dy, _ = action
                mouse.Controller().scroll(dx, dy)
            elif action_type == 'keypress':
                _, key, _ = action
                keyboard.Controller().press(key)
            elif action_type == 'keyrelease':
                _, key, _ = action
                keyboard.Controller().release(key)
            last_time = action[-1]
    print("Replay finished.")
    replay_button.config(state=tk.NORMAL)
    is_replaying = False


def start_replay():
    global is_replaying
    if not is_replaying and actions:
        replay_button.config(state=tk.DISABLED)
        replay_thread = threading.Thread(target=replay_func)
        replay_thread.start()


def terminate_program():
    global is_terminated, is_recording, is_replaying
    is_terminated = True
    is_recording = False
    is_replaying = False
    root.destroy()


if __name__ == "__main__":
    print("Press '1' to start/stop recording actions. Press 'x' to terminate the program.")

    mouse_listener = mouse.Listener(on_move=on_move, on_click=on_click, on_scroll=on_scroll)
    mouse_listener.start()

    keyboard_listener = keyboard.Listener(on_press=on_press, on_release=on_release)
    keyboard_listener.start()

    root = tk.Tk()
    root.title("Action Recorder")
    root.geometry("300x200")

    start_button = tk.Button(root, text="Start Recording", width=15, command=toggle_recording)
    start_button.pack(pady=10)

    replay_button = tk.Button(root, text="Replay", width=15, command=start_replay, state=tk.DISABLED)
    replay_button.pack(pady=10)

    terminate_button = tk.Button(root, text="Terminate", width=15, command=terminate_program)
    terminate_button.pack(pady=10)

    root.mainloop()
