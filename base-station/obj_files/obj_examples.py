from face import Face
from obj_file import ObjFile
from vertex import Vertex


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
            Vertex(-0.125, 0, -0.125),
            Vertex(0.125, 0, -0.125),
            Vertex(0.125, 0.25, -0.125),
            Vertex(-0.125, 0.25, -0.125),
            Vertex(-0.125, 0, 0.125),
            Vertex(0.125, 0, 0.125),
            Vertex(0.125, 0.25, 0.125),
            Vertex(-0.125, 0.25, 0.125),
            Vertex(-0.125, 0.5, -0.125),
            Vertex(0.125, 0.5, -0.125),
            Vertex(0.125, 1, -0.125),
            Vertex(-0.125, 1, -0.125),
            Vertex(-0.125, 0.5, 0.125),
            Vertex(0.125, 0.5, 0.125),
            Vertex(0.125, 1, 0.125),
            Vertex(-0.125, 1, 0.125),
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


class PlusSign(ObjFile):
    def __init__(self):
        vertices = [
            Vertex(-0.125, 0, -0.125),
            Vertex(0.125, 0, -0.125),
            Vertex(-0.125, 0, 0.125),
            Vertex(0.125, 0, 0.125),
            Vertex(-0.125, 0.166, -0.125),
            Vertex(0.125, 0.166, -0.125),
            Vertex(-0.125, 0.166, 0.125),
            Vertex(0.125, 0.166, 0.125),
            Vertex(-0.125, 0.333, -0.125),
            Vertex(0.125, 0.333, -0.125),
            Vertex(-0.125, 0.333, 0.125),
            Vertex(0.125, 0.333, 0.125),
            Vertex(-0.125, 0.5, -0.125),
            Vertex(0.125, 0.5, -0.125),
            Vertex(-0.125, 0.5, 0.125),
            Vertex(0.125, 0.5, 0.125),
            Vertex(-0.25, 0.166, -0.125),
            Vertex(0.25, 0.166, -0.125),
            Vertex(-0.25, 0.166, 0.125),
            Vertex(0.25, 0.166, 0.125),
            Vertex(-0.25, 0.333, -0.125),
            Vertex(0.25, 0.333, -0.125),
            Vertex(-0.25, 0.333, 0.125),
            Vertex(0.25, 0.333, 0.125),
        ]

        faces = [
            Face([1, 2, 4, 3]),
            Face([13, 14, 16, 15]),
            Face([1, 2, 6, 5]),
            Face([9, 10, 14, 13]),
            Face([17, 18, 22, 21]),
            Face([3, 4, 8, 7]),
            Face([11, 12, 16, 15]),
            Face([19, 20, 24, 23]),
            Face([9, 11, 15, 13]),
            Face([1, 3, 7, 5]),
            Face([9, 11, 23, 21]),
            Face([17, 19, 23, 21]),
            Face([5, 7, 19, 17]),
            Face([10, 12, 16, 14]),
            Face([2, 4, 8, 6]),
            Face([10, 12, 24, 22]),
            Face([18, 20, 24, 22]),
            Face([6, 8, 20, 18]),
        ]

        super().__init__(vertices, faces)


if __name__ == "__main__":
    obj = ObjFile.from_path("hallway_high_quality.obj")
    point = ExclamationPoint()
    point.set_offset(Vertex(0, 0, 0), obj.get_offset())
    with open("hallway_high_quality.obj", "a") as f:
        f.write(str(point))
