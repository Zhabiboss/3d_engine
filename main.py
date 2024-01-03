import pygame
import sys
import math

pygame.init()
res = width, height = 1080, 720
screen = pygame.display.set_mode(res)
clock = pygame.time.Clock()
fps = 60
dt = lambda: 1 / clock.get_fps() if clock.get_fps() != 0 else 1 / fps
fov = 180
cx, cy, cz = 0, 0, 0
cax, cay = 0, 0

def project(x: float, y: float, z: float, scale = 100) -> tuple[float, float]:
    px = ((x * fov) / (z + fov)) * scale
    py = ((y * fov) / (z + fov)) * scale
    px = width / 2 + px
    py = height / 2 + py
    return px, py

def rotate_point_around_point(x1: float, y1: float, z1: float, x2: float, y2: float, z2: float, ax: float, ay: float):
    x_rotated = (x1 - x2) * math.cos(ay) + (z1 - z2) * math.sin(ay) + x2
    y_rotated = (y1 - y2) * math.cos(ax) - ((x1 - x2) * math.sin(ay) - (z1 - z2) * math.cos(ay)) * math.sin(ax) + y2
    z_rotated = (z1 - z2) * math.cos(ax) * math.cos(ay) - (x1 - x2) * math.cos(ax) * math.sin(ay) + (y1 - y2) * math.sin(ax) + z2
    return x_rotated, y_rotated, z_rotated

class Object:
    def __init__(self, verticies: list[tuple[int | float, int | float, int | float]], edges: list[tuple[int, int]], faces: list[tuple[int, int, int, int]], position: list[float, float, float]):
        self.verticies = verticies
        self.edges = edges
        self.faces = faces
        self.position = position
        self.ax: float = 0.0
        self.ay: float = 0.0
        self.az: float = 0.0

    def get_face_depth(self, face):
        return sum(self.rotate_vertex(self.verticies[vertex])[2] for vertex in face) / len(face)

    def draw(self):
        # Sort faces by depth
        sorted_faces = sorted(self.faces, key = self.get_face_depth, reverse = True)

        for face in sorted_faces:
            # Draw face
            polygon = [project(*self.rotate_vertex(self.verticies[vertex])) for vertex in face]
            pygame.draw.polygon(screen, (255, 0, 0), polygon)
            
            # Draw edges of the face
            num_vertices = len(face)
            for i in range(num_vertices):
                vertex1 = self.rotate_vertex(self.verticies[face[i]])
                vertex2 = self.rotate_vertex(self.verticies[face[(i + 1) % num_vertices]])
                pos1 = project(*vertex1)
                pos2 = project(*vertex2)
                pygame.draw.line(screen, (255, 255, 255), pos1, pos2)

    def rotate_vertex(self, vertex):
        x, y, z = vertex
        y_rotated = y * math.cos(self.ax) - z * math.sin(self.ax)
        z_rotated = y * math.sin(self.ax) + z * math.cos(self.ax)
        x_rotated = x * math.cos(self.ay) + z_rotated * math.sin(self.ay)
        z_rotated = -x * math.sin(self.ay) + z_rotated * math.cos(self.ay)
        return x_rotated + self.position[0], y_rotated + self.position[1], z_rotated + self.position[2]

class Cube(Object):
    def __init__(self, position):
        super().__init__([(-1, -1, -1), (1, -1, -1), (1, 1, -1), (-1, 1, -1), (-1, -1, 1), (1, -1, 1), (1, 1, 1), (-1, 1, 1)], 
                         [(0, 1), (1, 2), (2, 3), (3, 0), (4, 5), (5, 6), (6, 7), (7, 4), (0, 4), (1, 5), (2, 6), (3, 7)],
                         [[0, 1, 2, 3], [4, 5, 6, 7], [0, 1, 5, 4], [2, 3, 7, 6], [0, 3, 7, 4], [1, 2, 6, 5]], 
                         position)
        
cube = Cube((0, 0, 10))
cube_ = Cube((0, 30, 10)) 

pygame.event.set_grab(True)
pygame.mouse.set_visible(False)
pygame.mouse.set_pos(width // 2, height // 2)

while True:
    screen.fill((50, 50, 85))

    cube.draw()
    #cube_.draw()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()

        elif event.type == pygame.MOUSEMOTION:
            dx, dy = pygame.mouse.get_rel()
            cay -= dx * 0.01
            cax -= dy * 0.01
            cube.ay -= dx * 0.01
            #cube.ax -= dy * 0.01
            cube.position = rotate_point_around_point(cube.position[0], cube.position[1], cube.position[2],
                                                      cx, cy, cz, -dy * 0.01, -dx * 0.01)
            #cube_.ay += math.pi - dx * 0.01
            #cube_.ax += math.pi * 2 - dy * 0.01
            #cube_.position = rotate_point_around_point(cube_.position[0], cube_.position[1], cube_.position[2],
            #                                          cx, cy, cz, -dy * 0.005, -dx * 0.005)
    
    keys = pygame.key.get_pressed()
    cube.position = list(cube.position)
    if keys[pygame.K_w]:
        cube.position[2] -= math.cos(cay) * dt() * 100
        cube.position[1] -= math.sin(cay) * dt() * 100
    if keys[pygame.K_s]:
        cube.position[2] += math.cos(cay) * dt() * 100
        cube.position[1] += math.sin(cay) * dt() * 100
    if keys[pygame.K_a]:
        cube.position[2] -= math.sin(cay) * dt() * 100
        cube.position[1] += math.cos(cay) * dt() * 100
    if keys[pygame.K_d]:
        cube.position[2] += math.sin(cay) * dt() * 100
        cube.position[1] -= math.cos(cay) * dt() * 100
    cube.position = tuple(cube.position)

    pygame.display.update()
    clock.tick(fps)