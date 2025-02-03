import evdev
import math
import matplotlib.pyplot as plt
import numpy as np
import sys
import time

def read_joycon_imu(device_path):
    try:
        device = evdev.InputDevice(device_path)
        print(f"Listening to {device_path} ({device.name})")
    except FileNotFoundError:
        print(f"Error: Device {device_path} not found.")
        return
    
    gyro = {'x': 0, 'y': 0, 'z': 0}
    accel = {'x': 0, 'y': 0, 'z': 0}
    
    for event in device.read_loop():
        if event.type == evdev.ecodes.EV_ABS:
            abs_event = evdev.categorize(event)
            
            if abs_event.event.code == evdev.ecodes.ABS_RX:
                gyro['x'] = abs_event.event.value
            elif abs_event.event.code == evdev.ecodes.ABS_RY:
                gyro['y'] = abs_event.event.value
            elif abs_event.event.code == evdev.ecodes.ABS_RZ:
                gyro['z'] = abs_event.event.value
            elif abs_event.event.code == evdev.ecodes.ABS_X:
                accel['x'] = abs_event.event.value
            elif abs_event.event.code == evdev.ecodes.ABS_Y:
                accel['y'] = abs_event.event.value
            elif abs_event.event.code == evdev.ecodes.ABS_Z:
                accel['z'] = abs_event.event.value
            
            orientation = calculate_orientation(accel, gyro)
            show_orientation(orientation)
            # plot_orientation_vector(orientation)

def show_orientation(orientation):
    sys.stdout.write(f"\rOrientation Vector: Roll={orientation['roll']: >+6.1f}°, Pitch={orientation['pitch']: >+6.1f}°, Yaw={orientation['yaw']: >+6.1f}°")
    sys.stdout.flush()


prev_time = time.time()
yaw_angle = 0.0  # Initialize yaw angle

ALPHA = 0.98  # Complementary filter constant (tunes how much we trust gyro vs accel)
GYRO_SENSITIVITY = 131.0  # Assuming ±250 dps range (check your device specs)

def calculate_orientation(accel, gyro):
    global yaw_angle, prev_time

    current_time = time.time()
    dt = current_time - prev_time
    prev_time = current_time

    # Compute roll and pitch using accelerometer
    roll = math.atan2(accel['y'], accel['z'])
    pitch = math.atan2(-accel['x'], math.sqrt(accel['y']**2 + accel['z']**2))

    # Convert gyro raw values to degrees per second
    gyro_x_dps = gyro['x'] / GYRO_SENSITIVITY
    gyro_y_dps = gyro['y'] / GYRO_SENSITIVITY
    gyro_z_dps = gyro['z'] / GYRO_SENSITIVITY

    # Integrate gyroscope data for yaw estimation
    yaw_angle += gyro_z_dps * dt

    # Normalize yaw to [0, 360)
    yaw_angle = yaw_angle % 360

    # Apply Complementary Filter: Blend gyro & accel data
    roll = ALPHA * (roll + math.radians(gyro_x_dps * dt)) + (1 - ALPHA) * roll
    pitch = ALPHA * (pitch + math.radians(gyro_y_dps * dt)) + (1 - ALPHA) * pitch

    return {
        'roll': math.degrees(roll),
        'pitch': math.degrees(pitch),
        'yaw': yaw_angle  # Yaw still needs magnetometer correction for long-term stability
    }

def plot_orientation_vector(orientation):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    
    roll = math.radians(orientation['roll'])
    pitch = math.radians(orientation['pitch'])
    yaw = math.radians(orientation['yaw'])
    
    # Define unit vector in initial position
    vector = np.array([1, 0, 0])
    
    # Rotation matrices
    Rx = np.array([
        [1, 0, 0],
        [0, math.cos(roll), -math.sin(roll)],
        [0, math.sin(roll), math.cos(roll)]
    ])
    
    Ry = np.array([
        [math.cos(pitch), 0, math.sin(pitch)],
        [0, 1, 0],
        [-math.sin(pitch), 0, math.cos(pitch)]
    ])
    
    Rz = np.array([
        [math.cos(yaw), -math.sin(yaw), 0],
        [math.sin(yaw), math.cos(yaw), 0],
        [0, 0, 1]
    ])
    
    # Apply rotations
    rotated_vector = Rz @ Ry @ Rx @ vector
    
    ax.quiver(0, 0, 0, rotated_vector[0], rotated_vector[1], rotated_vector[2], color='r', length=1.0)
    
    ax.set_xlim([-1, 1])
    ax.set_ylim([-1, 1])
    ax.set_zlim([-1, 1])
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.set_title('Orientation Vector')
    
    plt.show()

if __name__ == "__main__":
    read_joycon_imu('/dev/input/event22')
