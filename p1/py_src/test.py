import torch
import os

# 设置 DISPLAY
# os.environ["DISPLAY"] = ":0"
from direct.showbase.ShowBase import ShowBase
from util.repo import *
from panda3d.core import loadPrcFileData
from panda3d.core import WindowProperties
from panda3d.core import (
    NodePath,
    WindowProperties,
    Vec2, Vec3,
    TextNode,
    PNMImage, Texture,
    CardMaker,Point2,
    NodePath, Camera, PerspectiveLens,
    Point3, LVector3f, Texture,
Shader,Vec4, SamplerState
)
from art.basic import (
    create_cube_node, create_sphere_node,
uv_curve_surface,create_colored_cube_node
)
from typing import Tuple
from typing import List,Set, List, Dict,Callable
from panda3d_game.app import ControlShowBase, ContextShowBase, PhysicsShowBase,UniversalGravitySpace
from vispyutil.canvas import SynchronizedCanvas
from vispyutil.showbase import CanvasBackgroundShowBase


import numpy as np
from sympy.physics.units import (
    kilometer, meter,centimeter,
    gram, kilogram, tonne,
    newton, second
)
from panda3d.core import (
    NodePath,
    WindowProperties,
    Vec3,
    TextNode,
    PNMImage, Texture,
    CardMaker,Point2,
    NodePath, Camera, PerspectiveLens,
    Point3, LVector3f
)
from util.physics import autocomplete_units, G_val, getG
# from demos.ball_room import MassedBall,tmoon
from util.log import *
from config.style import styleSheet
import yaml
from util.physics import autocomplete_units, G_val, getG
from art.assets.starfield import StarCanvas
# from PyQt5.QtWidgets import (
#     QWidget, QApplication, QMainWindow,
#     QDockWidget, QTextEdit, QPlainTextEdit
# )

from art.procedural_art.perlin_landmap import fractal_perlin_custom_lac
from util.geometry import format_normal

tdirt = Texture()
tdirt.read(os.path.join(res_root, "dirt.jpg"))
tdirt.setWrapU(Texture.WM_repeat)
tdirt.setWrapV(Texture.WM_repeat)
tdirt.minfilter = SamplerState.FT_linear_mipmap_linear
tdirt.magfilter = SamplerState.FT_linear_mipmap_linear

terrain_vert = """
#version 140

in vec4 p3d_Vertex;
in vec3 p3d_Normal;
in vec3 p3d_MultiTexCoord0;

uniform mat4 p3d_ModelViewMatrix;
uniform mat4 p3d_ModelViewProjectionMatrix;
uniform mat3 p3d_NormalMatrix;

out vec3 fragPos;
out vec3 normal;
out vec2 uv;


void main() {
    // Calculate vertex position, fragment position, and surface normal
    gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;
    fragPos = vec3(p3d_ModelViewMatrix * p3d_Vertex);
    normal = p3d_NormalMatrix * p3d_Normal;

    // Calculate UV
    uv = p3d_MultiTexCoord0.xy;
}
"""

