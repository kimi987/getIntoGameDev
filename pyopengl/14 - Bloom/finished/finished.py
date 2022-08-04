import pygame as pg
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram,compileShader
import numpy as np
import pyrr
import math

####################### Model #################################################

class SimpleComponent:


    def __init__(self, position, eulers):

        self.position = np.array(position, dtype=np.float32)
        self.eulers = np.array(eulers, dtype=np.float32)
        self.modelTransform = pyrr.matrix44.create_identity(dtype=np.float32)
    
    def update(self):
        
        self.modelTransform = pyrr.matrix44.create_identity(dtype=np.float32)
        self.modelTransform = pyrr.matrix44.multiply(
            m1=self.modelTransform, 
            m2=pyrr.matrix44.create_from_eulers(
                eulers=np.radians(self.eulers), dtype=np.float32
            )
        )
        self.modelTransform = pyrr.matrix44.multiply(
            m1=self.modelTransform, 
            m2=pyrr.matrix44.create_from_translation(
                vec=np.array(self.position),dtype=np.float32
            )
        )
        
class BillBoardComponent:

    def __init__(self, position):

        self.position = np.array(position, dtype=np.float32)
        self.modelTransform = pyrr.matrix44.create_identity(dtype=np.float32)
    
    def update(self, playerPosition):
        
        directionFromPlayer = self.position - playerPosition
        angle1 = np.arctan2(-directionFromPlayer[1],directionFromPlayer[0])
        dist2d = math.sqrt(directionFromPlayer[0] ** 2 + directionFromPlayer[1] ** 2)
        angle2 = np.arctan2(directionFromPlayer[2],dist2d)

        self.modelTransform = pyrr.matrix44.create_identity(dtype=np.float32)
        self.modelTransform = pyrr.matrix44.multiply(
            self.modelTransform,
            pyrr.matrix44.create_from_y_rotation(theta=angle2, dtype=np.float32)
        )
        self.modelTransform = pyrr.matrix44.multiply(
           self.modelTransform,
            pyrr.matrix44.create_from_z_rotation(theta=angle1, dtype=np.float32)
        )
        self.modelTransform = pyrr.matrix44.multiply(
            self.modelTransform,
            pyrr.matrix44.create_from_translation(self.position,dtype=np.float32)
        )

class BrightBillboard:


    def __init__(self, position, color, strength):

        self.position = np.array(position, dtype=np.float32)
        self.modelTransform = pyrr.matrix44.create_identity(dtype=np.float32)
        self.color = np.array(color, dtype=np.float32)
        self.strength = strength
    
    def update(self, playerPosition):
        
        directionFromPlayer = self.position - playerPosition
        angle1 = np.arctan2(-directionFromPlayer[1],directionFromPlayer[0])
        dist2d = math.sqrt(directionFromPlayer[0] ** 2 + directionFromPlayer[1] ** 2)
        angle2 = np.arctan2(directionFromPlayer[2],dist2d)

        self.modelTransform = pyrr.matrix44.create_identity(dtype=np.float32)
        self.modelTransform = pyrr.matrix44.multiply(
            self.modelTransform,
            pyrr.matrix44.create_from_y_rotation(theta=angle2, dtype=np.float32)
        )
        self.modelTransform = pyrr.matrix44.multiply(
           self.modelTransform,
            pyrr.matrix44.create_from_z_rotation(theta=angle1, dtype=np.float32)
        )
        self.modelTransform = pyrr.matrix44.multiply(
            self.modelTransform,
            pyrr.matrix44.create_from_translation(self.position,dtype=np.float32)
        )

class Player:


    def __init__(self, position):

        self.position = np.array(position, dtype = np.float32)
        self.theta = 0
        self.phi = 0
        self.update_vectors()
    
    def update_vectors(self):

        self.modelTransform = pyrr.matrix44.create_identity(dtype=np.float32)
        self.modelTransform = pyrr.matrix44.multiply(
            m1=self.modelTransform, 
            m2=pyrr.matrix44.create_from_x_rotation(
                theta=np.radians(self.phi), dtype=np.float32
            )
        )
        self.modelTransform = pyrr.matrix44.multiply(
            m1=self.modelTransform, 
            m2=pyrr.matrix44.create_from_z_rotation(
                theta=np.radians(270 - self.theta), dtype=np.float32
            )
        )
        self.modelTransform = pyrr.matrix44.multiply(
            m1=self.modelTransform, 
            m2=pyrr.matrix44.create_from_translation(
                vec=np.array(self.position),dtype=np.float32
            )
        )

        self.forwards = np.array(
            [
                np.cos(np.deg2rad(self.theta)) * np.cos(np.deg2rad(self.phi)),
                np.sin(np.deg2rad(self.theta)) * np.cos(np.deg2rad(self.phi)),
                np.sin(np.deg2rad(self.phi))
            ],
            dtype = np.float32
        )

        globalUp = np.array([0,0,1], dtype=np.float32)

        self.right = np.cross(self.forwards, globalUp)

        self.up = np.cross(self.right, self.forwards)

        self.viewTransform = pyrr.matrix44.create_look_at(
            eye = self.position,
            target = self.position + self.forwards,
            up = self.up, 
            dtype = np.float32
        )

class Reflector:


    def __init__(self, position, eulers):

        self.position = np.array(position, dtype=np.float32)
        self.eulers = np.array(eulers, dtype=np.float32)
        self.modelTransform = pyrr.matrix44.create_identity(dtype=np.float32)
    
    def update(self, camera_pos):
        
        self.modelTransform = pyrr.matrix44.create_identity(dtype=np.float32)
        self.modelTransform = pyrr.matrix44.multiply(
            m1=self.modelTransform, 
            m2=pyrr.matrix44.create_from_eulers(
                eulers=np.radians(self.eulers), dtype=np.float32
            )
        )
        self.modelTransform = pyrr.matrix44.multiply(
            m1=self.modelTransform, 
            m2=pyrr.matrix44.create_from_translation(
                vec=np.array(self.position),dtype=np.float32
            )
        )

        
        phi = self.eulers[1]
        theta = self.eulers[2] - 180

        self.forwards = np.array(
            [
                np.cos(np.deg2rad(theta)) * np.cos(np.deg2rad(phi)),
                np.sin(np.deg2rad(theta)) * np.cos(np.deg2rad(phi)),
                np.sin(np.deg2rad(phi))
            ],
            dtype = np.float32
        )
        incident_direction = self.position - camera_pos
        self.forwards = pyrr.vector.normalize(incident_direction - 2 * np.dot(incident_direction, self.forwards) * self.forwards)

        globalUp = np.array([0,0,1], dtype=np.float32)

        self.right = np.cross(self.forwards, globalUp)

        self.up = np.cross(self.right, self.forwards)

        self.viewTransform = pyrr.matrix44.create_look_at(
            eye = self.position,
            target = self.position + self.forwards,
            up = self.up, 
            dtype = np.float32
        )

