from .vertex import Vertex
from .face import Face


class ObjFile:
    def __init__(self, vertices, faces):
        self.vertices = vertices
        self.faces = faces
        self.offset = 0

    def set_offset(self, position: Vertex, vertices_offset: int):
        self.offset = vertices_offset
        self.vertices = [vertex + position for vertex in self.vertices]
        for face in self.faces:
            face.offset(vertices_offset)

    def get_offset(self) -> int:
        return self.offset + len(self.vertices)

    def __str__(self) -> str:
        string = ""
        for vertex in self.vertices:
            string += vertex.as_line() + "\n"
        string += "\n"
        for face in self.faces:
            string += face.as_line() + "\n"
        string += "\n"
        return string

    @classmethod
    def from_path(cls, path: str):
        print(f"Creating object from file path: {path}")
        vertices = []
        faces = []
        with open(path) as f:
            for line in f:
                line_lst = line.split()
                if not line_lst:
                    continue
                if line_lst[0] == "v":
                    vertices.append(Vertex(float(line_lst[1]), float(line_lst[2]), float(line_lst[3])))
        return ObjFile(vertices, faces)