terrain_frag = """
#version 140

in vec3 fragPos;
in vec3 normal;
in vec2 uv;

uniform mat4 p3d_ViewMatrix;

uniform vec2 texScale0;

uniform struct p3d_LightModelParameters {
    vec4 ambient;
} p3d_LightModel;
uniform struct p3d_LightSourceParameters {
    // Primary light color.
    vec4 color;

    // Light color broken up into components, for compatibility with legacy
    // shaders. These are now deprecated.
    vec4 ambient;
    vec4 diffuse;
    vec4 specular;

    // View-space position. If w=0, this is a directional light, with the xyz
    // being -direction.
    vec4 position;

    // Spotlight-only settings
    vec3 spotDirection;
    float spotExponent;
    float spotCutoff;
    float spotCosCutoff;

    // Individual attenuation constants
    float constantAttenuation;
    float linearAttenuation;
    float quadraticAttenuation;

    // constant, linear, quadratic attenuation in one vector
    vec3 attenuation;

    // Shadow map for this light source
    sampler2DShadow shadowMap;

    // Transforms view-space coordinates to shadow map coordinates
    mat4 shadowViewMatrix;
} p3d_LightSource[2];
uniform struct p3d_MaterialParameters {
    vec4 ambient;
    vec4 diffuse;
    vec4 emission;
    vec3 specular;
    float shininess;
    
    vec4 baseColor;
    float roughness;
    float metallic;
    float refractiveIndex;
} p3d_Material;
uniform struct p3d_FogParameters {
    vec4 color;
    float density;
    float start;
    float end;
    float scale; // 1.0 / (end - start)
} p3d_Fog;
uniform sampler2D p3d_Texture0;

out vec4 p3d_FragColor;


vec4 applyLighting(vec4 color) {
    // Normalize normal and extract camera position from view matrix
    vec3 norm = normalize(normal);
    vec3 cameraPos = p3d_ViewMatrix[3].xyz;

    // Calculate lighting
    vec4 lighting = vec4(0.0);

    for(int i = 0; i < p3d_LightSource.length(); i++) {
        // Calculate light vector
        vec3 lightVector = p3d_LightSource[i].position.xyz - fragPos * 
            p3d_LightSource[i].position.w;

        // Calculate attenuation
        float dist = length(lightVector);
        float attenuation = 1.0 / (p3d_LightSource[i].constantAttenuation + 
            p3d_LightSource[i].linearAttenuation * dist + 
            p3d_LightSource[i].quadraticAttenuation * dist * dist);

        // Normalize light vector
        lightVector = normalize(lightVector);

        // Calculate diffuse lighting
        float nxDir = max(0.0, dot(norm, lightVector));
        vec4 diffuse = p3d_LightSource[i].color * nxDir * attenuation;

        // Calculate specular lighting
        vec3 cameraVector = normalize(cameraPos - fragPos);
        vec3 halfVector = normalize(lightVector + cameraVector);
        float nxHalf = max(0.0, dot(norm, halfVector));
        float specularPower = pow(nxHalf, p3d_Material.shininess);
        vec4 specular = p3d_LightSource[i].color * specularPower * 
            attenuation * int(nxDir != 0.0);

        // Calculate total lighting
        lighting += (p3d_LightModel.ambient * p3d_Material.ambient + 
            (diffuse * p3d_Material.diffuse) + 
            (specular * vec4(p3d_Material.specular, 1.0)));
    }

    // Apply lighting to initial color
    lighting.a = color.a;
    return color * lighting;
}


vec4 applyFog(vec4 color) {
    // If fog is disabled, skip fog calculations
    if(p3d_Fog.start == p3d_Fog.end) {
        return color;
    }

    // Calculate linear fog
    float dist = length(fragPos);
    float fogFactor = (p3d_Fog.end - dist) / (p3d_Fog.end - p3d_Fog.start);
    fogFactor = clamp(fogFactor, 0, 1);
    return mix(p3d_Fog.color, color, fogFactor);
}


void main() {
    // Calculate base color
    // vec4 baseColor = texture(p3d_Texture0, uv);
    vec4 baseColor = texture(p3d_Texture0, uv / texScale0);
    // Calculate final color
    p3d_FragColor = applyFog(applyLighting(baseColor));
}
"""
water_vert = """
#version 140

in vec4 p3d_Vertex;
in vec3 p3d_Normal;

uniform mat4 p3d_ModelViewMatrix;
uniform mat4 p3d_ModelViewProjectionMatrix;
uniform mat3 p3d_NormalMatrix;

out vec3 fragPos;
out vec3 normal;


void main() {
    // Calculate position, fragment position, and normal
    gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;
    fragPos = vec3(p3d_ModelViewMatrix * p3d_Vertex);
    normal = p3d_NormalMatrix * p3d_Normal;
}
"""