class Scene:


    def __init__(self):

        self.cubes = [
            SimpleComponent(
                position = [-5,0,1],
                eulers = [0,0,0]
            ),
        ]

        self.medkits = [
            BillBoardComponent(
                position = [3,0,0.5]
            )
        ]

        self.containers = [
            SimpleComponent(
                position = [0,0,0],
                eulers = [0,0,0]
            ),
        ]

        self.mirrors = [
            Reflector(
                position = [9.8, 0, 2],
                eulers = [0,0,0]
            ),
        ]

        self.lights = [
            BrightBillboard(
                position = [
                    4.0, 
                    -4.0 + i, 
                    1.0
                ],
                color = [
                    np.random.uniform(low=0.0, high=1.0), 
                    np.random.uniform(low=0.0, high=1.0), 
                    np.random.uniform(low=0.0, high=1.0)
                ],
                strength = 3
            )
            for i in range(8)
        ]

        self.player = Player(
            position = [0,0,2]
        )

    def update(self, rate):

        for cube in self.cubes:
            cube.update()
        
        for medkit in self.medkits:
            medkit.update(self.player.position)

        for light in self.lights:
            light.update(self.player.position)

        for container in self.containers:
            container.update()

        for mirror in self.mirrors:
            mirror.update(self.player.position)
        
        self.player.update_vectors()
    
    def move_player(self, dPos):

        dPos = 0.4 * np.array(dPos, dtype = np.float32)
        self.player.position += dPos
    
    def spin_player(self, dTheta, dPhi):

        self.player.theta += 0.4 * dTheta
        if self.player.theta > 360:
            self.player.theta -= 360
        elif self.player.theta < 0:
            self.player.theta += 360
        
        self.player.phi = min(
            89, max(-89, self.player.phi + 0.4 * dPhi)
        )

####################### Control ###############################################

