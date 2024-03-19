from .face import Face
from .obj_file import ObjFile
from .vertex import Vertex


class Cube(ObjFile):
    def __init__(self):
        vertices = [
            Vertex(-1, -1, -1),
            Vertex(1, -1, -1),
            Vertex(1, 1, -1),
            Vertex(-1, 1, -1),
            Vertex(-1, -1, 1),
            Vertex(1, -1, 1),
            Vertex(1, 1, 1),
            Vertex(-1, 1, 1),
        ]

        faces = [
            Face([1, 2, 3, 4]),
            Face([5, 6, 7, 8]),
            Face([1, 2, 6, 5]),
            Face([2, 3, 7, 6]),
            Face([3, 4, 8, 7]),
            Face([4, 1, 5, 8]),
        ]

        super().__init__(vertices, faces)


class ExclamationPoint(ObjFile):
    def __init__(self):
        vertices = [
            Vertex(0, 0, 0),
            Vertex(0.25, 0, 0),
            Vertex(0.25, 0.25, 0),
            Vertex(0, 0.25, 0),
            Vertex(0, 0, 0.25),
            Vertex(0.25, 0, 0.25),
            Vertex(0.25, 0.25, 0.25),
            Vertex(0, 0.25, 0.5),
            Vertex(0, 0.5, 0),
            Vertex(0.25, 0.5, 0),
            Vertex(0.25, 1, 0),
            Vertex(0, 1, 0),
            Vertex(0, 0.5, 0.25),
            Vertex(0.25, 0.5, 0.25),
            Vertex(0.25, 1, 0.25),
            Vertex(0, 1, 0.25),
        ]

        faces = [
            Face([1, 2, 3, 4]),
            Face([5, 6, 7, 8]),
            Face([1, 2, 6, 5]),
            Face([2, 3, 7, 6]),
            Face([3, 4, 8, 7]),
            Face([4, 1, 5, 8]),
            Face([9, 10, 11, 12]),
            Face([13, 14, 15, 16]),
            Face([9, 10, 14, 13]),
            Face([10, 11, 15, 14]),
            Face([11, 12, 16, 15]),
            Face([12, 9, 13, 16]),
        ]

        super().__init__(vertices, faces)


if __name__ == "__main__":
    obj = ObjFile.from_path("hallway_high_quality.obj")
    point = ExclamationPoint()
    point.set_offset(Vertex(0, 0, 0), obj.get_offset())
    with open("hallway_high_quality.obj", "a") as f:
        f.write(str(point))
