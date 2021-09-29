from typing import Optional
from ..EnumProperty import EnumProperty_scene_objects, EnumProperty_sl_preset
import bpy
from bpy.types import Context, Object, UILayout
from ..RoboArmComponent import SerialChain, Joint, walk_chained_empties
from .RBA_PG_joint_dh import RBA_PG_joint_dh
import itertools

class RBA_OP_add_sl_list_op(bpy.types.Operator):
	'''internal operator to mutate serial link generation settings'''
	bl_idname = "rba.add_sl_list_op"
	bl_label = ""
	bl_options={'INTERNAL',}

	action: bpy.props.EnumProperty(items=(  # type: ignore
		('ADD', "add", ""),
		('CLR', "clear", ""),
		('DEL', "del", "")
	)) 
	p1: bpy.props.IntProperty() # type: ignore

	def execute(self, context:Context):
		ls = context.window_manager.sl_add_op_option.joints
		if(self.action=='ADD'):
			nw = ls.add()
		elif(self.action=='DEL'):
			ls.remove(self.p1)
		elif(self.action=="CLR"):
			ls.clear()

		return {'FINISHED'}

	
class RBA_OP_add_sl(bpy.types.Operator):
	'''Construct a serial link'''
	bl_idname = "rba.add_sl"
	bl_label = "Add Serial Link"
	bl_options = {'REGISTER','UNDO'}

	show_name: bpy.props.BoolProperty(name="Show name of each frame", default=True)  # type: ignore
	generate_driver: bpy.props.BoolProperty(name="Generate driver for joint variables", description="Generate driver that can be used to animate forward kinematics. Joints can be moved directly if it isn't generated", default=True)  # type: ignore
	lock_constant: bpy.props.BoolProperty(name="Lock constant parameters", description="Prevent changing constant parameters. Constant parameters(= Non-joint variables) can be changed interactively if it's unchecked", default=True)  # type: ignore
	active_tab: bpy.props.EnumProperty(items=(  # type: ignore
		('GENERAL', "General", ""),
		('DH', "DH params", ""),
		('CONSTRAINT', "Constraint", ""),
	))
	preset: EnumProperty_sl_preset  # type: ignore
	obj_to_be_replaced: EnumProperty_scene_objects  # type: ignore

	def execute(self, context:Context):
		option = context.window_manager.sl_add_op_option
		ls = option.joints
		col = context.collection

		active_obj = context.view_layer.objects.active
		cursor_matrix = bpy.context.scene.cursor.matrix
		sc = SerialChain()
		sc.base = cursor_matrix if active_obj==None else active_obj.matrix_local
		sc.joints = []

		j:RBA_PG_joint_dh
		for j in ls:
			joint = Joint(j.d,j.theta,j.a,j.alpha,j.is_prismatic,z_first=option.z_first)
			if j.is_constrained:
				joint.q_min = j.q_min
				joint.q_max = j.q_max
			sc.joints.append(joint)

		empties = sc.as_empties(col,self.show_name,self.generate_driver,self.lock_constant,context.view_layer.objects.active)

		for o in context.scene.objects:
			o.select_set(False)

		for empty in empties:
			empty.select_set(True)

		bpy.context.view_layer.objects.active = empties[0]

		return {'FINISHED'}

	def invoke(self,context:Context,event):
		if self.obj_to_be_replaced!=0 and self.obj_to_be_replaced in bpy.data.objects:
			context.view_layer.objects.active = bpy.data.objects[self.obj_to_be_replaced]

		elif self.preset == 'EDIT':
			if bpy.context.object ==None:
				self.report({'ERROR_INVALID_CONTEXT'}, "Set a serial link as a active object first")
				return {'CANCELLED'}
		else:
			context.view_layer.objects.active = None


		bpy.ops.rba.load_sl_preset(preset=self.preset)

		return self.execute(context)


	def draw(self,context:Context):
		wm = context.window_manager
		layout = self.layout

		box = layout.box()
		box.prop(self, "show_name")
		box.prop(wm.sl_add_op_option, "z_first")
		box.prop(self, "lock_constant")
		box.prop(self, "generate_driver")

		row = layout.row()
		op = row.operator("rba.add_sl_list_op",text="Add Joint",icon='ADD')
		op.action = 'ADD'
		row.operator("rba.add_sl_list_op",text="Clear", icon='TRASH').action = 'CLR'

		if len(wm.sl_add_op_option.joints)==0:
			return

		layout.row().prop(self, "active_tab", expand=True)

		box = layout.box()
		box = box.split(factor=.05,align=True)
		col_id = box.column(align=True)
		col_id.label(text="#")
		box = box.split(factor=.09, align=True)
		col_del = box.column(align=True)
		col_del.label(text='Del')

		col_prismatic:UILayout

		col_d:UILayout
		col_theta:UILayout
		col_a:UILayout
		col_alpha:UILayout

		col_constrained:UILayout
		col_qMin:UILayout
		col_qMax:UILayout

		if self.active_tab=='GENERAL':
			col_prismatic = box.column(heading="Type", align=True)

		elif self.active_tab == 'DH':
			box = box.split(factor=1/4, align=True)
			col_d = box.column(heading="d",align=True)
			box = box.split(factor=1/3, align=True)
			col_theta = box.column(heading="θ",align=True)
			box = box.split(factor=1/2, align=True)
			col_a = box.column(heading="a (r)",align=True)
			col_alpha = box.column(heading="α", align=True)

		elif self.active_tab == 'CONSTRAINT':
			col_constrained=box.column(heading="Constrained",align=True)
			col_qMin = box.column(align=True)
			col_qMin.label(text="Min(q)")
			col_qMax = box.column(align=True)
			col_qMax.label(text="Max(q)")


		id_count=0
		item:RBA_PG_joint_dh
		for item in wm.sl_add_op_option.joints:
			col_id.label(text=f'{id_count}')
			op = col_del.operator("rba.add_sl_list_op", text="", icon='REMOVE')
			op.action = 'DEL'
			op.p1 = id_count
			id_count = id_count+1
			
			if self.active_tab == 'GENERAL':
				col_prismatic.prop(item, "is_prismatic",text="prismatic" if item.is_prismatic else "revolute",toggle=1)

			elif self.active_tab == 'DH':
				col_d.prop(item, "d", text="")
				col_theta.prop(item, "theta", text="")
				col_a.prop(item, "a", text="")
				col_alpha.prop(item, "alpha", text="")

			elif self.active_tab == 'CONSTRAINT':
				col_constrained.prop(item, "is_constrained",text="")
				if item.is_constrained==False:
					col_qMin.label(text="-")
					col_qMax.label(text="-")
				elif item.is_prismatic:
					col_qMin.prop(item, "q_min_d",text="",)
					col_qMax.prop(item, "q_max_d",text="")
				else:
					col_qMin.prop(item, "q_min_theta",text="")
					col_qMax.prop(item, "q_max_theta",text="")
			