class App:


    def __init__(self, screenWidth, screenHeight):

        self.screenWidth = screenWidth
        self.screenHeight = screenHeight

        self.renderer = GraphicsEngine(screenWidth, screenHeight)

        self.scene = Scene()

        self.lastTime = pg.time.get_ticks()
        self.currentTime = 0
        self.numFrames = 0
        self.frameTime = 0

        self.mainLoop()

    def mainLoop(self):
        running = True
        while (running):
            #check events
            for event in pg.event.get():
                if (event.type == pg.QUIT):
                    running = False
                elif event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE:
                        running = False
            
            self.handleKeys()
            self.handleMouse()

            self.scene.update(self.frameTime * 0.05)
            
            self.renderer.render(self.scene)

            #timing
            self.calculateFramerate()
        self.quit()

    def handleKeys(self):

        keys = pg.key.get_pressed()
        combo = 0
        directionModifier = 0
        """
        w: 1 -> 0 degrees
        a: 2 -> 90 degrees
        w & a: 3 -> 45 degrees
        s: 4 -> 180 degrees
        w & s: 5 -> x
        a & s: 6 -> 135 degrees
        w & a & s: 7 -> 90 degrees
        d: 8 -> 270 degrees
        w & d: 9 -> 315 degrees
        a & d: 10 -> x
        w & a & d: 11 -> 0 degrees
        s & d: 12 -> 225 degrees
        w & s & d: 13 -> 270 degrees
        a & s & d: 14 -> 180 degrees
        w & a & s & d: 15 -> x
        """

        if keys[pg.K_w]:
            combo += 1
        if keys[pg.K_a]:
            combo += 2
        if keys[pg.K_s]:
            combo += 4
        if keys[pg.K_d]:
            combo += 8
        
        if combo > 0:
            if combo == 3:
                directionModifier = 45
            elif combo == 2 or combo == 7:
                directionModifier = 90
            elif combo == 6:
                directionModifier = 135
            elif combo == 4 or combo == 14:
                directionModifier = 180
            elif combo == 12:
                directionModifier = 225
            elif combo == 8 or combo == 13:
                directionModifier = 270
            elif combo == 9:
                directionModifier = 315
            
            dPos = [
                self.frameTime * 0.025 * np.cos(np.deg2rad(self.scene.player.theta + directionModifier)),
                self.frameTime * 0.025 * np.sin(np.deg2rad(self.scene.player.theta + directionModifier)),
                0
            ]

            self.scene.move_player(dPos)

    def handleMouse(self):

        (x,y) = pg.mouse.get_pos()
        theta_increment = self.frameTime * 0.05 * ((self.screenWidth // 2) - x)
        phi_increment = self.frameTime * 0.05 * ((self.screenHeight // 2) - y)
        self.scene.spin_player(theta_increment, phi_increment)
        pg.mouse.set_pos((self.screenWidth // 2,self.screenHeight // 2))

    def calculateFramerate(self):

        self.currentTime = pg.time.get_ticks()
        delta = self.currentTime - self.lastTime
        if (delta >= 1000):
            framerate = max(1,int(1000.0 * self.numFrames/delta))
            #pg.display.set_caption(f"Running at {framerate} fps.")
            self.renderer.update_fps(framerate)
            self.lastTime = self.currentTime
            self.numFrames = -1
            self.frameTime = float(1000.0 / max(1,framerate))
        self.numFrames += 1

    def quit(self):
        
        self.renderer.destroy()

####################### View  #################################################

class GraphicsEngine:


    def __init__(self, screenWidth, screenHeight):

        self.screenWidth = screenWidth
        self.screenHeight = screenHeight

        #initialise pygame
        pg.init()
        pg.mouse.set_visible(False)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MAJOR_VERSION, 3)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MINOR_VERSION, 3)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_PROFILE_MASK,
                                    pg.GL_CONTEXT_PROFILE_CORE)
        pg.display.set_mode((self.screenWidth,self.screenHeight), pg.OPENGL|pg.DOUBLEBUF)

        #initialise opengl
        glClearColor(0.0, 0.0, 0.0, 1)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        self.create_framebuffers()

        self.create_assets()

        self.setup_shaders()

        self.query_shader_locations()
    
    def create_framebuffers(self):
        self.fbos = []
        self.colorBuffers = []
        self.depthStencilBuffers = []
        for i in range(2):
            self.fbos.append(glGenFramebuffers(1))
            glBindFramebuffer(GL_FRAMEBUFFER, self.fbos[i])
        
            new_color_buffer_0 = glGenTextures(1)
            glBindTexture(GL_TEXTURE_2D, new_color_buffer_0)
            glTexImage2D(
                GL_TEXTURE_2D, 0, GL_RGB, 
                self.screenWidth, self.screenHeight,
                0, GL_RGB, GL_UNSIGNED_BYTE, None
            )
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_BORDER)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_BORDER)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
            glBindTexture(GL_TEXTURE_2D, 0)
            glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, 
                                    GL_TEXTURE_2D, new_color_buffer_0, 0)
            
            new_color_buffer_1 = glGenTextures(1)
            glBindTexture(GL_TEXTURE_2D, new_color_buffer_1)
            glTexImage2D(
                GL_TEXTURE_2D, 0, GL_RGB, 
                self.screenWidth, self.screenHeight,
                0, GL_RGB, GL_UNSIGNED_BYTE, None
            )
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_BORDER)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_BORDER)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
            glBindTexture(GL_TEXTURE_2D, 0)
            glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT1, 
                                    GL_TEXTURE_2D, new_color_buffer_1, 0)
            
            self.colorBuffers.append([new_color_buffer_0, new_color_buffer_1])
            
            self.depthStencilBuffers.append(glGenRenderbuffers(1))
            glBindRenderbuffer(GL_RENDERBUFFER, self.depthStencilBuffers[i])
            glRenderbufferStorage(
                GL_RENDERBUFFER, GL_DEPTH24_STENCIL8, self.screenWidth, self.screenHeight
            )
            glBindRenderbuffer(GL_RENDERBUFFER,0)
            glFramebufferRenderbuffer(GL_FRAMEBUFFER, GL_DEPTH_STENCIL_ATTACHMENT, 
                                        GL_RENDERBUFFER, self.depthStencilBuffers[i])

            glBindFramebuffer(GL_FRAMEBUFFER, 0)
    
    def setup_shaders(self):

        projection_transform = pyrr.matrix44.create_perspective_projection(
            fovy = 45, aspect = self.screenWidth/self.screenHeight, 
            near = 0.1, far = 50, dtype=np.float32
        )

        self.lighting_shader = self.createShader("shaders/vertex.txt", "shaders/fragment.txt")
        glUseProgram(self.lighting_shader)
        glUniformMatrix4fv(
            glGetUniformLocation(self.lighting_shader,"projection"),
            1, GL_FALSE, projection_transform
        )
        glUniform1i(glGetUniformLocation(self.lighting_shader, "material.albedo"), 0)
        glUniform1i(glGetUniformLocation(self.lighting_shader, "material.ao"), 1)
        glUniform1i(glGetUniformLocation(self.lighting_shader, "material.specular"), 2)
        glUniform1i(glGetUniformLocation(self.lighting_shader, "material.normal"), 3)
        glUniform1i(glGetUniformLocation(self.lighting_shader, "bright_material"), 4)

        self.unlit_shader = self.createShader("shaders/vertex_light.txt", "shaders/fragment_light.txt")
        glUseProgram(self.unlit_shader)
        glUniformMatrix4fv(
            glGetUniformLocation(self.unlit_shader,"projection"),
            1, GL_FALSE, projection_transform
        )
        glUniform1i(glGetUniformLocation(self.unlit_shader, "imageTexture"), 0)
        glUniform1i(glGetUniformLocation(self.unlit_shader, "bright_material"), 1)

        self.post_shader = self.createShader("shaders/simple_post_vertex.txt", "shaders/post_fragment.txt")

        self.crt_shader = self.createShader("shaders/simple_post_vertex.txt", "shaders/crt_fragment.txt")

        self.screen_shader = self.createShader("shaders/simple_post_vertex.txt", "shaders/screen_fragment.txt")
        glUseProgram(self.screen_shader)
        glUniform1i(glGetUniformLocation(self.screen_shader, "material"), 0)
        glUniform1i(glGetUniformLocation(self.screen_shader, "bright_material"), 1)

        self.bloom_blur_shader = self.createShader("shaders/simple_post_vertex.txt", "shaders/bloom_blur_fragment.txt")
        glUseProgram(self.bloom_blur_shader)
        glUniform1i(glGetUniformLocation(self.bloom_blur_shader, "material"), 0)
        glUniform1i(glGetUniformLocation(self.bloom_blur_shader, "bright_material"), 1)

        self.bloom_transfer_shader = self.createShader("shaders/simple_post_vertex.txt", "shaders/bloom_transfer_fragment.txt")
        glUseProgram(self.bloom_transfer_shader)
        glUniform1i(glGetUniformLocation(self.bloom_transfer_shader, "material"), 0)
        glUniform1i(glGetUniformLocation(self.bloom_transfer_shader, "bright_material"), 1)

        self.bloom_resolve_shader = self.createShader("shaders/simple_post_vertex.txt", "shaders/bloom_resolve_fragment.txt")
        glUseProgram(self.bloom_resolve_shader)
        glUniform1i(glGetUniformLocation(self.bloom_resolve_shader, "material"), 0)
        glUniform1i(glGetUniformLocation(self.bloom_resolve_shader, "bright_material"), 1)

    def query_shader_locations(self):

        #attributes shared by both shaders
        self.modelMatrixLocation = {}
        self.viewMatrixLocation = {}
        self.tintLoc = {}

        glUseProgram(self.lighting_shader)
        self.modelMatrixLocation["lit"] = glGetUniformLocation(self.lighting_shader, "model")
        self.viewMatrixLocation["lit"] = glGetUniformLocation(self.lighting_shader, "view")
        self.lightLocation = {
            "position": [
                glGetUniformLocation(self.lighting_shader, f"lightPos[{i}]")
                for i in range(8)
            ],
            "color": [
                glGetUniformLocation(self.lighting_shader, f"lights[{i}].color")
                for i in range(8)
            ],
            "strength": [
                glGetUniformLocation(self.lighting_shader, f"lights[{i}].strength")
                for i in range(8)
            ]
        }
        self.cameraPosLoc = glGetUniformLocation(self.lighting_shader, "viewPos")

        glUseProgram(self.unlit_shader)
        self.modelMatrixLocation["unlit"] = glGetUniformLocation(self.unlit_shader, "model")
        self.viewMatrixLocation["unlit"] = glGetUniformLocation(self.unlit_shader, "view")
        self.tintLoc["unlit"] = glGetUniformLocation(self.unlit_shader, "tint")

        glUseProgram(self.screen_shader)
        self.tintLoc["screen"] = glGetUniformLocation(self.screen_shader, "tint")

    def create_assets(self):

        self.wood_texture = AdvancedMaterial("wood")
        self.cube_mesh = Mesh("models/cube.obj")
        self.medkit_texture = AdvancedMaterial("medkit")
        self.medkit_billboard = BillBoard(w = 0.6, h = 0.5)
        self.container_mesh = Mesh("models/container.obj")
        self.monkey_mesh = Mesh("models/monkey.obj")

        self.light_texture = Material("gfx/greenlight.png")
        self.light_billboard = BillBoard(w = 0.2, h = 0.1)
        self.mirror_mesh = BillBoard(w = 2.0, h = 2.0)

        self.screen = TexturedQuad(0, 0, 1, 1)

        self.font = Font()
        self.fps_label = TextLine("FPS: ", self.font, (-0.9, 0.9), (0.05, 0.05))
    
    def createShader(self, vertexFilepath, fragmentFilepath):

        with open(vertexFilepath,'r') as f:
            vertex_src = f.readlines()

        with open(fragmentFilepath,'r') as f:
            fragment_src = f.readlines()
        
        shader = compileProgram(compileShader(vertex_src, GL_VERTEX_SHADER),
                                compileShader(fragment_src, GL_FRAGMENT_SHADER),
                            )
        
        return shader

    def update_fps(self, new_fps):

        self.fps_label.build_text(f"FPS: {new_fps}", self.font)
    
    def render_external(self, scene, mirror):
        #First pass
        glBindFramebuffer(GL_FRAMEBUFFER, self.fbos[1])
        glDrawBuffers(2, (GL_COLOR_ATTACHMENT0, GL_COLOR_ATTACHMENT1))
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glEnable(GL_DEPTH_TEST)
        
        #lit shader
        glUseProgram(self.lighting_shader)

        glUniformMatrix4fv(self.viewMatrixLocation["lit"], 1, GL_FALSE, mirror.viewTransform)

        glUniform3fv(self.cameraPosLoc, 1, mirror.position)

        for i,light in enumerate(scene.lights):
            glUniform3fv(self.lightLocation["position"][i], 1, light.position)
            glUniform3fv(self.lightLocation["color"][i], 1, light.color)
            glUniform1f(self.lightLocation["strength"][i], light.strength)
        
        self.wood_texture.use()
        glBindVertexArray(self.monkey_mesh.vao)
        glUniformMatrix4fv(self.modelMatrixLocation["lit"],1,GL_FALSE,scene.player.modelTransform)
        glDrawArrays(GL_TRIANGLES, 0, self.monkey_mesh.vertex_count)
        
        
        self.wood_texture.use()
        glBindVertexArray(self.cube_mesh.vao)
        for cube in scene.cubes:
            glUniformMatrix4fv(self.modelMatrixLocation["lit"],1,GL_FALSE,cube.modelTransform)
            glDrawArrays(GL_TRIANGLES, 0, self.cube_mesh.vertex_count)
        

        glBindVertexArray(self.container_mesh.vao)
        for container in scene.containers:
            glUniformMatrix4fv(self.modelMatrixLocation["lit"],1,GL_FALSE,container.modelTransform)
            glDrawArrays(GL_TRIANGLES, 0, self.container_mesh.vertex_count)
        
        self.medkit_texture.use()
        glBindVertexArray(self.medkit_billboard.vao)
        for medkit in scene.medkits:
            glUniformMatrix4fv(self.modelMatrixLocation["lit"],1,GL_FALSE,medkit.modelTransform)
            glDrawArrays(GL_TRIANGLES, 0, self.medkit_billboard.vertexCount)

        #unlit shader
        glUseProgram(self.unlit_shader)

        glUniformMatrix4fv(self.viewMatrixLocation["unlit"], 1, GL_FALSE, mirror.viewTransform)

        self.light_texture.use()
        glBindVertexArray(self.light_billboard.vao)
        for i,light in enumerate(scene.lights):

            glUniform3fv(self.tintLoc["unlit"], 1, light.color)
            glUniformMatrix4fv(self.modelMatrixLocation["unlit"],1,GL_FALSE,light.modelTransform)
            glDrawArrays(GL_TRIANGLES, 0, self.light_billboard.vertexCount)
        
    def render_internal(self, scene):
        #First pass
        glBindFramebuffer(GL_FRAMEBUFFER, self.fbos[0])
        glDrawBuffers(2, (GL_COLOR_ATTACHMENT0, GL_COLOR_ATTACHMENT1))
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glEnable(GL_DEPTH_TEST)
        
        #lit shader
        glUseProgram(self.lighting_shader)

        glUniformMatrix4fv(self.viewMatrixLocation["lit"], 1, GL_FALSE, scene.player.viewTransform)

        glUniform3fv(self.cameraPosLoc, 1, scene.player.position)

        for i,light in enumerate(scene.lights):
            glUniform3fv(self.lightLocation["position"][i], 1, light.position)
            glUniform3fv(self.lightLocation["color"][i], 1, light.color)
            glUniform1f(self.lightLocation["strength"][i], light.strength)

        self.wood_texture.use()
        glBindVertexArray(self.cube_mesh.vao)
        for cube in scene.cubes:
            glUniformMatrix4fv(self.modelMatrixLocation["lit"],1,GL_FALSE,cube.modelTransform)
            glDrawArrays(GL_TRIANGLES, 0, self.cube_mesh.vertex_count)
        
        glBindVertexArray(self.container_mesh.vao)
        for container in scene.containers:
            glUniformMatrix4fv(self.modelMatrixLocation["lit"],1,GL_FALSE,container.modelTransform)
            glDrawArrays(GL_TRIANGLES, 0, self.container_mesh.vertex_count)
        
        self.medkit_texture.use()
        glBindVertexArray(self.medkit_billboard.vao)
        for medkit in scene.medkits:
            glUniformMatrix4fv(self.modelMatrixLocation["lit"],1,GL_FALSE,medkit.modelTransform)
            glDrawArrays(GL_TRIANGLES, 0, self.medkit_billboard.vertexCount)
        
        #unlit shader
        glUseProgram(self.unlit_shader)

        glUniformMatrix4fv(self.viewMatrixLocation["unlit"], 1, GL_FALSE, scene.player.viewTransform)

        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, self.colorBuffers[1][0])
        glActiveTexture(GL_TEXTURE1)
        glBindTexture(GL_TEXTURE_2D, self.colorBuffers[1][1])
        glBindVertexArray(self.mirror_mesh.vao)
        glUniform3fv(self.tintLoc["unlit"], 1, np.array([1,1,1], dtype=np.float32))
        for mirror in scene.mirrors:
            glUniformMatrix4fv(self.modelMatrixLocation["unlit"],1,GL_FALSE,mirror.modelTransform)
            glDrawArrays(GL_TRIANGLES, 0, self.mirror_mesh.vertexCount)
        
        
        self.light_texture.use()
        glBindVertexArray(self.light_billboard.vao)
        for i,light in enumerate(scene.lights):

            glUniform3fv(self.tintLoc["unlit"], 1, light.color)
            glUniformMatrix4fv(self.modelMatrixLocation["unlit"],1,GL_FALSE,light.modelTransform)
            glDrawArrays(GL_TRIANGLES, 0, self.light_billboard.vertexCount)
        
    def render(self, scene):
        
        for mirror in scene.mirrors:
            self.render_external(scene, mirror)
        
        self.render_internal(scene)

        #Post processing pass
        glUseProgram(self.screen_shader)
        glBindFramebuffer(GL_FRAMEBUFFER, self.fbos[0])
        glDrawBuffers(2, (GL_COLOR_ATTACHMENT0, GL_COLOR_ATTACHMENT1))
        glDisable(GL_DEPTH_TEST)

        glUniform4fv(self.tintLoc["screen"], 1, np.array([1.0, 0.0, 0.0, 1.0], dtype = np.float32))
        self.font.use()
        glBindVertexArray(self.fps_label.vao)
        glDrawArrays(GL_TRIANGLES, 0, self.fps_label.vertex_count)
        
        #Bloom
        for _ in range(8):

            glBindFramebuffer(GL_FRAMEBUFFER, self.fbos[1])
            glDrawBuffers(1, (GL_COLOR_ATTACHMENT1,))
            glDisable(GL_DEPTH_TEST)
            glUseProgram(self.bloom_blur_shader)
            glActiveTexture(GL_TEXTURE0)
            glBindTexture(GL_TEXTURE_2D, self.colorBuffers[0][0])
            glActiveTexture(GL_TEXTURE1)
            glBindTexture(GL_TEXTURE_2D, self.colorBuffers[0][1])
            glBindVertexArray(self.screen.vao)
            glDrawArrays(GL_TRIANGLES, 0, self.screen.vertex_count)

            glBindFramebuffer(GL_FRAMEBUFFER, self.fbos[0])
            glDrawBuffers(1, (GL_COLOR_ATTACHMENT1,))
            glDisable(GL_DEPTH_TEST)
            glUseProgram(self.bloom_transfer_shader)
            glActiveTexture(GL_TEXTURE0)
            glBindTexture(GL_TEXTURE_2D, self.colorBuffers[1][0])
            glActiveTexture(GL_TEXTURE1)
            glBindTexture(GL_TEXTURE_2D, self.colorBuffers[1][1])
            glBindVertexArray(self.screen.vao)
            glDrawArrays(GL_TRIANGLES, 0, self.screen.vertex_count)
        glBindFramebuffer(GL_FRAMEBUFFER, self.fbos[1])
        glDrawBuffers(1, (GL_COLOR_ATTACHMENT0,))
        glUseProgram(self.bloom_resolve_shader)
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, self.colorBuffers[0][0])
        glActiveTexture(GL_TEXTURE1)
        glBindTexture(GL_TEXTURE_2D, self.colorBuffers[0][1])
        glBindVertexArray(self.screen.vao)
        glDrawArrays(GL_TRIANGLES, 0, self.screen.vertex_count)
        
        #CRT emulation pass
        
        glUseProgram(self.crt_shader)
        glBindFramebuffer(GL_FRAMEBUFFER, self.fbos[0])
        glDrawBuffers(1, (GL_COLOR_ATTACHMENT0,))
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glDisable(GL_DEPTH_TEST)

        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, self.colorBuffers[1][0])
        glBindVertexArray(self.screen.vao)
        glDrawArrays(GL_TRIANGLES, 0, self.screen.vertex_count)
        

        #Put the final result on screen
        glUseProgram(self.screen_shader)
        glBindFramebuffer(GL_FRAMEBUFFER, 0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glDisable(GL_DEPTH_TEST)

        glUniform4fv(self.tintLoc["screen"], 1, np.array([1.0, 1.0, 1.0, 1.0], dtype = np.float32))
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, self.colorBuffers[0][0])
        glActiveTexture(GL_TEXTURE1)
        glBindTexture(GL_TEXTURE_2D, self.colorBuffers[0][1])
        glBindVertexArray(self.screen.vao)
        glDrawArrays(GL_TRIANGLES, 0, self.screen.vertex_count)

        pg.display.flip()

    def destroy(self):

        self.cube_mesh.destroy()
        self.wood_texture.destroy()
        self.medkit_billboard.destroy()
        self.medkit_texture.destroy()
        self.light_billboard.destroy()
        self.light_texture.destroy()
        self.mirror_mesh.destroy()
        self.font.destroy()
        self.fps_label.destroy()
        glDeleteProgram(self.lighting_shader)
        glDeleteProgram(self.unlit_shader)
        glDeleteProgram(self.post_shader)
        glDeleteProgram(self.crt_shader)
        glDeleteProgram(self.screen_shader)
        glDeleteProgram(self.bloom_blur_shader)
        glDeleteProgram(self.bloom_transfer_shader)
        glDeleteProgram(self.bloom_resolve_shader)
        glDeleteTextures(len(self.colorBuffers[0]), self.colorBuffers[0])
        glDeleteTextures(len(self.colorBuffers[1]), self.colorBuffers[1])
        glDeleteRenderbuffers(len(self.depthStencilBuffers), self.depthStencilBuffers)
        glDeleteFramebuffers(len(self.fbos), self.fbos)
        pg.quit()

