from typing import List

from .obj_examples import ExclamationPoint
from .obj_file import ObjFile
from .vertex import Vertex


def add_markers(path: str, dangers: List[Vertex]) -> None:
    """
    Adds exclamations points in a .obj file at each position in a list of dangers
    :param path: The path to the .obj file to edit
    :param dangers: List of Vertices that represents where to place the danger points
    :return: None
    """
    objs = [ObjFile.from_path(path)]
    for danger_vertex in dangers:
        offset = objs[-1].get_offset()
        danger_obj = ExclamationPoint()
        danger_obj.set_offset(danger_vertex, offset)
        objs.append(danger_obj)
    with open(path, "a") as f:
        for obj in objs[1:]:
            f.write(str(obj))


if __name__ == "__main__":
    add_markers("hallway_high_quality.obj", [Vertex(0, 0, 0), Vertex(1, 0, 0), Vertex(0, 0, 1)])
