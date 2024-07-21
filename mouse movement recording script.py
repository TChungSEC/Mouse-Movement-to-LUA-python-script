from pynput import mouse, keyboard
import time

# Variables to store mouse movements
mouse_movements = []
recording = False

# Define hotkey (F2)
start_stop_key = keyboard.Key.f2

# Mouse event handler
def on_move(x, y):
    if recording:
        mouse_movements.append((x, y, time.time()))

# Keyboard event handler
def on_press(key):
    global recording
    try:
        if key == start_stop_key:
            recording = not recording
            if recording:
                print("Recording started...")
                mouse_movements.clear()
            else:
                print("Recording stopped.")
                generate_lua_script()
    except AttributeError:
        pass

def on_release(key):
    if key == keyboard.Key.esc:
        # Stop listener
        return False

# Generate Lua script
def generate_lua_script():
    with open("mouse_movements.lua", "w") as f:
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
    print("Lua script generated: mouse_movements.lua")

# Start listeners
mouse_listener = mouse.Listener(on_move=on_move)
keyboard_listener = keyboard.Listener(on_press=on_press, on_release=on_release)

mouse_listener.start()
keyboard_listener.start()

mouse_listener.join()
keyboard_listener.join()