class Mesh:


    def __init__(self, filename):
        # x, y, z, s, t, nx, ny, nz, tx, ty, tz, bx, by, bz
        self.vertices = self.loadMesh(filename)
        self.vertex_count = len(self.vertices)//14
        self.vertices = np.array(self.vertices, dtype=np.float32)

        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)
        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW)
        offset = 0
        #position
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 56, ctypes.c_void_p(offset))
        offset += 12
        #texture
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 56, ctypes.c_void_p(offset))
        offset += 8
        #normal
        glEnableVertexAttribArray(2)
        glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, 56, ctypes.c_void_p(offset))
        offset += 12
        #tangent
        glEnableVertexAttribArray(3)
        glVertexAttribPointer(3, 3, GL_FLOAT, GL_FALSE, 56, ctypes.c_void_p(offset))
        offset += 12
        #bitangent
        glEnableVertexAttribArray(4)
        glVertexAttribPointer(4, 3, GL_FLOAT, GL_FALSE, 56, ctypes.c_void_p(offset))
        offset += 12
    
    def loadMesh(self, filename):

        #raw, unassembled data
        v = []
        vt = []
        vn = []
        
        #final, assembled and packed result
        vertices = []

        #open the obj file and read the data
        with open(filename,'r') as f:
            line = f.readline()
            while line:
                firstSpace = line.find(" ")
                flag = line[0:firstSpace]
                if flag=="v":
                    #vertex
                    line = line.replace("v ","")
                    line = line.split(" ")
                    l = [float(x) for x in line]
                    v.append(l)
                elif flag=="vt":
                    #texture coordinate
                    line = line.replace("vt ","")
                    line = line.split(" ")
                    l = [float(x) for x in line]
                    vt.append(l)
                elif flag=="vn":
                    #normal
                    line = line.replace("vn ","")
                    line = line.split(" ")
                    l = [float(x) for x in line]
                    vn.append(l)
                elif flag=="f":
                    #face, three or more vertices in v/vt/vn form
                    line = line.replace("f ","")
                    line = line.replace("\n","")
                    #get the individual vertices for each line
                    line = line.split(" ")
                    faceVertices = []
                    faceTextures = []
                    faceNormals = []
                    for vertex in line:
                        #break out into [v,vt,vn],
                        #correct for 0 based indexing.
                        l = vertex.split("/")
                        position = int(l[0]) - 1
                        faceVertices.append(v[position])
                        texture = int(l[1]) - 1
                        faceTextures.append(vt[texture])
                        normal = int(l[2]) - 1
                        faceNormals.append(vn[normal])
                    # obj file uses triangle fan format for each face individually.
                    # unpack each face
                    triangles_in_face = len(line) - 2

                    vertex_order = []
                    """
                        eg. 0,1,2,3 unpacks to vertices: [0,1,2,0,2,3]
                    """
                    for i in range(triangles_in_face):
                        vertex_order.append(0)
                        vertex_order.append(i+1)
                        vertex_order.append(i+2)
                    # calculate tangent and bitangent for point
                    # how do model positions relate to texture positions?
                    point1 = faceVertices[vertex_order[0]]
                    point2 = faceVertices[vertex_order[1]]
                    point3 = faceVertices[vertex_order[2]]
                    uv1 = faceTextures[vertex_order[0]]
                    uv2 = faceTextures[vertex_order[1]]
                    uv3 = faceTextures[vertex_order[2]]
                    #direction vectors
                    deltaPos1 = [point2[i] - point1[i] for i in range(3)]
                    deltaPos2 = [point3[i] - point1[i] for i in range(3)]
                    deltaUV1 = [uv2[i] - uv1[i] for i in range(2)]
                    deltaUV2 = [uv3[i] - uv1[i] for i in range(2)]
                    # calculate
                    den = 1 / (deltaUV1[0] * deltaUV2[1] - deltaUV2[0] * deltaUV1[1])
                    tangent = []
                    #tangent x
                    tangent.append(den * (deltaUV2[1] * deltaPos1[0] - deltaUV1[1] * deltaPos2[0]))
                    #tangent y
                    tangent.append(den * (deltaUV2[1] * deltaPos1[1] - deltaUV1[1] * deltaPos2[1]))
                    #tangent z
                    tangent.append(den * (deltaUV2[1] * deltaPos1[2] - deltaUV1[1] * deltaPos2[2]))
                    bitangent = []
                    #bitangent x
                    bitangent.append(den * (-deltaUV2[0] * deltaPos1[0] + deltaUV1[0] * deltaPos2[0]))
                    #bitangent y
                    bitangent.append(den * (-deltaUV2[0] * deltaPos1[1] + deltaUV1[0] * deltaPos2[1]))
                    #bitangent z
                    bitangent.append(den * (-deltaUV2[0] * deltaPos1[2] + deltaUV1[0] * deltaPos2[2]))
                    for i in vertex_order:
                        for x in faceVertices[i]:
                            vertices.append(x)
                        for x in faceTextures[i]:
                            vertices.append(x)
                        for x in faceNormals[i]:
                            vertices.append(x)
                        for x in tangent:
                            vertices.append(x)
                        for x in bitangent:
                            vertices.append(x)
                line = f.readline()
        return vertices
    
    def destroy(self):
        glDeleteVertexArrays(1, (self.vao,))
        glDeleteBuffers(1,(self.vbo,))

