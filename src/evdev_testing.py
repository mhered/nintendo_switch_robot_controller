import evdev

# Adjust to your event numbers (check evtest output)
joycon_left_IMU_path = "/dev/input/event20"
joycon_right_IMU_path = "/dev/input/event22"
joycon_combined_path = "/dev/input/event23"

# Open the left Joy-Con device
joycon_left = evdev.InputDevice(joycon_left_IMU_path)
print(f"Listening to {joycon_left.name} at {joycon_left_IMU_path}")

# Read events from Joy-Con
for event in joycon_left.read_loop():
    print(event)
