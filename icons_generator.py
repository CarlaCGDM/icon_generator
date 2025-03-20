import bpy
import math
import mathutils
import os

# Define the resolutions to render
RESOLUTIONS = [1024, 512, 256, 128, 64]

import mathutils

def scale_object_to_fit_camera(obj, target_size=2):
    """Scale the object so that its front plane bounding box fits within the camera's view, with the largest side equal to `target_size`."""
    
    # Ensure we're in object mode
    bpy.ops.object.mode_set(mode='OBJECT')

    # Get the object's world-space bounding box corners
    bounding_box = [obj.matrix_world @ mathutils.Vector(corner) for corner in obj.bound_box]
    
    # Get the min and max values for the bounding box
    min_x = min(corner.x for corner in bounding_box)
    max_x = max(corner.x for corner in bounding_box)
    min_y = min(corner.y for corner in bounding_box)
    max_y = max(corner.y for corner in bounding_box)
    min_z = min(corner.z for corner in bounding_box)
    max_z = max(corner.z for corner in bounding_box)

    # Calculate the width and height of the front-facing plane
    width = max_x - min_x
    depth = max_y - min_y  # Depending on the camera angle, this could be front or side
    height = max_z - min_z

    # Determine which plane is facing the camera
    front_plane = "XY"  # Assume the front plane is the X-Y plane (this is a common case)
    
    # For a different camera angle, we might need additional checks to determine which plane is facing the camera.
    # For now, let's assume the front-facing plane is along the XY axis for simplicity.

    print(f"Object bounding box dimensions - Width: {width}, Depth: {depth}, Height: {height}")

    if front_plane == "XY":
        # If the front plane is XY, determine the larger dimension (width vs. depth)
        largest_dimension = max(width, depth)
        scale_factor = target_size / largest_dimension
        print(f"Scaling the object to fit the front plane XY. Largest dimension: {largest_dimension}. Scale factor: {scale_factor}")
        # Apply the scale to the object
        obj.scale = (scale_factor, scale_factor, scale_factor)
    
    elif front_plane == "YZ":
        # If the front plane is YZ, then we'd scale based on height and depth
        largest_dimension = max(height, depth)
        scale_factor = target_size / largest_dimension
        print(f"Scaling the object to fit the front plane YZ. Largest dimension: {largest_dimension}. Scale factor: {scale_factor}")
        # Apply the scale to the object
        obj.scale = (scale_factor, scale_factor, scale_factor)
    
    elif front_plane == "ZX":
        # If the front plane is ZX, scale based on height and width
        largest_dimension = max(width, height)
        scale_factor = target_size / largest_dimension
        print(f"Scaling the object to fit the front plane ZX. Largest dimension: {largest_dimension}. Scale factor: {scale_factor}")
        # Apply the scale to the object
        obj.scale = (scale_factor, scale_factor, scale_factor)

def create_icons_folder():
    """Create the 'Icons' folder and subfolders for each resolution."""
    base_dir = os.path.dirname(bpy.data.filepath)  # Directory of the Blender file
    icons_dir = os.path.join(base_dir, "Icons")
    
    if not os.path.exists(icons_dir):
        os.makedirs(icons_dir)
        print(f"Created 'Icons' folder at: {icons_dir}")
    
    return icons_dir

def setup_render_settings(resolution):
    """Set up render settings for the given resolution."""
    bpy.context.scene.render.resolution_x = resolution
    bpy.context.scene.render.resolution_y = resolution
    bpy.context.scene.render.image_settings.file_format = 'PNG'
    bpy.context.scene.render.image_settings.color_mode = 'RGBA'  # For transparent background
    bpy.context.scene.render.film_transparent = True  # Enable transparent background
    print(f"Render settings updated for resolution: {resolution}x{resolution}")

def render_object(obj, resolution, output_dir):
    """Render an object at the specified resolution and save it to the output directory."""
    # Hide all other objects except the object and lights
    for other_obj in bpy.context.scene.objects:
        if other_obj != obj and other_obj.type != 'LIGHT':
            other_obj.hide_render = True
        else:
            other_obj.hide_render = False
    
    # Set the output file path
    output_path = os.path.join(output_dir, f"{resolution}.png")
    bpy.context.scene.render.filepath = output_path
    
    # Render the object
    print(f"Rendering {obj.name} at {resolution}x{resolution}...")
    bpy.ops.render.render(write_still=True)
    print(f"Saved render to: {output_path}")


def ensure_object_mode():
    """Ensure Blender is in Object Mode."""
    bpy.ops.object.mode_set(mode='OBJECT')

