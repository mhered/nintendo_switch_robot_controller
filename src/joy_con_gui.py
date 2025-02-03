import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import math


def add_parallelepiped(ax, pose, length, width, height, color, alpha=0.5):
    """
    Adds a parallelepiped to the given 3D axis based on its center of gravity (CoG),
    normal vector, and dimensions.

    Parameters:
    - ax: Matplotlib 3D axis handler.
    - pose: Tuple containing the CoG position (x, y, z) and a normal vector (nx, ny, nz).
    - length: Length of the parallelepiped.
    - width: Width of the parallelepiped.
    - height: Height of the parallelepiped.
    - color: RGB tuple for the parallelepiped color.
    - alpha: Transparency of the parallelepiped faces.

    Returns:
    - True if the parallelepiped is successfully added, False otherwise.
    """
    try:
        # Unpack pose parameters
        cog = np.array(pose[:3])  # Center of Gravity
        normal = np.array(pose[3:])  # Normal vector

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

        # Add the parallelepiped to the 3D axis
        poly3d = [[list(vertex) for vertex in face] for face in faces]
        ax.add_collection3d(
            Poly3DCollection(
                poly3d, facecolors=color, linewidths=3, edgecolors=color, alpha=alpha
            )
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


length, width, height = 102, 35.9, 13.9  # Joy-Con dimensions in mm
neon_red = (255 / 255, 60 / 255, 40 / 255)  # Nintendo Switch Neon Joy-Con Red
neon_blue = (10 / 255, 185 / 255, 230 / 255)  # Nintendo Switch Neon Joy-Con Blue


# Function to update the drawing based on new poses
def update_drawing(ax, left_joy_con_pose, right_joy_con_pose):
    """Clears the axes and redraws the parallelepipeds at new poses."""
    ax.cla()  # Clear the axes

    # Add joy-con L (red)
    success1 = add_parallelepiped(
        ax, left_joy_con_pose[0] + left_joy_con_pose[1], 
        length, width, height, 
        neon_red
    )

    # Add joy-con R (blue)
    success2 = add_parallelepiped(
        ax, right_joy_con_pose[0] + right_joy_con_pose[1],
        length, width, height,
        neon_blue
    )

    # Adjust axis limits to fit both parallelepipeds
    all_x = [
        left_joy_con_pose[0][0],
        right_joy_con_pose[0][0] + width,
        left_joy_con_pose[0][0] + width,
    ]
    all_y = [-width / 2, width / 2, -width / 2, width / 2]
    all_z = [0, height, height]

    ax.set_xlim(min(all_x) - 10, max(all_x) + 10)
    ax.set_ylim(min(all_y) - 10, max(all_y) + 10)
    ax.set_zlim(min(all_z) - 10, max(all_z) + 10)

    set_axes_equal(ax)  # Ensure equal scaling

    plt.draw()  # Redraw the figure

def orientation_vector(tilt_angle_x, tilt_angle_y):
    """
    Computes the orientation vector (normal to the main face) based on tilt angles.

    Parameters:
    - tilt_angle_x: Rotation around the X-axis in radians.
    - tilt_angle_y: Rotation around the Y-axis in radians.

    Returns:
    - A unit vector [nx, ny, nz] representing the orientation.
    """
    nx = math.sin(tilt_angle_y) * math.cos(tilt_angle_x)
    ny = math.sin(tilt_angle_x)
    nz = math.cos(tilt_angle_y) * math.cos(tilt_angle_x)
    
    return [nx, ny, nz]  # Normalized by trigonometry

# Main execution flow with keyboard interaction using Matplotlib's key event handling
fig, ax = setup_figure()

# Initial poses
left_tilt_angle_x = 0  # Initial tilt angle around X-axis of left joy-con
left_tilt_angle_y = 0  # Initial tilt angle around Y-axis of left joy-con

right_tilt_angle_x = 0  # Initial tilt angle around X-axis of right joy-con
right_tilt_angle_y = 0  # Initial tilt angle around Y-axis of right joy-con

left_joy_con_pose = ([0, 0, 0], orientation_vector(left_tilt_angle_x, left_tilt_angle_y))  # Base at (0,0,0)
right_joy_con_pose = ([90, 0, 0], orientation_vector(right_tilt_angle_x, right_tilt_angle_y))  # Shifted position

# Initial drawing
update_drawing(ax, left_joy_con_pose, right_joy_con_pose)
plt.ion()  # Enable interactive mode
plt.show()

# Rotation step in radians
rotation_step = 5 * (math.pi / 180)  # 5-degree rotation

def on_key(event):
    global left_tilt_angle_y, left_tilt_angle_x, left_joy_con_pose, right_tilt_angle_y, right_tilt_angle_x, right_joy_con_pose

    if event.key == "w":  # Rotate left joy-con up
        left_tilt_angle_x += rotation_step
    elif event.key == "s":  # Rotate left joy-con down
        left_tilt_angle_x -= rotation_step
    elif event.key == "d":  # Rotate left joy-con left
        left_tilt_angle_y += rotation_step
    elif event.key == "a":  # Rotate left joy-con right
        left_tilt_angle_y -= rotation_step
    elif event.key == "i":  # Rotate right joy-con up
        right_tilt_angle_x += rotation_step
    elif event.key == "k":  # Rotate right joy-con down
        right_tilt_angle_x -= rotation_step
    elif event.key == "l":  # Rotate right joy-con left
        right_tilt_angle_y += rotation_step
    elif event.key == "j":  # Rotate right joy-con right
        right_tilt_angle_y -= rotation_step


    # Compute new normal vector with combined rotations
    left_joy_con_pose = ([0, 0, 0], orientation_vector(left_tilt_angle_x, left_tilt_angle_y))  
    right_joy_con_pose = ([90, 0, 0], orientation_vector(right_tilt_angle_x, right_tilt_angle_y))  

    # Update the drawing with the new pose
    update_drawing(ax, left_joy_con_pose, right_joy_con_pose)
    plt.draw()  # Redraw the plot


# Disable default Matplotlib key bindings (e.g., "s" for save)
fig.canvas.mpl_disconnect(fig.canvas.manager.key_press_handler_id)

# Connect key press events
fig.canvas.mpl_connect("key_press_event", on_key)

# Keep the plot open and responsive
plt.ioff()  # Disable interactive mode when finished
plt.show()  # Keep the final state displayed