class Material:

    
    def __init__(self, filepath):
        self.texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.texture)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST_MIPMAP_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        image = pg.image.load(filepath).convert_alpha()
        image = pg.transform.flip(image, False, True)
        image_width,image_height = image.get_rect().size
        img_data = pg.image.tostring(image,'RGBA')
        glTexImage2D(GL_TEXTURE_2D,0,GL_RGBA,image_width,image_height,0,GL_RGBA,GL_UNSIGNED_BYTE,img_data)
        glGenerateMipmap(GL_TEXTURE_2D)

    def use(self):
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D,self.texture)

    def destroy(self):
        glDeleteTextures(1, (self.texture,))

class AdvancedMaterial:

    
    def __init__(self, fileroot):

        #albedo
        self.albedoTexture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.albedoTexture)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST_MIPMAP_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        image = pg.image.load(f"gfx/{fileroot}_albedo.png").convert_alpha()
        image_width,image_height = image.get_rect().size
        img_data = pg.image.tostring(image,'RGBA')
        glTexImage2D(GL_TEXTURE_2D,0,GL_RGBA,image_width,image_height,0,GL_RGBA,GL_UNSIGNED_BYTE,img_data)
        glGenerateMipmap(GL_TEXTURE_2D)

        #ambient occlusion
        self.ambientOcclusionTexture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.ambientOcclusionTexture)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST_MIPMAP_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        image = pg.image.load(f"gfx/{fileroot}_ao.png").convert_alpha()
        image_width,image_height = image.get_rect().size
        img_data = pg.image.tostring(image,'RGBA')
        glTexImage2D(GL_TEXTURE_2D,0,GL_RGBA,image_width,image_height,0,GL_RGBA,GL_UNSIGNED_BYTE,img_data)
        glGenerateMipmap(GL_TEXTURE_2D)

        #glossmap
        self.glossmapTexture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.glossmapTexture)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST_MIPMAP_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        image = pg.image.load(f"gfx/{fileroot}_glossmap.png").convert_alpha()
        image_width,image_height = image.get_rect().size
        img_data = pg.image.tostring(image,'RGBA')
        glTexImage2D(GL_TEXTURE_2D,0,GL_RGBA,image_width,image_height,0,GL_RGBA,GL_UNSIGNED_BYTE,img_data)
        glGenerateMipmap(GL_TEXTURE_2D)

        #normal
        self.normalTexture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.normalTexture)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST_MIPMAP_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        image = pg.image.load(f"gfx/{fileroot}_normal.png").convert_alpha()
        image_width,image_height = image.get_rect().size
        img_data = pg.image.tostring(image,'RGBA')
        glTexImage2D(GL_TEXTURE_2D,0,GL_RGBA,image_width,image_height,0,GL_RGBA,GL_UNSIGNED_BYTE,img_data)
        glGenerateMipmap(GL_TEXTURE_2D)

        #handy list
        self.textures = [
            self.albedoTexture, self.ambientOcclusionTexture, self.glossmapTexture, self.normalTexture
        ]

    def use(self):

        for i,texture in enumerate(self.textures):
            glActiveTexture(GL_TEXTURE0 + i)
            glBindTexture(GL_TEXTURE_2D, texture)

    def destroy(self):
        glDeleteTextures(len(self.textures), self.textures)

