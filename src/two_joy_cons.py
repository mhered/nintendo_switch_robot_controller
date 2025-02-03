import asyncio
import evdev
import math
import time
import sys
import numpy as np



class JoyCon:
    # Constants for Kalman Filter
    _ALPHA = 0.98 # Complementary filter constant (tunes how much we trust gyro vs accel)
    _PROCESS_NOISE_VARIANCE = 1e-5
    _MEASUREMENT_NOISE_VARIANCE = 1e-2
    _ACCEL_SENSITIVITY = 0.000244  # Convert raw accel values to G
    _GYRO_SENSITIVITY = 0.070  # Convert gyro raw values to deg/s

    def __init__(self, device_path):
        self.device_path = device_path
        self.device = evdev.InputDevice(device_path)
        self.gyro = {'x': 0, 'y': 0, 'z': 0}
        self.accel = {'x': 0, 'y': 0, 'z': 0}
        self.orientation = {'roll': 0.0, 'pitch': 0.0, 'yaw': 0.0}
        self.prev_time = time.time()
        self.yaw_angle = 0.0

        # Kalman Filter initialization
        self.state = np.zeros((4, 1))  # [roll, pitch, roll_bias, pitch_bias]
        self.P = np.eye(4)  # State covariance matrix
        self.Q = np.eye(4) * self._PROCESS_NOISE_VARIANCE  # Process noise covariance
        self.R = np.eye(2) * self._MEASUREMENT_NOISE_VARIANCE  # Measurement noise covariance

        print(f"Initialized JoyCon at {device_path} ({self.device.name})")

    async def monitor(self):
        async for event in self.device.async_read_loop():
            if event.type == evdev.ecodes.EV_ABS:
                self._process_event(event)
                self._update_orientation()

    def _process_event(self, event):
        if event.code == evdev.ecodes.ABS_RX:
            self.gyro['x'] = event.value * self._GYRO_SENSITIVITY # Convert gyro raw values to deg/s
        elif event.code == evdev.ecodes.ABS_RY:
            self.gyro['y'] = event.value * self._GYRO_SENSITIVITY # Convert gyro raw values to deg/s
        elif event.code == evdev.ecodes.ABS_RZ:
            self.gyro['z'] = event.value * self._GYRO_SENSITIVITY # Convert gyro raw values to deg/s
        elif event.code == evdev.ecodes.ABS_X:
            self.accel['x'] = event.value * self._ACCEL_SENSITIVITY # Convert accel raw values to G
        elif event.code == evdev.ecodes.ABS_Y:
            self.accel['y'] = event.value * self._ACCEL_SENSITIVITY # Convert accel raw values to G
        elif event.code == evdev.ecodes.ABS_Z:
            self.accel['z'] = event.value * self._ACCEL_SENSITIVITY # Convert accel raw values to G

    def _update_orientation(self):
        current_time = time.time()
        dt = current_time - self.prev_time
        self.prev_time = current_time

        # Compute roll using accelerometer
        roll = math.atan2(self.accel['y'], self.accel['z'])
        pitch = math.atan2(-self.accel['x'], math.sqrt(self.accel['y']**2 + self.accel['z']**2))

        # Compute pitch considering roll angle to extend range to [-180, 180]
        # pitch = math.atan2(-self.accel['x'], self.accel['y'] * math.sin(roll) + self.accel['z'] * math.cos(roll))

        # Integrate gyroscope data for yaw estimation
        self.yaw_angle += self.gyro['z'] * dt

        # Normalize yaw to [0, 360)
        self.yaw_angle %= 360

        # Apply Complementary Filter: Blend gyro & accel data
        roll = self._ALPHA * (roll + math.radians(self.gyro['x'] * dt)) + (1 - self._ALPHA) * roll
        pitch = self._ALPHA * (pitch + math.radians(self.gyro['y'] * dt)) + (1 - self._ALPHA) * pitch

        self.orientation = {
            'roll': math.degrees(roll),
            'pitch': math.degrees(pitch),
            'yaw': self.yaw_angle
        }
    
    def _update_orientation_Kalman(self):
        current_time = time.time()
        dt = current_time - self.prev_time
        self.prev_time = current_time

        # Predict Step
        F = np.eye(4)
        F[0, 2] = -dt
        F[1, 3] = -dt

        u = np.array([[self.gyro['x'] - self.state[2, 0]],
                      [self.gyro['y'] - self.state[3, 0]],
                      [0],
                      [0]])

        self.state = F @ self.state + u * dt
        self.P = F @ self.P @ F.T + self.Q

        # Measurement Update Step
        accel_roll = math.atan2(self.accel['y'], self.accel['z'])
        accel_pitch = math.atan2(-self.accel['x'], math.sqrt(self.accel['y']**2 + self.accel['z']**2))
        z = np.array([[accel_roll],
                      [accel_pitch]])

        H = np.array([[1, 0, 0, 0],
                      [0, 1, 0, 0]])

        y = z - H @ self.state
        S = H @ self.P @ H.T + self.R
        K = self.P @ H.T @ np.linalg.inv(S)
        self.state = self.state + K @ y
        self.P = (np.eye(4) - K @ H) @ self.P

        # Update orientation
        self.orientation = {
            'roll': math.degrees(self.state[0, 0]),
            'pitch': math.degrees(self.state[1, 0]),
            'yaw': self.yaw_angle  # Yaw can be updated similarly
        }

    def get_orientation(self):
        return self.orientation
    
    def get_accel(self):
        return self.accel

