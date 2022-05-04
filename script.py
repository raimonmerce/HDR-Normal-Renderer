import bpy
import random
import os
from math import radians

#Constants
path_images = "";
path_object = '';
output_dir = '';
output_file_pattern_string = 'render%d-%s.jpg'
output_file_pattern_string_normal = 'renderN%d-%s.jpg'
rotation_steps = 5;
rotation_angle = 360.0;
sizeX = 1080;
sizeY = 1080;
cameraLend = 164;

C = bpy.context;

#Get object
bpy.ops.import_scene.obj(filepath=path_object)
bpy.ops.object.shade_smooth();
subject = C.selected_objects[0]; 
C.scene.world.use_nodes = True;
world_tree = C.scene.world.node_tree;

object_tree = subject.active_material.node_tree;

bpy.context.scene.render.film_transparent = True #Not render background
render = bpy.context.scene.render #Change render view size
print(render.resolution_x)
print(render.resolution_y)
render.resolution_x = sizeX;
render.resolution_y = sizeY;
cam_ob = bpy.data.cameras.values()[0];
cam_ob.lens = cameraLend;

world = world_tree.nodes[0];
enode = world_tree.nodes.new("ShaderNodeTexEnvironment");
world_tree.links.new(enode.outputs['Color'], world.inputs['Surface'])

matOutput = object_tree.nodes.get("Material Output")
matDefault = object_tree.nodes.get("Principled BSDF")
subject.active_material.name = "Default OBJ"


normalNode = object_tree.nodes.new(type="ShaderNodeNormalMap")
#object_tree.links.new(normalNode.outputs['Normal'], matOutput.inputs['Surface'])
#object_tree.links.new(matDefault.outputs['BSDF'], matOutput.inputs['Surface'])

for subdir, dirs, files in os.walk(path_images):
    for file in files:
        myTuple = (subdir, file);
        path_image = "/".join(myTuple);
        enode.image = bpy.data.images.load(path_image);
        original_rotation = subject.rotation_euler;
        for step in range(0, rotation_steps):
            subject.rotation_euler[0] += radians(random.randint(0,359));
            subject.rotation_euler[1] += radians(random.randint(0,359));
            subject.rotation_euler[2] += radians(random.randint(0,359));
            #Render HDR
            bpy.context.scene.render.filepath = os.path.join(output_dir, (output_file_pattern_string % (step,file.replace('.exr', ''))))
            bpy.ops.render.render(write_still = True)
            
            #Render Normal
            object_tree.links.new(normalNode.outputs['Normal'], matOutput.inputs['Surface'])
            bpy.context.scene.render.filepath = os.path.join(output_dir, (output_file_pattern_string_normal % (step,file.replace('.exr', ''))))
            bpy.ops.render.render(write_still = True)
            
            object_tree.links.new(matDefault.outputs['BSDF'], matOutput.inputs['Surface'])
            
        subject.rotation_euler = original_rotation