class BillBoard:


    def __init__(self, w, h):

        #x,y,z, s,t, normal, tangent, bitangent

        self.vertices = (
            0, -w/2,  h/2, 0, 0, -1, 0, 0, 0, 0, 1, 0, 1, 0,
            0, -w/2, -h/2, 0, 1, -1, 0, 0, 0, 0, 1, 0, 1, 0,
            0,  w/2, -h/2, 1, 1, -1, 0, 0, 0, 0, 1, 0, 1, 0,

            0, -w/2,  h/2, 0, 0, -1, 0, 0, 0, 0, 1, 0, 1, 0,
            0,  w/2, -h/2, 1, 1, -1, 0, 0, 0, 0, 1, 0, 1, 0,
            0,  w/2,  h/2, 1, 0, -1, 0, 0, 0, 0, 1, 0, 1, 0
        )
        self.vertices = np.array(self.vertices, dtype=np.float32)
        self.vertexCount = 6
        
        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)
        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW)
        offset = 0
        #position
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 56, ctypes.c_void_p(offset))
        offset += 12
        #texture
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 56, ctypes.c_void_p(offset))
        offset += 8
        #normal
        glEnableVertexAttribArray(2)
        glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, 56, ctypes.c_void_p(offset))
        offset += 12
        #tangent
        glEnableVertexAttribArray(3)
        glVertexAttribPointer(3, 3, GL_FLOAT, GL_FALSE, 56, ctypes.c_void_p(offset))
        offset += 12
        #bitangent
        glEnableVertexAttribArray(4)
        glVertexAttribPointer(4, 3, GL_FLOAT, GL_FALSE, 56, ctypes.c_void_p(offset))
        offset += 12
    
    def destroy(self):
        glDeleteVertexArrays(1, (self.vao,))
        glDeleteBuffers(1, (self.vbo,))

