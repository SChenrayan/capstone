from typing import List

from .obj_examples import ExclamationPoint, PlusSign
from .obj_file import ObjFile
from .vertex import Vertex


def add_markers(path: str, markers: List[Vertex], warnings: List[Vertex]) -> None:
    """
    Adds exclamations points in a .obj file at each position in a list of dangers
    :param path: The path to the .obj file to edit
    :param markers: List of Vertices that represents where to place the marker points
    :param warnings: List of Vertices that represents where to place the warning points
    :return: None
    """
    objs = [ObjFile.from_path(path)]
    for marker in markers:
        offset = objs[-1].get_offset()
        plus = PlusSign()
        plus.set_offset(marker, offset)
        objs.append(plus)
    for warning in warnings:
        offset = objs[-1].get_offset()
        danger_obj = ExclamationPoint()
        danger_obj.set_offset(warning, offset)
        objs.append(danger_obj)
    with open(path, "a") as f:
        for obj in objs[1:]:
            f.write(str(obj))


if __name__ == "__main__":
    add_markers("hallway_high_quality.obj", [Vertex(0, 0, 0), Vertex(1, 0, 0), Vertex(0, 0, 1)], [Vertex(1, 1, 1)])
