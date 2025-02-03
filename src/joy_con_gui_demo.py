import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import math
import asyncio

def draw_brick(ax, cog, euler_angles, length, width, height, color, alpha=0.5):
    """
    Draws a brick in the given 3D axis based on its center of gravity (CoG),
    normal vector, and dimensions.

    Parameters:
    - ax: Matplotlib 3D axis handler.
    - cog: CoG position (x, y, z) 
    - euler_angles: roll, pitch, yaw.
    - length: Length of the brick.
    - width: Width of the brick.
    - height: Height of the brick.
    - color: RGB tuple for the brick color.
    - alpha: Transparency of the brick faces.

    Returns:
    - True if the brick is successfully added, False otherwise.
    """
    try:
        # extract Euler angles 
        roll = euler_angles.get('roll', 0.0)
        pitch = euler_angles.get('pitch', 0.0)
        yaw = euler_angles.get('yaw', 0.0)

        # Compute the normal vector
        normal = orientation_vector_from_rpy(roll, pitch, yaw)

        # Normalize the normal vector
        normal = normal / np.linalg.norm(normal)

        # Define local coordinate system (aligning with the normal vector)
        z_axis = normal  # Normal is treated as the local z-axis
        x_axis = np.array([1, 0, 0])  # Default x-axis
        if np.allclose(z_axis, x_axis):  # Prevent singularity
            x_axis = np.array([0, 1, 0])
        x_axis = np.cross(z_axis, x_axis)
        x_axis /= np.linalg.norm(x_axis)  # Normalize
        y_axis = np.cross(z_axis, x_axis)  # Define y-axis
        y_axis /= np.linalg.norm(y_axis)  # Normalize

        # Define half-dimensions
        l2, w2, h2 = length / 2, width / 2, height / 2

        # Define vertices in local coordinates
        local_vertices = np.array(
            [
                [-l2, -w2, -h2],
                [l2, -w2, -h2],
                [l2, w2, -h2],
                [-l2, w2, -h2],  # Bottom face
                [-l2, -w2, h2],
                [l2, -w2, h2],
                [l2, w2, h2],
                [-l2, w2, h2],  # Top face
            ]
        )

        # Transform vertices to global coordinates
        transformation_matrix = np.column_stack((x_axis, y_axis, z_axis))
        global_vertices = np.dot(local_vertices, transformation_matrix.T) + cog

        # Define faces using transformed vertices
        faces = [
            [global_vertices[i] for i in [0, 1, 2, 3]],  # Bottom face
            [global_vertices[i] for i in [4, 5, 6, 7]],  # Top face
            [global_vertices[i] for i in [0, 1, 5, 4]],  # Side face
            [global_vertices[i] for i in [1, 2, 6, 5]],  # Side face
            [global_vertices[i] for i in [2, 3, 7, 6]],  # Side face
            [global_vertices[i] for i in [3, 0, 4, 7]],  # Side face
        ]

        # Add the brick to the 3D axis
        poly3d = [[list(vertex) for vertex in face] for face in faces]
        ax.add_collection3d(
            Poly3DCollection(
                poly3d, facecolors=color, linewidths=3, edgecolors=color, alpha=alpha
            )
        )

        # text label
        ax.text(
            cog[0], cog[1], cog[2] + height / 2,
            f"Roll: {math.degrees(euler_angles['roll']):.1f}º\n"
            f"Pitch: {math.degrees(euler_angles['pitch']):.1f}º",
            color='black'
        )

        return True  # Successful execution

    except Exception as e:
        print(f"Error: {e}")
        return False  # Failed execution
 
def set_axes_equal(ax):
    """Set equal aspect ratio for 3D plots (for older Matplotlib versions)."""
    x_limits = ax.get_xlim()
    y_limits = ax.get_ylim()
    z_limits = ax.get_zlim()

    x_range = abs(x_limits[1] - x_limits[0])
    y_range = abs(y_limits[1] - y_limits[0])
    z_range = abs(z_limits[1] - z_limits[0])

    max_range = max(x_range, y_range, z_range) / 2.0

    mid_x = np.mean(x_limits)
    mid_y = np.mean(y_limits)
    mid_z = np.mean(z_limits)

    ax.set_xlim(mid_x - max_range, mid_x + max_range)
    ax.set_ylim(mid_y - max_range, mid_y + max_range)
    ax.set_zlim(mid_z - max_range, mid_z + max_range)