class TexturedQuad:


    def __init__(self, x, y, w, h):
        self.vertices = (
            x - w, y + h, 0, 1,
            x - w, y - h, 0, 0,
            x + w, y - h, 1, 0,

            x - w, y + h, 0, 1,
            x + w, y - h, 1, 0,
            x + w, y + h, 1, 1
        )
        self.vertices = np.array(self.vertices, dtype=np.float32)

        self.vertex_count = 6
        
        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)
        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW)

        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 16, ctypes.c_void_p(0))

        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 16, ctypes.c_void_p(8))
    
    def destroy(self):
        glDeleteVertexArrays(1, (self.vao,))
        glDeleteBuffers(1, (self.vbo,))

class Font:

    def __init__(self):

         #some parameters for fine tuning.
        w = 55.55 / 1000.0
        h =  63.88 / 1150.0
        heightOffset = 8.5 / 1150.0
        margin = 0.014

        """
            Letter: (left, top, width, height)
        """
        self.letterTexCoords = {
            'A': (       w, h,                          w - margin, margin - h), 'B': ( 3.0 * w, h,                          w - margin, margin - h),
            'C': ( 5.0 * w, h,                          w - margin, margin - h), 'D': ( 7.0 * w, h,                          w - margin, margin - h),
            'E': ( 9.0 * w, h,                          w - margin, margin - h), 'F': (11.0 * w, h,                          w - margin, margin - h),
            'G': (13.0 * w, h,                          w - margin, margin - h), 'H': (15.0 * w, h,                          w - margin, margin - h),
            'I': (17.0 * w, h,                          w - margin, margin - h), 'J': (       w, 3.0 * h + heightOffset,     w - margin, margin - h),
            'K': ( 3.0 * w, 3.0 * h + heightOffset,     w - margin, margin - h), 'L': ( 5.0 * w, 3.0 * h + heightOffset,     w - margin, margin - h),
            'M': ( 7.0 * w, 3.0 * h + heightOffset,     w - margin, margin - h), 'N': ( 9.0 * w, 3.0 * h + heightOffset,     w - margin, margin - h),
            'O': (11.0 * w, 3.0 * h + heightOffset,     w - margin, margin - h), 'P': (13.0 * w, 3.0 * h + heightOffset,     w - margin, margin - h),
            'Q': (15.0 * w, 3.0 * h + heightOffset,     w - margin, margin - h), 'R': (17.0 * w, 3.0 * h + heightOffset,     w - margin, margin - h),
            'S': (       w, 5.0 * h + 2 * heightOffset, w - margin, margin - h), 'T': ( 3.0 * w, 5.0 * h + 2 * heightOffset, w - margin, margin - h),
            'U': ( 5.0 * w, 5.0 * h + 2 * heightOffset, w - margin, margin - h), 'V': ( 7.0 * w, 5.0 * h + 2 * heightOffset, w - margin, margin - h),
            'W': ( 9.0 * w, 5.0 * h + 2 * heightOffset, w - margin, margin - h), 'X': (11.0 * w, 5.0 * h + 2 * heightOffset, w - margin, margin - h),
            'Y': (13.0 * w, 5.0 * h + 2 * heightOffset, w - margin, margin - h), 'Z': (15.0 * w, 5.0 * h + 2 * heightOffset, w - margin, margin - h),

            'a': (       w,                     7.0 * h, w - margin, margin - h), 'b': ( 3.0 * w,                     7.0 * h, w - margin, margin - h),
            'c': ( 5.0 * w,                     7.0 * h, w - margin, margin - h), 'd': ( 7.0 * w,                     7.0 * h, w - margin, margin - h),
            'e': ( 9.0 * w,                     7.0 * h, w - margin, margin - h), 'f': (11.0 * w,                     7.0 * h, w - margin, margin - h),
            'g': (13.0 * w,                     7.0 * h, w - margin, margin - h), 'h': (15.0 * w,                     7.0 * h, w - margin, margin - h),
            'i': (17.0 * w,                     7.0 * h, w - margin, margin - h), 'j': (       w,      9.0 * h + heightOffset, w - margin, margin - h),
            'k': ( 3.0 * w,      9.0 * h + heightOffset, w - margin, margin - h), 'l': ( 5.0 * w,      9.0 * h + heightOffset, w - margin, margin - h),
            'm': ( 7.0 * w,      9.0 * h + heightOffset, w - margin, margin - h), 'n': ( 9.0 * w,      9.0 * h + heightOffset, w - margin, margin - h),
            'o': (11.0 * w,      9.0 * h + heightOffset, w - margin, margin - h), 'p': (13.0 * w,      9.0 * h + heightOffset, w - margin, margin - h),
            'q': (15.0 * w,      9.0 * h + heightOffset, w - margin, margin - h), 'r': (17.0 * w,      9.0 * h + heightOffset, w - margin, margin - h),
            's': (       w, 11.0 * h + 2 * heightOffset, w - margin, margin - h), 't': ( 3.0 * w, 11.0 * h + 2 * heightOffset, w - margin, margin - h),
            'u': ( 5.0 * w, 11.0 * h + 2 * heightOffset, w - margin, margin - h), 'v': ( 7.0 * w, 11.0 * h + 2 * heightOffset, w - margin, margin - h),
            'w': ( 9.0 * w, 11.0 * h + 2 * heightOffset, w - margin, margin - h), 'x': (11.0 * w, 11.0 * h + 2 * heightOffset, w - margin, margin - h),
            'y': (13.0 * w, 11.0 * h + 2 * heightOffset, w - margin, margin - h), 'z': (15.0 * w, 11.0 * h + 2 * heightOffset, w - margin, margin - h),

            '0': (       w, 13.0 * h, w - margin, margin - h), '1':  ( 3.0 * w,                13.0 * h, w - margin, margin - h),
            '2': ( 5.0 * w, 13.0 * h, w - margin, margin - h), '3':  ( 7.0 * w,                13.0 * h, w - margin, margin - h),
            '4': ( 9.0 * w, 13.0 * h, w - margin, margin - h), '5':  (11.0 * w,                13.0 * h, w - margin, margin - h),
            '6': (13.0 * w, 13.0 * h, w - margin, margin - h), '7':  (15.0 * w,                13.0 * h, w - margin, margin - h),
            '8': (17.0 * w, 13.0 * h, w - margin, margin - h), '9':  (       w, 15.0 * h + heightOffset, w - margin, margin - h),
            
            '.':  ( 3.0 * w,     15.0 * h + heightOffset, w - margin, margin - h), ',': ( 5.0 * w,     15.0 * h + heightOffset, w - margin, margin - h),
            ';':  ( 7.0 * w,     15.0 * h + heightOffset, w - margin, margin - h), ':': ( 9.0 * w,     15.0 * h + heightOffset, w - margin, margin - h),
            '$':  (11.0 * w,     15.0 * h + heightOffset, w - margin, margin - h), '#': (13.0 * w,     15.0 * h + heightOffset, w - margin, margin - h),
            '\'': (15.0 * w,     15.0 * h + heightOffset, w - margin, margin - h), '!': (17.0 * w,     15.0 * h + heightOffset, w - margin, margin - h),
            '"':  (       w, 17.0 * h + 2 * heightOffset, w - margin, margin - h), '/': ( 3.0 * w, 17.0 * h + 2 * heightOffset, w - margin, margin - h),
            '?':  ( 5.0 * w, 17.0 * h + 2 * heightOffset, w - margin, margin - h), '%': ( 7.0 * w, 17.0 * h + 2 * heightOffset, w - margin, margin - h),
            '&':  ( 9.0 * w, 17.0 * h + 2 * heightOffset, w - margin, margin - h), '(': (11.0 * w, 17.0 * h + 2 * heightOffset, w - margin, margin - h),
            ')':  (13.0 * w, 17.0 * h + 2 * heightOffset, w - margin, margin - h), '@': (15.0 * w, 17.0 * h + 2 * heightOffset, w - margin, margin - h)
        }

        self.texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.texture)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST_MIPMAP_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        image = pg.image.load("gfx/Inconsolata.png").convert_alpha()
        image_width,image_height = image.get_rect().size
        img_data = pg.image.tostring(image,'RGBA')
        glTexImage2D(GL_TEXTURE_2D,0,GL_RGBA,image_width,image_height,0,GL_RGBA,GL_UNSIGNED_BYTE,img_data)
        glGenerateMipmap(GL_TEXTURE_2D)
    
    def get_bounding_box(self, letter):

        if letter in self.letterTexCoords:
            return self.letterTexCoords[letter]
        return None
    
    def use(self):
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D,self.texture)

    def destroy(self):
        glDeleteTextures(1, (self.texture,))