water_frag = """
#version 140

in vec3 fragPos;
in vec3 normal;

uniform mat4 p3d_ViewMatrix;
uniform struct p3d_LightModelParameters {
    vec4 ambient;
} p3d_LightModel;
uniform struct p3d_LightSourceParameters {
    // Primary light color.
    vec4 color;

    // Light color broken up into components, for compatibility with legacy
    // shaders. These are now deprecated.
    vec4 ambient;
    vec4 diffuse;
    vec4 specular;

    // View-space position. If w=0, this is a directional light, with the xyz
    // being -direction.
    vec4 position;

    // Spotlight-only settings
    vec3 spotDirection;
    float spotExponent;
    float spotCutoff;
    float spotCosCutoff;

    // Individual attenuation constants
    float constantAttenuation;
    float linearAttenuation;
    float quadraticAttenuation;

    // constant, linear, quadratic attenuation in one vector
    vec3 attenuation;

    // Shadow map for this light source
    sampler2DShadow shadowMap;

    // Transforms view-space coordinates to shadow map coordinates
    mat4 shadowViewMatrix;
} p3d_LightSource[2];
uniform struct p3d_MaterialParameters {
    vec4 ambient;
    vec4 diffuse;
    vec4 emission;
    vec3 specular;
    float shininess;
    
    vec4 baseColor;
    float roughness;
    float metallic;
    float refractiveIndex;
} p3d_Material;
uniform struct p3d_FogParameters {
    vec4 color;
    float density;
    float start;
    float end;
    float scale; // 1.0 / (end - start)
} p3d_Fog;

out vec4 p3d_FragColor;


vec4 applyLighting(vec4 color) {
    // Normalize normal and extract camera position from view matrix
    vec3 norm = normalize(normal);
    vec3 cameraPos = p3d_ViewMatrix[3].xyz;

    // Calculate lighting
    vec4 lighting = vec4(0.0);

    for(int i = 0; i < p3d_LightSource.length(); i++) {
        // Calculate light vector
        vec3 lightVector = p3d_LightSource[i].position.xyz - fragPos * 
            p3d_LightSource[i].position.w;

        // Calculate attenuation
        float dist = length(lightVector);
        float attenuation = 1.0 / (p3d_LightSource[i].constantAttenuation + 
            p3d_LightSource[i].linearAttenuation * dist + 
            p3d_LightSource[i].quadraticAttenuation * dist * dist);

        // Normalize light vector
        lightVector = normalize(lightVector);

        // Calculate diffuse lighting
        float nxDir = max(0.0, dot(norm, lightVector));
        vec4 diffuse = p3d_LightSource[i].color * nxDir * attenuation;

        // Calculate specular lighting
        vec3 cameraVector = normalize(cameraPos - fragPos);
        vec3 halfVector = normalize(lightVector + cameraVector);
        float nxHalf = max(0.0, dot(norm, halfVector));
        float specularPower = pow(nxHalf, p3d_Material.shininess);
        vec4 specular = p3d_LightSource[i].color * specularPower * 
            attenuation * int(nxDir != 0.0);

        // Calculate total lighting
        lighting += (p3d_LightModel.ambient * p3d_Material.ambient + 
            (diffuse * p3d_Material.diffuse) + 
            (specular * vec4(p3d_Material.specular, 1.0)));
    }

    // Apply lighting to initial color
    lighting.a = color.a;
    return color * lighting;
}


vec4 applyFog(vec4 color) {
    // If fog is disabled, skip fog calculations
    if(p3d_Fog.start == p3d_Fog.end) {
        return color;
    }

    // Calculate linear fog
    float dist = length(fragPos);
    float fogFactor = (p3d_Fog.end - dist) / (p3d_Fog.end - p3d_Fog.start);
    fogFactor = clamp(fogFactor, 0, 1);
    return mix(p3d_Fog.color, color, fogFactor);
}


void main() {
    // Calculate base color
    vec4 baseColor = vec4(1, 1, 1, 1);

    // Calculate final color
    p3d_FragColor = applyFog(applyLighting(baseColor));
}
"""

