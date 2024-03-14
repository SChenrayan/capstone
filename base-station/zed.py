import time
import pyzed.sl as sl
import ogl_viewer.viewer as gl


def main(ip, port):
    init = sl.InitParameters()
    init.depth_mode = sl.DEPTH_MODE.NEURAL
    init.coordinate_units = sl.UNIT.METER
    init.coordinate_system = sl.COORDINATE_SYSTEM.RIGHT_HANDED_Y_UP  # OpenGL's coordinate system is right_handed
    init.camera_resolution = sl.RESOLUTION.HD720
    init.set_from_stream(ip, port)
    zed = sl.Camera()
    status = zed.open(init)
    if status != sl.ERROR_CODE.SUCCESS:
        print("Camera Open : " + repr(status) + ". Exit program.")
        exit()

    camera_infos = zed.get_camera_information()
    pose = sl.Pose()

    tracking_state = sl.POSITIONAL_TRACKING_STATE.OFF
    positional_tracking_parameters = sl.PositionalTrackingParameters()
    positional_tracking_parameters.set_floor_as_origin = True
    returned_state = zed.enable_positional_tracking(positional_tracking_parameters)
    if returned_state != sl.ERROR_CODE.SUCCESS:
        print("Enable Positional Tracking : " + repr(status) + ". Exit program.")
        exit()

    spatial_mapping_parameters = sl.SpatialMappingParameters(resolution=sl.MAPPING_RESOLUTION.MEDIUM,
                                                             mapping_range=sl.MAPPING_RANGE.MEDIUM,
                                                             max_memory_usage=2048, save_texture=False,
                                                             use_chunk_only=True, reverse_vertex_order=False,
                                                             map_type=sl.SPATIAL_MAP_TYPE.MESH)
    pymesh = sl.Mesh()
    mapping_state = sl.SPATIAL_MAPPING_STATE.NOT_ENABLED

    runtime_parameters = sl.RuntimeParameters()
    runtime_parameters.confidence_threshold = 50

    mapping_activated = False

    image = sl.Mat()
    point_cloud = sl.Mat()
    pose = sl.Pose()

    markers = []
    add_marker = False

    viewer = gl.GLViewer()

    viewer.init(zed.get_camera_information().camera_configuration.calibration_parameters.left_cam, pymesh,
                1)
    print("Press on 'Space' to enable / disable spatial mapping")
    print("Disable the spatial mapping after enabling it will output a .obj mesh file")
    while viewer.is_available():
        # Grab an image, a RuntimeParameters object must be given to grab()
        if zed.grab(runtime_parameters) == sl.ERROR_CODE.SUCCESS:
            # Retrieve left image
            zed.retrieve_image(image, sl.VIEW.LEFT)
            # Update pose data (used for projection of the mesh over the current image)
            tracking_state = zed.get_position(pose)

            if mapping_activated:
                mapping_state = zed.get_spatial_mapping_state()
                # Compute elapsed time since the last call of Camera.request_spatial_map_async()
                duration = time.time() - last_call
                # Ask for a mesh update if 500ms elapsed since last request
                if (duration > .5 and viewer.chunks_updated()):
                    zed.request_spatial_map_async()
                    last_call = time.time()

                if zed.get_spatial_map_request_status_async() == sl.ERROR_CODE.SUCCESS:
                    zed.retrieve_spatial_map_async(pymesh)
                    viewer.update_chunks()

                if add_marker:
                    markers.append(pose)

            change_state, add_marker = viewer.update_view(image, pose.pose_data(), tracking_state, mapping_state)

            if change_state:
                if not mapping_activated:
                    init_pose = sl.Transform()
                    zed.reset_positional_tracking(init_pose)
                    markers = []

                    # Configure spatial mapping parameters
                    spatial_mapping_parameters.resolution_meter = sl.SpatialMappingParameters().get_resolution_preset(
                        sl.MAPPING_RESOLUTION.MEDIUM)
                    spatial_mapping_parameters.use_chunk_only = True
                    # TODO: Check if we can save texture below??
                    spatial_mapping_parameters.save_texture = False  # Set to True to apply texture over the created mesh
                    spatial_mapping_parameters.map_type = sl.SPATIAL_MAP_TYPE.MESH

                    # Enable spatial mapping
                    zed.enable_spatial_mapping(spatial_mapping_parameters)

                    # Clear previous mesh data
                    pymesh.clear()
                    viewer.clear_current_mesh()

                    # Start timer
                    last_call = time.time()

                    mapping_activated = True
                else:
                    # Extract whole mesh
                    zed.extract_whole_spatial_map(pymesh)

                    filter_params = sl.MeshFilterParameters()
                    filter_params.set(sl.MESH_FILTER.MEDIUM)
                    # Filter the extracted mesh
                    pymesh.filter(filter_params, True)
                    viewer.clear_current_mesh()

                    # If textures have been saved during spatial mapping, apply them to the mesh
                    if spatial_mapping_parameters.save_texture:
                        print("Save texture set to : {}".format(spatial_mapping_parameters.save_texture))
                        pymesh.apply_texture(sl.MESH_TEXTURE_FORMAT.RGBA)

                    # Save mesh as an obj file
                    filepath = "mesh_gen.obj"
                    status = pymesh.save(filepath)
                    if status:
                        print("Mesh saved under " + filepath)
                        # TODO: Add markers to mesh
                    else:
                        print("Failed to save the mesh under " + filepath)

                    mapping_state = sl.SPATIAL_MAPPING_STATE.NOT_ENABLED
                    mapping_activated = False

    image.free(memory_type=sl.MEM.CPU)
    pymesh.clear()
    # Disable modules and close camera
    zed.disable_spatial_mapping()
    zed.disable_positional_tracking()
    zed.close()

    # Free allocated memory before closing the camera
    pymesh.clear()
    image.free()
    point_cloud.free()
    # Close the ZED
    zed.close()
