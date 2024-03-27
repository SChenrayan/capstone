import datetime
import math
import time
from typing import Tuple

import pyzed.sl as sl
import ogl_viewer.viewer as gl
from util import log
from obj_files.vertex import Vertex
from obj_files.add_markers import add_markers


class ZedCamera:
    def __init__(self, ip, port):
        init = sl.InitParameters()
        init.depth_mode = sl.DEPTH_MODE.QUALITY
        init.coordinate_units = sl.UNIT.METER
        init.coordinate_system = sl.COORDINATE_SYSTEM.RIGHT_HANDED_Y_UP  # OpenGL's coordinate system is right_handed
        init.camera_resolution = sl.RESOLUTION.HD720
        init.sdk_verbose = True
        init.set_from_stream(ip, port)
        self._log(f"--- Opening camera on address: {ip}:{port}")
        self._zed = sl.Camera()
        status = self._zed.open(init)
        if status != sl.ERROR_CODE.SUCCESS:
            self._log("Camera Open : " + repr(status) + ". Exit program.")
            raise RuntimeError(f"Error opening ZED camera with IP: {ip}:{port}")

        self._log(f"--- Opened camera")

        self._positional_tracking_parameters = sl.PositionalTrackingParameters()
        self._positional_tracking_parameters.set_floor_as_origin = True
        self._positional_tracking_parameters.enable_imu_fusion = False

        returned_state = self._zed.enable_positional_tracking(self._positional_tracking_parameters)
        if returned_state != sl.ERROR_CODE.SUCCESS:
            self._log("Enable Positional Tracking Failed : " + repr(returned_state) + ". Exit program.")
            exit()

        self._log("--- Enabled positional tracking")

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
        self._warnings = []
        self._position = sl.Pose()
        self._global_position = sl.Pose()
        self._image = sl.Mat()
        self._pymesh = sl.Mesh()
        self._last_call = time.time()

        self._mapping_active = False
        self._running = False

        self._viewer = gl.GLViewer()

        self.FILEPATH = "mesh_gen.obj"
    
    def _log(self, msg):
        log(msg, "ZED")

    def run(self):
        self._running = True
        self._last_call = time.time()
        init_position = sl.Transform()
        self._zed.reset_positional_tracking(init_position)
        self._viewer.init(self._zed.get_camera_information().camera_configuration.calibration_parameters.left_cam, self._pymesh, 1)
        self._log("Initialized view")

    def grab(self):
        available = self._viewer.is_available()
        if not self._running or not available:
            self._log(f"Unable to grab, running = {self._running}, available = {available}")
            return False
        grab = self._zed.grab(self._runtime_parameters)
        if grab == sl.ERROR_CODE.SUCCESS:
            self._zed.retrieve_image(self._image, sl.VIEW.LEFT)
            self._zed.get_position(self._position)
            tracking_state, global_vertex = self.get_global_position()

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
                
            self._viewer.update_view(self._image, self._position.pose_data(), global_vertex.as_tuple(), tracking_state, mapping_state)
        else:
            self._log(f"Grabbing from ZED camera failed. ERROR CODE: {grab}")
        return True

    def get_global_position(self) -> Tuple[Vertex, sl.POSITIONAL_TRACKING_STATE]:
        state = self._zed.get_position(self._global_position, sl.REFERENCE_FRAME.WORLD)
        if state == sl.POSITIONAL_TRACKING_STATE.OK:
            translation = sl.Translation()
            x = round(self._global_position.get_translation(translation).get()[0], 3)
            y = round(self._global_position.get_translation(translation).get()[1], 3)
            z = round(self._global_position.get_translation(translation).get()[2], 3)
            return state, Vertex(x, y, z)
        else:
            return state, Vertex(0, 0, 0)

    def add_marker(self) -> str:
        if not self._mapping_active:
            msg = "Cannot place markers while not mapping"
            self._log(msg)
            return msg
        vertex, state = self.get_global_position()
        if state == sl.POSITIONAL_TRACKING_STATE.OK:
            self._markers.append(vertex)
            msg = f"Marker added at position: {vertex.x}, {vertex.y}, {vertex.z}"
            self._log(msg)
            return msg
        else:
            msg = f"Unable to place marker because tracking state is {state}"
            self._log(msg)
            return msg

    def add_warning(self) -> str:
        if not self._mapping_active:
            msg = "Cannot place markers while not mapping"
            self._log(msg)
            return msg
        point_cloud = sl.Mat()
        self._zed.retrieve_measure(point_cloud, sl.MEASURE.DEPTH)
        vertex, state = self.get_global_position()
        depth = point_cloud.get_value(self._zed.get_resolution().width / 2, self._zed.get_resolution().height / 2)[1]

        if state == sl.POSITIONAL_TRACKING_STATE.OK:
            rotation = self._global_position.get_rotation_vector()
            pitch, yaw = round(rotation[0], 3), round(rotation[1], 3)
            ground_proj = depth * math.cos(pitch) - 0.25  # Move marker closer to avoid clipping
            dx = -1 * math.sin(yaw) * ground_proj
            dy = depth * math.sin(pitch)
            dz = -1 * math.cos(yaw) * ground_proj

            displacement_vertex = Vertex(dx, dy, dz)
            warning_vertex = vertex + displacement_vertex

            self._warnings.append(warning_vertex)
            msg = f"Marker added at position: {warning_vertex.x}, {warning_vertex.y}, {warning_vertex.z}"
            self._log(msg)
            return msg
        else:
            msg = f"Unable to place marker because tracking state is {state}"
            self._log(msg)
            return msg

    def toggle_mapping(self):
        if not self._running:
            raise RuntimeError("Cannot enable mapping when the viewer is not running.")

        self._viewer.lock()
        if not self._mapping_active:
            init_position = sl.Transform()
            self._zed.reset_positional_tracking(init_position)
            self._zed.enable_spatial_mapping(self._spatial_mapping_parameters)

            self._last_call = time.time()

            self._mapping_active = True
        else:
            self.extract()
            self._markers = []
            self._warnings = []
            self._mapping_active = False
            self._viewer.clear_current_mesh()

        self._viewer.unlock()

    def extract(self):
        self._zed.extract_whole_spatial_map(self._pymesh)
        filter_params = sl.MeshFilterParameters()
        filter_params.set(sl.MESH_FILTER.MEDIUM)

        self._pymesh.filter(filter_params, True)
        self._pymesh.apply_texture(sl.MESH_TEXTURE_FORMAT.RGBA)

        time = datetime.datetime.now()
        timestamped_path = "mesh_objs/" + str(time.month) + "_" + str(time.day) + "_" + str(time.year) + "_" + str(time.hour) + "_" + str(time.minute) + "_" + str(time.second) + "_mesh_gen.obj"

        status = self._pymesh.save(timestamped_path)
        if status:
            self._log(f"Initial mesh saved under {timestamped_path}")
        else:
            self._log(f"Failed to save initial mesh under {timestamped_path}")

        add_markers(timestamped_path, self._markers, self._warnings)
        self._log(f"Markers added to mesh under {timestamped_path}")

    def close(self):
        self._log("Closing ZED")
        self._viewer.exit()
        self._running = False
        self._image.free(memory_type=sl.MEM.CPU)
        self._pymesh.clear()
        self._image.free()
        self._zed.disable_spatial_mapping()
        self._zed.disable_positional_tracking()
        self._zed.close()
