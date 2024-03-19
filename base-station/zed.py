import threading
import time

import pyzed.sl as sl
import ogl_viewer.viewer as gl


def main(ip, port):
    init = sl.InitParameters()
    init.depth_mode = sl.DEPTH_MODE.QUALITY
    init.coordinate_units = sl.UNIT.METER
    init.coordinate_system = sl.COORDINATE_SYSTEM.RIGHT_HANDED_Y_UP  # OpenGL's coordinate system is right_handed
    init.camera_resolution = sl.RESOLUTION.HD720
    init.set_from_stream(ip, port)
    zed = sl.Camera()
    status = zed.open(init)
    if status != sl.ERROR_CODE.SUCCESS:
        print("Camera Open : " + repr(status) + ". Exit program.")
        exit()

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
    # Close the ZED
    zed.close()


class ZedCamera:
    def __init__(self, ip, port):
        init = sl.InitParameters()
        init.depth_mode = sl.DEPTH_MODE.QUALITY
        init.coordinate_units = sl.UNIT.METER
        init.coordinate_system = sl.COORDINATE_SYSTEM.RIGHT_HANDED_Y_UP  # OpenGL's coordinate system is right_handed
        init.camera_resolution = sl.RESOLUTION.HD720
        init.set_from_stream(ip, port)
        print(f"-------------- Opening camera on address: {ip}:{port}")
        self._zed = sl.Camera()
        status = self._zed.open(init)
        if status != sl.ERROR_CODE.SUCCESS:
            print("Camera Open : " + repr(status) + ". Exit program.")
            raise RuntimeError(f"Error opening ZED camera with IP: {ip}:{port}")
    
        print(f"-------------- Opened camera")

        self._positional_tracking_parameters = sl.PositionalTrackingParameters()
        self._positional_tracking_parameters.set_floor_as_origin = True
        self._positional_tracking_parameters.enable_imu_fusion = False

        returned_state = self._zed.enable_positional_tracking(self._positional_tracking_parameters)
        if returned_state != sl.ERROR_CODE.SUCCESS:
            print("Enable Positional Tracking Failed : " + repr(returned_state) + ". Exit program.")
            exit()

        print("-------------- Enabled positional tracking")

        self._runtime_parameters = sl.RuntimeParameters()
        self._runtime_parameters.confidence_threshold = 50
        self._spatial_mapping_parameters = sl.SpatialMappingParameters(
            resolution=sl.MAPPING_RESOLUTION.MEDIUM,
            mapping_range=sl.MAPPING_RANGE.MEDIUM,
            max_memory_usage=2048,
            save_texture=True,
            use_chunk_only=True,
            reverse_vertex_order=False,
            map_type=sl.SPATIAL_MAP_TYPE.MESH,
        )

        self._markers = []
        self._position = sl.Pose()
        self._image = sl.Mat()
        self._pymesh = sl.Mesh()
        self._last_call = time.time()

        self._mapping_active = False
        self._running = False

        self._viewer = gl.GLViewer()

        self.FILEPATH = "mesh_gen.obj"

    def run(self):
        self._running = True
        self._last_call = time.time()
        init_position = sl.Transform()
        self._zed.reset_positional_tracking(init_position)
        self._viewer.init(self._zed.get_camera_information().camera_configuration.calibration_parameters.left_cam, self._pymesh, 1)
        print("-------------- Initialized view")

    def grab(self):
        print("-------------- in grab")
        available = self._viewer.is_available()
        if not self._running or not available:
            print(f"-------------- Unable to grab, running = {self.running}, available = {available}")
            return False
        grab = self._zed.grab(self._runtime_parameters)
        print(f"-------------- grab = {grab}")
        if grab == sl.ERROR_CODE.SUCCESS:
            self._zed.retrieve_image(self._image, sl.VIEW.LEFT)
            print(f"-------------- Retrieved image")
            tracking_state = self._zed.get_position(self._position)
            print(f"-------------- Tracking state = {tracking_state}")

            if self._mapping_active:
                mapping_state = self._zed.get_spatial_mapping_state()
                duration = time.time() - self._last_call
                if duration > 0.5 and self._viewer.chunks_updated():
                    self._zed.request_spatial_map_async()
                    self._last_call = time.time()

                if self._zed.get_spatial_map_request_status_async() == sl.ERROR_CODE.SUCCESS:
                    self._zed.retrieve_spatial_map_async(self._pymesh)
                    self._viewer.update_chunks()
            else:
                mapping_state = sl.SPATIAL_MAPPING_STATE.NOT_ENABLED

            self._viewer.update_view(self._image, self._position.pose_data(), tracking_state, mapping_state)
        else:
            print(f"Grabbing from ZED camera failed. ERROR CODE: {grab}")
        return True

    def toggle_mapping(self):
        if not self._running:
            raise RuntimeError("Cannot enable mapping when the viewer is not running.")
        if not self._mapping_active:
            init_position = sl.Transform()
            self._zed.reset_positional_tracking(init_position)
            self._zed.enable_spatial_mapping(self._spatial_mapping_parameters)

            self._pymesh.clear()
            self._viewer.clear_current_mesh()

            self._last_call = time.time()

            self._mapping_active = True
        else:
            self._zed.extract_whole_spatial_map(self._pymesh)
            filter_params = sl.MeshFilterParameters()
            filter_params.set(sl.MESH_FILTER.MEDIUM)
            self._pymesh.filter(filter_params, True)
            self._viewer.clear_current_mesh()
            self._pymesh.apply_texture(sl.MESH_TEXTURE_FORMAT.RGBA)

            status = self._pymesh.save(self.FILEPATH)
            if status:
                print(f"Initial mesh saved under {self.FILEPATH}")
            else:
                print(f"Failed to save initial mesh under {self.FILEPATH}")

            self._mapping_active = False

    def close(self):
        self._running = False
        self._image.free(memory_type=sl.MEM.CPU)
        self._pymesh.clear()
        self._image.free()
        self._zed.disable_spatial_mapping()
        self._zed.disable_positional_tracking()
        self._zed.close()


def temp_thread(zed: ZedCamera):
    while True:
        input()
        zed.toggle_mapping()


if __name__ == "__main__":
    zed = ZedCamera("10.110.241.132", 8002)
    thread = threading.Thread(target=temp_thread, args=(zed,))
    thread.daemon = True
    thread.start()
    zed.run()
    while zed.grab():
        pass
    zed.close()