# Function to initialize figure and axes
def setup_figure():
    """Creates and returns a Matplotlib 3D figure and axis."""
    fig = plt.figure()
    ax = fig.add_subplot(111, projection="3d")

    ax.set_xlabel("X (mm)")
    ax.set_ylabel("Y (mm)")
    ax.set_zlabel("Z (mm)")

    return fig, ax


def draw_joycons(orientations, ax):
    """
    Draws Joy-Cons based on their orientations.

    Parameters:
    - orientations: Dictionary where keys are device names and values are dictionaries
                    with 'roll', 'pitch', and 'yaw' angles in radians.
                    Example: {"JoyCon_L": {'roll': 0.0, 'pitch': 0.0, 'yaw': 0.0}}
    """
    # Joy-Con dimensions in mm
    length, width, height = 102, 35.9, 13.9

    # Colors
    neon_red = (255 / 255, 60 / 255, 40 / 255)  # Nintendo Switch Neon Joy-Con Red
    neon_blue = (10 / 255, 185 / 255, 230 / 255)  # Nintendo Switch Neon Joy-Con Blue

    # Base positions for left and right Joy-Cons
    cog_left = np.array([-60, 0, 0])     # Base position for left Joy-Con
    cog_right = np.array([60, 0, 0])     # Base position for right Joy-Con
    
    # Iterate through the orientations dictionary
    for device_name, angles in orientations.items():

        # Determine position and color based on device name
        if device_name == "JoyCon_L":
            position = cog_left
            color = neon_red
        elif device_name == "JoyCon_R":
            position = cog_right
            color = neon_blue
        else:
            # Default position and color for any other device
            position = np.array([0, 0, 0])
            color = (0.5, 0.5, 0.5)  # Grey color for unknown devices

        # Add the Joy-Con to the plot
        draw_brick(ax, position, angles, length, width, height, color)


    # Adjust axis limits to fit both bricks
    all_x = [
        cog_left[0],
        cog_right[0] + width,
        cog_left[0] + width,
    ]
    all_y = [-width / 2, width / 2, -width / 2, width / 2]
    all_z = [0, height, height]

    ax.set_xlim(min(all_x) - 10, max(all_x) + 10)
    ax.set_ylim(min(all_y) - 10, max(all_y) + 10)
    ax.set_zlim(min(all_z) - 10, max(all_z) + 10)

    set_axes_equal(ax)  # Ensure equal scaling

def orientation_vector_from_rpy(roll, pitch, yaw):
    """
    Converts roll, pitch, and yaw angles (in radians) to a normal vector.
    """
    # Define the reference vector along the z-axis
    reference_vector = np.array([0, 0, 1])

    # Rotation matrices
    Rz_yaw = np.array([
        [np.cos(yaw), -np.sin(yaw), 0],
        [np.sin(yaw),  np.cos(yaw), 0],
        [0,            0,           1]
    ])

    Ry_pitch = np.array([
        [ np.cos(pitch), 0, np.sin(pitch)],
        [ 0,             1, 0           ],
        [-np.sin(pitch), 0, np.cos(pitch)]
    ])

    Rx_roll = np.array([
        [1, 0,           0          ],
        [0, np.cos(roll), -np.sin(roll)],
        [0, np.sin(roll),  np.cos(roll)]
    ])

    # Combined rotation matrix
    R = Rz_yaw @ Ry_pitch @ Rx_roll

    # Apply rotation to the reference vector
    oriented_vector = R @ reference_vector

    # Normalize the resulting vector
    oriented_vector /= np.linalg.norm(oriented_vector)

    return oriented_vector


async def display_joycons(interval=0.1):
    # setup
    fig, ax = setup_figure()
    orientations = {"JoyCon_L": {'roll': 0.0, 'pitch': 0.0, 'yaw': 0.0},
                    "JoyCon_R": {'roll': 0.0, 'pitch': 0.0, 'yaw': 0.0}}

    plt.ion()  # Enable interactive mode
    draw_joycons(orientations, ax) # Initial draw
    plt.show()

    # loop
    while True:
        # update orientations
        orientations["JoyCon_L"]["roll"] += 0.01
        orientations["JoyCon_L"]["pitch"] = 0.0
        orientations["JoyCon_R"]["roll"] = 0.00
        orientations["JoyCon_R"]["pitch"] += 0.02
        
        ax.cla()
        draw_joycons(orientations, ax)
        fig.canvas.draw_idle()  # Schedule a redraw
        plt.pause(0.001)  # Yield to the GUI event loop

        await asyncio.sleep(interval)

async def main():
    display_task = display_joycons()
    await asyncio.gather(display_task)

if __name__ == "__main__":
    asyncio.run(main())