def show_orientation(orientations):
    for device_name, orientation in orientations.items():
        angles = (f" {orientation['roll']: >+6.1f}"
                   f" {orientation['pitch']: >+6.1f}"
                   f" {orientation['yaw']: >+6.1f}")
        if device_name == "Nintendo Switch Left Joy-Con IMU":
            angles_left = angles
        elif device_name == "Nintendo Switch Right Joy-Con IMU":
            angles_right = angles
            
    sys.stdout.write(f"\r{angles_left} |{angles_right}")
    sys.stdout.flush()

async def display_orientations(joycons, interval=0.1):
    header = (" Joy-Con (L)          | Joy-Con (R) Units: deg \n"
              "  Roll   Pitch  Yaw   |  Roll   Pitch  Yaw   ")
    print(header)
    while True:
        orientations = {joycon.device.name: joycon.get_orientation() for joycon in joycons}
        show_orientation(orientations)
        await asyncio.sleep(interval)

def show_acceleration(accelerations):
    for device_name, accel in accelerations.items():
        accels = (f" {accel['x']: >+6.1f}"
                   f" {accel['y']: >+6.1f}"
                   f" {accel['z']: >+6.1f}")
        if device_name == "Nintendo Switch Left Joy-Con IMU":
            accels_left = accels
        elif device_name == "Nintendo Switch Right Joy-Con IMU":
            accels_right = accels
            
    sys.stdout.write(f"\r{accels_left} |{accels_right}")
    sys.stdout.flush()

async def display_accelerations(joycons, interval=0.1):
    header = (" Joy-Con (L)          | Joy-Con (R) Units: g \n"
              " accelX accelY accelZ | accelX accelY accelZ ")
    print(header)
    while True:
        accelerations = {joycon.device.name: joycon.get_accel() for joycon in joycons}
        show_acceleration(accelerations)
        await asyncio.sleep(interval)

async def main():
    device_paths = ['/dev/input/event20', '/dev/input/event22']
    joycons = [JoyCon(path) for path in device_paths]
    monitor_tasks = [joycon.monitor() for joycon in joycons]
    display_task = display_orientations(joycons)
    # display_task = display_accelerations(joycons)

    await asyncio.gather(*monitor_tasks, display_task)


if __name__ == "__main__":
    asyncio.run(main())

