import pygame
from pygame.locals import *

from shaders import *

from gl import Renderer, Model

width = 960
height = 540

deltaTime = 0.0

pygame.init()

screen = pygame.display.set_mode((width, height), pygame.OPENGL | pygame.DOUBLEBUF)
clock = pygame.time.Clock()

rend = Renderer(screen)

rend.setShaders(vertex_shader, fragment_shader)

face = Model("model.obj")

face.position.z -= 10

rend.scene.append( face )


isRunning = True

while isRunning:

    keys = pygame.key.get_pressed()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            isRunning = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                isRunning = False


    if keys[K_LEFT]:
        rend.camPosition.x -= 10 * deltaTime

    elif keys[K_RIGHT]:
        rend.camPosition.x += 10 * deltaTime

    deltaTime = clock.tick(60) / 1000
    #print(deltaTime)

    rend.update()
    rend.render()
    pygame.display.flip()

pygame.quit()