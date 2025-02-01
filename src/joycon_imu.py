import time
import numpy as np
from pyjoycon import JoyCon, get_R_id, get_L_id

class JoyConIMU:
    def __init__(self, is_right_joycon=True):
        """
        Initializes connection to the Joy-Con and sets up IMU processing.
        - is_right_joycon: Set to True for the right Joy-Con, False for the left.
        """
        joycon_id = get_R_id() if is_right_joycon else get_L_id()
        print(f"Detected Joy-Con ID: {joycon_id}")  # Debugging line

        if not joycon_id:
            raise Exception("Joy-Con not found! Ensure Bluetooth is enabled and Joy-Con is paired.")

        self.joycon = JoyCon(*joycon_id)
        self.orientation = np.array([0, 0, 1])  # Default orientation (pointing upwards)
        self.alpha = 0.98  # Complementary filter parameter

    def read_imu(self):
        """
        Reads IMU data from the Joy-Con and returns acceleration and gyro values.
        """
        data = self.joycon.get_status()
        acc = np.array([data["accel_x"], data["accel_y"], data["accel_z"]])
        gyro = np.array([data["gyro_x"], data["gyro_y"], data["gyro_z"]])
        return acc, gyro

    def update_orientation(self, dt=0.01):
        """
        Updates the orientation vector using a complementary filter.
        - dt: Time step for integration (in seconds).
        """
        acc, gyro = self.read_imu()

        # Normalize accelerometer data to get a gravity vector
        acc_norm = acc / np.linalg.norm(acc)

        # Convert gyro to radians/s and integrate (Euler integration)
        gyro_rad = np.deg2rad(gyro) * dt
        rotation_matrix = np.array([
            [1, -gyro_rad[2], gyro_rad[1]],
            [gyro_rad[2], 1, -gyro_rad[0]],
            [-gyro_rad[1], gyro_rad[0], 1]
        ])
        new_orientation = np.dot(rotation_matrix, self.orientation)

        # Complementary filter: combine gyro and accelerometer
        self.orientation = self.alpha * new_orientation + (1 - self.alpha) * acc_norm
        self.orientation /= np.linalg.norm(self.orientation)  # Normalize

        return self.orientation

if __name__ == "__main__":
    imu = JoyConIMU(is_right_joycon=True)  # Set to False for the left Joy-Con

    try:
        while True:
            orientation_vector = imu.update_orientation()
            print(f"Orientation Vector: {orientation_vector}")
            time.sleep(0.01)  # Adjust update frequency
    except KeyboardInterrupt:
        print("Stopping IMU reading.")
