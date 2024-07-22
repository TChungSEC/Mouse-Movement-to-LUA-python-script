from pynput import mouse, keyboard
import time
import os

# Variables to store mouse movements and settings
mouse_movements = []
recording = False
start_stop_key = keyboard.Key.f2  # Default hotkey
save_directory = os.path.dirname(os.path.abspath(__file__))  # Default to script's directory

def print_banner():
    """Print the initial banner and instructions."""
    print(f"""
----------------------------------
CREATED BY KEENAN D

Press the current hotkey ({map_key(start_stop_key)}) to start/stop recording.
Press F1 to change hotkey.
Press ESC to exit the program.
----------------------------------
""")

def change_hotkey():
    """Prompt user to press a new hotkey."""
    global start_stop_key
    print("Press any key to set as the new hotkey:")
    with keyboard.Listener(on_press=on_key_for_hotkey) as listener:
        listener.join()

def on_key_for_hotkey(key):
    """Handle key press events for changing hotkey."""
    global start_stop_key
    try:
        # Check if key is a special key or a character key
        if isinstance(key, keyboard.Key):
            start_stop_key = key
        elif isinstance(key, keyboard.KeyCode):
            start_stop_key = key
        print(f"Hotkey changed to: {map_key(start_stop_key)}")
        # Reload banner with new hotkey
        print_banner()
        return False  # Stop the listener after setting the new hotkey
    except AttributeError:
        pass

def map_key(key):
    """Map key object or string to its name."""
    if isinstance(key, keyboard.Key):
        return key.name.capitalize()
    elif isinstance(key, keyboard.KeyCode):
        return key.char.upper()
    return str(key)

def on_move(x, y):
    """Record mouse movements."""
    if recording:
        mouse_movements.append((x, y, time.time()))

def on_press(key):
    """Handle key press events."""
    global recording, start_stop_key
    try:
        if key == start_stop_key:
            recording = not recording
            if recording:
                print("Recording started...")
                mouse_movements.clear()
            else:
                print("Recording stopped.")
                generate_lua_script()
        elif key == keyboard.Key.f1:  # Change hotkey using F1
            change_hotkey()
    except AttributeError:
        pass

def on_release(key):
    """Stop the program if ESC is pressed."""
    if key == keyboard.Key.esc:
        return False

def generate_lua_script():
    """Generate Lua script and save to file with automatic sequential naming."""
    base_filename = "mouse_movements"
    extension = ".lua"
    file_number = 1
    output_file = os.path.join(save_directory, f"{base_filename}{file_number}{extension}")
    while os.path.exists(output_file):
        file_number += 1
        output_file = os.path.join(save_directory, f"{base_filename}{file_number}{extension}")

    with open(output_file, "w") as f:
        f.write("-- CREATED BY KEENAN D\n")
        f.write("-- Lua script for mouse movements\n")
        f.write("function OnEvent(event, arg)\n")
        f.write("    if (event == \"PROFILE_ACTIVATED\") then\n")
        f.write("        EnablePrimaryMouseButtonEvents(true)\n")
        f.write("    end\n")
        for i, (x, y, t) in enumerate(mouse_movements):
            if i > 0:
                dx = x - mouse_movements[i-1][0]
                dy = y - mouse_movements[i-1][1]
                dt = t - mouse_movements[i-1][2]
                f.write(f"    MoveMouseRelative({dx}, {dy})\n")
                f.write(f"    Sleep({int(dt * 1000)})\n")
        f.write("end\n")
    print(f"Lua script generated: {os.path.abspath(output_file)}")

# Print the initial banner
print_banner()

# Start listeners
mouse_listener = mouse.Listener(on_move=on_move)
keyboard_listener = keyboard.Listener(on_press=on_press, on_release=on_release)

mouse_listener.start()
keyboard_listener.start()

mouse_listener.join()
keyboard_listener.join()
