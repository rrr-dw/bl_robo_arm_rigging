import bpy
from bpy.types import Context, Object, Scene

def scene_objs_to_enum_items(scene:Scene,context:Context):
	names:list[str] = [o.name for o in bpy.context.scene.objects]

	items = [(name, name,"",i+1) for i,name in enumerate(names)]
	items.append(('NONE',"(None)","",0))
	return items
	
EnumProperty_scene_objects = bpy.props.EnumProperty(items=scene_objs_to_enum_items,name="Objects")
