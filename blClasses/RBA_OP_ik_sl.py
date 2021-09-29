from mathutils import Vector
from ..RoboArmComponent.IK import apply_IK
from ..EnumProperty import EnumProperty_scene_objects, EnumProperty_sl_preset
import bpy
from bpy.types import Context, Event, Object, UILayout
from ..RoboArmComponent import SerialChain, Joint, walk_chained_empties
from .RBA_PG_joint_dh import RBA_PG_joint_dh
import itertools

class RBA_OP_ik_sl(bpy.types.Operator):
	'''Move the tip of current serial link interactively'''
	bl_idname = "rba.ik_sl"
	bl_label = "IK Serial Link"
	bl_options = {'REGISTER','UNDO'}

	iteration:bpy.props.IntProperty(name="iteration", min=0, default=10) # type: ignore
	target:bpy.props.FloatVectorProperty(name="target", subtype='TRANSLATION') # type: ignore
	insert_keyframe:bpy.props.BoolProperty(name="insert keyframe",default=True,description="insert keyframe for joint variables(q_i)") # type: ignore
	constrained:bpy.props.BoolProperty(name="constrained",default=False,description="WIP") # type: ignore
	control_key:str

	@classmethod
	def poll(cls,context:Context):
		if bpy.context.object == None or bpy.context.object.data!=None:
			return False

		sc = SerialChain.create_from_base_empty(bpy.context.object)
		if sc==None:
			return False

		return len(sc.joints)>1 and sc.has_driver(bpy.context.object)

	def execute(self, context:Context):
		if self.control_key in bpy.data.objects:
			control = bpy.data.objects[self.control_key]
			bpy.data.objects.remove(control)
			context.view_layer.objects.active.select_set(True)

		sc = SerialChain.create_from_base_empty(bpy.context.object)
		apply_IK(sc, Vector(self.target), self.iteration, self.constrained)
		sc.as_empties(context.collection,original_base=bpy.context.object,insert_keyframe=self.insert_keyframe)

		return {'FINISHED'}

	def invoke(self,context:Context,event):
		sc = SerialChain.create_from_base_empty(bpy.context.object)
		self.target = sc.global_mat(-1).translation

		control = bpy.data.objects.new("_IK_Target_Control",None)
		self.control_key = control.name_full
		context.collection.objects.link(control)
		control.location = self.target
		for o in bpy.context.selected_objects:
			o.select_set(False)

		control.select_set(True)

		context.window_manager.modal_handler_add(self)
		return bpy.ops.transform.translate('INVOKE_DEFAULT')

	def modal(self,context:Context,event:Event):
		if self.control_key not in bpy.data.objects:
			return {'CANCELLED'}

		control = bpy.data.objects[self.control_key]
		self.target = control.location
		return self.execute(context)

	def draw(self,context:Context):
		layout = self.layout

		layout.prop(self, "iteration")
		layout.prop(self, "target")
		layout.prop(self, "insert_keyframe")

