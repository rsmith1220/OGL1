import glm #pip install PyGLM

from numpy import array, float32

# pip install PyOpenGL
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader

from obj import Obj


class Model(object):
    def __init__(self, objName):
        self.model = Obj(objName)

        self.createVertexBuffer()

        self.position = glm.vec3(0,0,0)
        self.rotation = glm.vec3(0,0,0)
        self.scale = glm.vec3(1,1,1)


    def createVertexBuffer(self):
        buffer = []

        self.polycount = 0

        for face in self.model.faces:
            self.polycount += 1

            for i in range(3):
                # positions
                pos = self.model.vertices[face[i][0] - 1]
                buffer.append(pos[0])
                buffer.append(pos[1])
                buffer.append(pos[2])

                # texcoords
                uvs = self.model.texcoords[face[i][1] - 1]
                buffer.append(uvs[0])
                buffer.append(uvs[1])

                # normals
                norm = self.model.normals[face[i][2] - 1]
                buffer.append(norm[0])
                buffer.append(norm[1])
                buffer.append(norm[2])

            if len(face) == 4:

                self.polycount += 1

                for i in [0,2,3]:
                    # positions
                    pos = self.model.vertices[face[i][0] - 1]
                    buffer.append(pos[0])
                    buffer.append(pos[1])
                    buffer.append(pos[2])

                    # texcoords
                    uvs = self.model.texcoords[face[i][1] - 1]
                    buffer.append(uvs[0])
                    buffer.append(uvs[1])

                    # normals
                    norm = self.model.normals[face[i][2] - 1]
                    buffer.append(norm[0])
                    buffer.append(norm[1])
                    buffer.append(norm[2])


        self.vertBuffer = array(buffer, dtype = float32)
        
        # Vertex Buffer Object
        self.VBO = glGenBuffers(1)
        # Vertex Array Object
        self.VAO = glGenVertexArrays(1)

    def getModelMatrix(self):
        identity = glm.mat4(1)

        translateMat = glm.translate(identity, self.position)

        pitch = glm.rotate(identity, glm.radians(self.rotation.x), glm.vec3(1,0,0))
        yaw   = glm.rotate(identity, glm.radians(self.rotation.y), glm.vec3(0,1,0))
        roll  = glm.rotate(identity, glm.radians(self.rotation.z), glm.vec3(0,0,1))

        rotationMat = pitch * yaw * roll

        scaleMat = glm.scale(identity, self.scale)

        return translateMat * rotationMat * scaleMat

    def render(self):

        glBindBuffer(GL_ARRAY_BUFFER, self.VBO)
        glBindVertexArray(self.VAO)

        # Mandar la informacion de vertices
        glBufferData(GL_ARRAY_BUFFER,           # Buffer ID
                     self.vertBuffer.nbytes,    # Buffer size in bytes
                     self.vertBuffer,           # Buffer data
                     GL_STATIC_DRAW)            # Usage

        # Atributos

        # Atributo de posiciones
        glVertexAttribPointer(0,                # Attribute number
                              3,                # Size
                              GL_FLOAT,         # Type
                              GL_FALSE,         # Is it normalized
                              4 * 8,            # Stride
                              ctypes.c_void_p(0))# Offset

        glEnableVertexAttribArray(0)

        # Atributo de texcoords
        glVertexAttribPointer(1,                # Attribute number
                              2,                # Size
                              GL_FLOAT,         # Type
                              GL_FALSE,         # Is it normalized
                              4 * 8,            # Stride
                              ctypes.c_void_p(4*3))# Offset

        glEnableVertexAttribArray(1)

        # Atributo de normals
        glVertexAttribPointer(2,                # Attribute number
                              3,                # Size
                              GL_FLOAT,         # Type
                              GL_FALSE,         # Is it normalized
                              4 * 8,            # Stride
                              ctypes.c_void_p(4*5))# Offset

        glEnableVertexAttribArray(2)

        glDrawArrays(GL_TRIANGLES, 0, self.polycount * 3 )


class Renderer(object):
    def __init__(self, screen):
        self.screen = screen
        _, _, self.width, self.height = screen.get_rect()

        glEnable(GL_DEPTH_TEST)
        glViewport(0,0, self.width, self.height)

        self.scene = []
        self.active_shader = None

        # ViewMatrix
        self.camPosition = glm.vec3(0,0,0)
        self.camRotation = glm.vec3(0,0,0)
        self.viewMatrix = self.getViewMatrix()

        # Projection Matrix
        self.projectionMatrix = glm.perspective(glm.radians(60),        # FOV
                                                self.width/self.height, # Aspect Ratio
                                                0.1,                    # Near Plane
                                                1000)                   # Far Plane
        

    def getViewMatrix(self):
        identity = glm.mat4(1)

        translateMat = glm.translate(identity, self.camPosition)

        pitch = glm.rotate(identity, glm.radians(self.camRotation.x), glm.vec3(1,0,0))
        yaw   = glm.rotate(identity, glm.radians(self.camRotation.y), glm.vec3(0,1,0))
        roll  = glm.rotate(identity, glm.radians(self.camRotation.z), glm.vec3(0,0,1))

        rotationMat = pitch * yaw * roll

        camMatrix = translateMat * rotationMat

        return glm.inverse(camMatrix)


    def setShaders(self, vertexShader, fragmentShader):
        if vertexShader is not None and fragmentShader is not None:
            self.active_shader = compileProgram( compileShader(vertexShader, GL_VERTEX_SHADER),
                                                 compileShader(fragmentShader, GL_FRAGMENT_SHADER))
        else:
            self.active_shader = None

    def update(self):
        self.viewMatrix = self.getViewMatrix()

    def render(self):
        glClearColor(0.2,0.2,0.2, 1)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        if self.active_shader is not None:
            glUseProgram(self.active_shader)

            glUniformMatrix4fv( glGetUniformLocation(self.active_shader, "viewMatrix"),
                                1, GL_FALSE, glm.value_ptr(self.viewMatrix))

            glUniformMatrix4fv( glGetUniformLocation(self.active_shader, "projectionMatrix"),
                                1, GL_FALSE, glm.value_ptr(self.projectionMatrix))


        for obj in self.scene:
            if self.active_shader is not None:
                glUniformMatrix4fv( glGetUniformLocation(self.active_shader, "modelMatrix"),
                                    1, GL_FALSE, glm.value_ptr(obj.getModelMatrix()))


            obj.render()