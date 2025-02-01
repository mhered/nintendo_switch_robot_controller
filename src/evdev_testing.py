import evdev

# Adjust to your event numbers (check evtest output)
joycon_left_path = "/dev/input/event19"
joycon_right_path = "/dev/input/event20"

# Open the left Joy-Con device
joycon_left = evdev.InputDevice(joycon_left_path)
print(f"Listening to {joycon_left.name} at {joycon_left_path}")

# Read events from Joy-Con
for event in joycon_left.read_loop():
    print(event)
