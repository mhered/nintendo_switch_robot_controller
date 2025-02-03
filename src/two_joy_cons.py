import asyncio
import sys
from myjoycon import myJoyCon 


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
    # setup
    header = (" Joy-Con (L)          | Joy-Con (R) Units: deg \n"
              "  Roll   Pitch  Yaw   |  Roll   Pitch  Yaw   ")
    print(header)
    
    # loop
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
    joycons = [myJoyCon(path) for path in device_paths]
    monitor_tasks = [joycon.monitor() for joycon in joycons]
    display_task = display_orientations(joycons)
    # display_task = display_accelerations(joycons)

    await asyncio.gather(*monitor_tasks, display_task)


if __name__ == "__main__":
    asyncio.run(main())

