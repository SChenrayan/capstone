class Face:
    def __init__(self, vertices):
        self.vertices = vertices

    def offset(self, offset: int):
        self.vertices = [vertex + offset for vertex in self.vertices]

    def as_line(self) -> str:
        string = "f"
        for vertex in self.vertices:
            string += f" {vertex}"
        return string