noise = fractal_perlin_custom_lac(
    (512,512),
    (4,4),
    lacunarity_list=[1.5, 2.2, 2.8, 1.7, 3.0]
)
z = noise * 100
z[-1] = 0
z[0] = 0
z[:,-1] = 0
z[:,0] = 0
x = torch.ones_like(z)
y = torch.ones_like(z)
# x = x * torch.lin
x = x * torch.linspace(-256, 255, 512).unsqueeze(0)
y = y * torch.linspace(-256, 255, 512).unsqueeze(1)

xyz = torch.concat([
    x.unsqueeze(-1),
    y.unsqueeze(-1),
    z.unsqueeze(-1)
],dim=-1)
landscape = uv_curve_surface(
    "land", xyz, False,False,
    vformat=format_normal
)

from panda3d.core import (
    Geom,
    GeomNode,
    GeomTriangles,
    GeomVertexData,
    GeomVertexFormat,
    GeomVertexWriter,
    Vec3
)
from panda3d_game.game_object import GameObject 

class WaterPlane(GameObject):
    plane_mesh = None
    water_mat = None
    water_shader = Shader.make(
        Shader.SL_GLSL,
        # "shaders/Water.vert.glsl",
        # "shaders/Water.frag.glsl"
        water_vert,
        water_frag
    )

    def __init__(self, pos=Vec3(), heading=0, scale=Vec3(1, 1, 1)):
        # Initialize plane mesh if necessary
        if self.plane_mesh is None:
            # Get V3N3T2 format
            vtx_format = GeomVertexFormat.get_v3() # FIXME

            # Allocate vertex data
            vertices = GeomVertexData("WaterPlane", vtx_format, Geom.UH_static)
            vertices.reserve_num_rows(4)

            # Write vertex data
            vertex = GeomVertexWriter(vertices, "vertex")
            vertex.add_data3(-1, 1, 0)
            vertex.add_data3(1, 1, 0)
            vertex.add_data3(-1, -1, 0)
            vertex.add_data3(1, -1, 0)

            # Allocate primitive data
            triangles = GeomTriangles(Geom.UH_static)
            triangles.reserve_num_vertices(6)

            # Write primitive data
            triangles.add_vertices(0, 2, 1)
            triangles.add_vertices(1, 2, 3)

            # Create plane mesh
            WaterPlane.plane_mesh = Geom(vertices)
            self.plane_mesh.add_primitive(triangles)

        # Create water plane
        self.plane = base.render.attach_new_node(GeomNode("WaterPlane"))
        self.plane.node().add_geom(self.plane_mesh)
        self.plane.set_pos(pos)
        self.plane.set_h(heading)
        self.plane.set_scale(scale)

        if self.water_mat is None:
            WaterPlane.water_mat = Material()
            self.water_mat.set_ambient(Vec4(0, .225, .8, 1))
            self.water_mat.set_diffuse(Vec4(0, .225, .8, 1))
            self.water_mat.set_specular(Vec3(.5, .5, .5))
            self.water_mat.set_shininess(32)
        self.plane.set_shader(self.water_shader)
        
        self.plane.set_material(self.water_mat)

    @property
    def mainPath(self):
        return self.plane


from direct.showbase.ShowBase import ShowBase
from panda3d.core import (
    AmbientLight,
    DirectionalLight,
    PointLight,
    Shader,
    Material,
    Vec3,
    Vec4,
GeomNode
)
from panda3d_game.app import ContextShowBase
# Shader
# Application Class
# =================
normals = []

