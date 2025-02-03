from stl import mesh
from mpl_toolkits import mplot3d
from matplotlib import pyplot

# Create a new plot
figure = pyplot.figure()
axes = mplot3d.Axes3D(figure)

# Colors
neon_red = (255 / 255, 60 / 255, 40 / 255)  # Nintendo Switch Neon Joy-Con Red
neon_blue = (10 / 255, 185 / 255, 230 / 255)  # Nintendo Switch Neon Joy-Con Blue

alpha = 1

# Load the STL files and add the vectors to the plot
JoyCon_L = mesh.Mesh.from_file("./CAD/JoyCon_L_xs.stl")
axes.add_collection3d(mplot3d.art3d.Poly3DCollection(
                        JoyCon_L.vectors, 
                        # shade=True, 
                        # lightsource = mplot3d.art3d.LightSource(azdeg=315, altdeg=45),
                        facecolors=neon_red, 
                        linewidths=1, 
                        edgecolors="black", 
                        alpha=alpha)
                        )

JoyCon_R = mesh.Mesh.from_file("./CAD/JoyCon_R_xs.stl")
axes.add_collection3d(mplot3d.art3d.Poly3DCollection(
                        JoyCon_R.vectors, 
                        # shade=True, 
                        # lightsource = mplot3d.art3d.LightSource(azdeg=315, altdeg=45),
                        facecolors=neon_blue, 
                        linewidths=1, 
                        edgecolors="black", 
                        alpha=alpha)
                        )

# Auto scale to the mesh size
scale = JoyCon_L.points.flatten()
axes.auto_scale_xyz(scale, scale, scale)

# Show the plot to the screen
pyplot.show()