def standardize_object(obj):
    """Standardize the scale, origin, and location of an object."""
    print(f"Processing object: {obj.name}")
    
    # Print initial transformation values
    print(f"Rotation: {obj.rotation_euler}")
    print(f"Scale: {obj.scale}")
    
    # Select the object and make it active
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    
    # Apply the scale
    print("Applying scale...")
    bpy.ops.object.transform_apply(scale=True)
    
    # Apply the rotation
    print("Applying rotation...")
    bpy.ops.object.transform_apply(rotation=True)
    
    # Set the origin to the center of the geometry
    print("Setting origin to center of geometry...")
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
    
    # Clear the location (move the origin to (0, 0, 0))
    print("Clearing location...")
    bpy.ops.object.location_clear(clear_delta=False)
    
    # Scale to fit in view
    print("Scaling object to fit camera...")
    scale_object_to_fit_camera(obj)
    
    # Deselect the object
    obj.select_set(False)
    print("-" * 40)

def create_setup_collection():
    """Create or get the 'Setup' collection and ensure it exists."""
    if "Setup" not in bpy.data.collections:
        setup_collection = bpy.data.collections.new("Setup")
        bpy.context.scene.collection.children.link(setup_collection)
        print("Created 'Setup' collection.")
    else:
        setup_collection = bpy.data.collections["Setup"]
        print("'Setup' collection already exists.")
    return setup_collection

def add_camera_to_collection(collection):
    """Add a camera to the specified collection."""
    print("Adding camera...")
    camera_data = bpy.data.cameras.new(name="RenderCamera")
    camera_object = bpy.data.objects.new(name="RenderCamera", object_data=camera_data)
    collection.objects.link(camera_object)
    
    # Position the camera
    camera_object.location = (0, -4, 0)  # Adjust as needed
    camera_object.rotation_euler = (mathutils.Euler((math.radians(90), 0, 0), 'XYZ'))  # Pointing towards the origin
    return camera_object

def lights_exist():
    """Check if there are any lights already in the scene."""
    return any(obj.type == 'LIGHT' for obj in bpy.context.view_layer.objects)

def add_3_point_lighting_to_collection(collection):
    """Add a 3-point lighting system to the specified collection if no lights exist."""
    
    if lights_exist():
        print("Lights already exist in the scene. Skipping light setup.")
        return []
    
    print("Adding 3-point lighting...")
    
    # Key Light
    key_light_data = bpy.data.lights.new(name="KeyLight", type='POINT')
    key_light_data.energy = 3000
    key_light_object = bpy.data.objects.new(name="KeyLight", object_data=key_light_data)
    key_light_object.location = (5, -5, 5)
    collection.objects.link(key_light_object)
    
    # Fill Light
    fill_light_data = bpy.data.lights.new(name="FillLight", type='POINT')
    fill_light_data.energy = 1500
    fill_light_object = bpy.data.objects.new(name="FillLight", object_data=fill_light_data)
    fill_light_object.location = (-5, -5, 5)
    collection.objects.link(fill_light_object)
    
    # Back Light
    back_light_data = bpy.data.lights.new(name="BackLight", type='POINT')
    back_light_data.energy = 900
    back_light_object = bpy.data.objects.new(name="BackLight", object_data=back_light_data)
    back_light_object.location = (0, 5, 5)
    collection.objects.link(back_light_object)
    
    return key_light_object, fill_light_object, back_light_object

def ensure_unique_in_collection(collection, objects):
    """Ensure the given objects are only in the specified collection."""
    for obj in objects:
        for coll in obj.users_collection:
            if coll != collection:
                coll.objects.unlink(obj)
    print("Ensured objects are unique to the 'Setup' collection.")

def main():
    """Main function to standardize objects and set up the scene."""
    ensure_object_mode()
    
    # Check if the "Target" collection exists
    if "Target" not in bpy.data.collections:
        print("Collection 'Target' does not exist.")
        return
    
    # Create or get the "Setup" collection
    setup_collection = create_setup_collection()
    
    # Add camera and lights to the "Setup" collection
    camera_object = add_camera_to_collection(setup_collection)
    lights = add_3_point_lighting_to_collection(setup_collection)
    
    # Set the camera as the active camera
    bpy.context.scene.camera = camera_object
    
    # Force a scene update to ensure that the lights are fully applied and rendered
    bpy.context.view_layer.update()  # This forces the scene to update
    
    # Ensure the camera and lights are only in the "Setup" collection
    ensure_unique_in_collection(setup_collection, [camera_object] + list(lights))
    
    print("Setup complete! Camera and 3-point lighting added to the 'Setup' collection.")
    
    # Create the 'Icons' folder and subfolders
    icons_dir = create_icons_folder()
    
    # Get the "Target" collection
    target_collection = bpy.data.collections["Target"]
    
    # Standardize objects in the "Target" collection
    for obj in target_collection.objects:
        if obj.type == 'MESH':  # Ensure it's a mesh
            standardize_object(obj)
    
    # Iterate through all objects in the "Target" collection
    for obj in target_collection.objects:
        if obj.type == 'MESH':  # Ensure it's a mesh
            print(f"Processing object: {obj.name}")
            
            # Render the object at each resolution
            for res in RESOLUTIONS:
                icon_dir = os.path.join(icons_dir, obj.name)
                setup_render_settings(res)
                render_object(obj, res, icon_dir)
            
            print("-" * 40)

    print("Rendering complete! All icons saved in the 'Icons' folder.")

# Run the script
if __name__ == "__main__":
    main()