class TextLine:

    
    def __init__(self, initial_text, font, start_position, letter_size):

        self.vao = glGenVertexArrays(1)
        self.vbo = glGenBuffers(1)
        self.start_position = start_position
        self.letter_size = letter_size
        self.build_text(initial_text, font)
    
    def build_text(self, new_text, font):

        self.vertices = []
        self.vertex_count = 0

        margin_adjustment = 0.96

        for i,letter in enumerate(new_text):

            bounding_box  = font.get_bounding_box(letter)
            if bounding_box is None:
                continue

            #top left
            self.vertices.append(
                self.start_position[0] - self.letter_size[0] + ((2 - margin_adjustment) * i * self.letter_size[0])
            )
            self.vertices.append(self.start_position[1] + self.letter_size[1])
            self.vertices.append(bounding_box[0] - bounding_box[2])
            self.vertices.append(bounding_box[1] + bounding_box[3])
            #top right
            self.vertices.append(
                self.start_position[0] + self.letter_size[0] + ((2 - margin_adjustment) * i * self.letter_size[0])
            )
            self.vertices.append(self.start_position[1] + self.letter_size[1])
            self.vertices.append(bounding_box[0] + bounding_box[2])
            self.vertices.append(bounding_box[1] + bounding_box[3])
            #bottom right
            self.vertices.append(
                self.start_position[0] + self.letter_size[0] + ((2 - margin_adjustment) * i * self.letter_size[0])
            )
            self.vertices.append(self.start_position[1] - self.letter_size[1])
            self.vertices.append(bounding_box[0] + bounding_box[2])
            self.vertices.append(bounding_box[1] - bounding_box[3])

            #bottom right
            self.vertices.append(
                self.start_position[0] + self.letter_size[0] + ((2 - margin_adjustment) * i * self.letter_size[0])
            )
            self.vertices.append(self.start_position[1] - self.letter_size[1])
            self.vertices.append(bounding_box[0] + bounding_box[2])
            self.vertices.append(bounding_box[1] - bounding_box[3])
            #bottom left
            self.vertices.append(
                self.start_position[0] - self.letter_size[0] + ((2 - margin_adjustment) * i * self.letter_size[0])
            )
            self.vertices.append(self.start_position[1] - self.letter_size[1])
            self.vertices.append(bounding_box[0] - bounding_box[2])
            self.vertices.append(bounding_box[1] - bounding_box[3])
            #top left
            self.vertices.append(
                self.start_position[0] - self.letter_size[0] + ((2 - margin_adjustment) * i * self.letter_size[0])
            )
            self.vertices.append(self.start_position[1] + self.letter_size[1])
            self.vertices.append(bounding_box[0] - bounding_box[2])
            self.vertices.append(bounding_box[1] + bounding_box[3])

            self.vertex_count += 6

        self.vertices = np.array(self.vertices, dtype=np.float32)

        glBindVertexArray(self.vao)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW)
        offset = 0
        #position
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 16, ctypes.c_void_p(offset))
        offset += 8
        #texture
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 16, ctypes.c_void_p(offset))
    
    def destroy(self):
        glDeleteVertexArrays(1, (self.vao,))
        glDeleteBuffers(1,(self.vbo,))

myApp = App(800,600)