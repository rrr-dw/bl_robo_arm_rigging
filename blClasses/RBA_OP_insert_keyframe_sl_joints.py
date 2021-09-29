import bpy
from bpy.types import Context, Event, Object, UILayout
from ..RoboArmComponent import SerialChain, Joint, walk_chained_empties

class RBA_OP_insert_keyframe_sl_joints(bpy.types.Operator):
	'''Insert keyframe for joint variables'''
	bl_idname = "rba.insert_keyframe_sl"
	bl_label = "Insert keyframe for joint variables"
	bl_options = {'REGISTER','UNDO'}

	@classmethod
	def poll(cls,context:Context):
		if bpy.context.object == None or bpy.context.object.data!=None:
			return False

		sc = SerialChain.create_from_base_empty(bpy.context.object)
		if sc==None:
			return False

		return sc.has_driver(bpy.context.object)

	def execute(self, context:Context):
		sc = SerialChain.create_from_base_empty(bpy.context.object)

		for i in range(len(sc.joints)):
			bpy.context.object.keyframe_insert(f'["q{i}"]')

		return {'FINISHED'}