class ShaderDemo(ContextShowBase):
    def __init__(self):
        # Call the base constructor
        ContextShowBase.__init__(self)
        # self.sphere = create_sphere_node("sphere", lat_res=24, lon_res=24,vformat=format_normal)
        # self.sphere_np = NodePath(self.sphere)
        self.land = GeomNode("land")
        self.land.addGeom(landscape)
        self.land_np = NodePath(self.land)
        self.land_np.reparent_to(self.render)



        # 创建材质

        mat = Material()
        mat.setAmbient((1, 1, 1, 1))# 环境光反射
        mat.setSpecular((0.5, 0.5, 0.5, 1))# 镜面光颜色
        mat.setShininess(20)# 镜面高光大小/锐利程度
        mat.setDiffuse((0.8, 0.8, 0.8, 1))  # RGB 越接近 1 越亮/浅  # 漫反射
        
        
 
        

        self.ambient_light = self.render.attach_new_node(AmbientLight("AmbientLight"))
        # self.ambient_light.node().set_color(Vec4(.2, .2, .2, 1))
        self.ambient_light.node().set_color(Vec4(.2, .2, .2, 1))
        self.render.set_light(self.ambient_light)
        
        self.sun = self.render.attach_new_node(DirectionalLight("Sun"))
        self.sun.set_hpr(45, -45, 0)
        self.render.set_light(self.sun)
        

        self.terrain_shader = Shader.make(
            Shader.SL_GLSL,
            terrain_vert,
            terrain_frag
        )
        print(self.terrain_shader)
        self.land_np.set_shader(self.terrain_shader)
        self.land_np.set_shader_input("texScale0", Vec2(.1, .1))
        
        self.land_np.set_texture(tdirt)
        self.water = WaterPlane(
            Vec3(0, 0, 50),
            scale=Vec3(256, 256, 1)
        )
        self.new_cam = Camera("new cam")           # Camera 节点
        self.new_cam_np = self.render.attachNewNode(self.new_cam)  
        self.new_cam_np.setPos(10,10,10)
       
    def pause_switch(self, *args,**kwargs):
        pass





from qpanda3d import  QPanda3DWidget,  Synchronizer, QControlMultiView
from demos.physics_room import PhyscRoomConsole
class ShaderControl(ShaderDemo, QControlMultiView):
    def __init__(self):
        QControlMultiView.__init__(self)
        ShaderDemo.__init__(self)
    # def __init__(self, isQt = True):
    #     import pdb
    #     QControl.__init__(self)
    #     ShaderDemo.__init__(self)
    #     self.isQt = isQt
    #     if self.isQt:
    #         self.startQt()
from demos.physics_room import PhyscRoomConsole
from ui.qtui import *
from demos.physics_room import PhyscRoomConsole
class ShaderControl(ShaderDemo, QControlMultiView):
    def __init__(self):
        QControlMultiView.__init__(self)
        ShaderDemo.__init__(self)
    # def __init__(self, isQt = True):
    #     import pdb
    #     QControl.__init__(self)
    #     ShaderDemo.__init__(self)
    #     self.isQt = isQt
    #     if self.isQt:
    #         self.startQt()
from demos.physics_room import PhyscRoomConsole
from ui.qtui import *
# class ShaderControl(ShaderDemo, QControl):
#     def __init__(self, isQt = True):
#         import pdb
#         QControl.__init__(self)
#         ShaderDemo.__init__(self)
#         self.isQt = isQt
#         if self.isQt:
#             self.startQt()
# from demos.physics_room import PhyscRoomConsole
# from ui.qtui import *

class ShaderGame(MultiViewQtGUI):
    def get_game(self):
        game = ShaderControl()
        self.cameras["test"] = game.new_cam_np
        return game

    def get_console(self):
        return PhyscRoomConsole(showbase=self.panda3d)

if __name__ == '__main__':
    # torch.set_printoptions(precision=16, sci_mode=False)
    import sys
    app = QApplication(sys.argv)
    window = ShaderGame()
    window.show()
    sys.exit(app.exec_())
