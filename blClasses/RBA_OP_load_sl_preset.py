from ..RoboArmComponent import SerialChain
from .RBA_PG_add_sl_op import RBA_PG_add_sl_op
from ..EnumProperty import EnumProperty_sl_preset # type: ignore
from .RBA_OP_add_sl import RBA_PG_joint_dh
from math import radians
import bpy
from bpy.types import Context, Event

class RBA_OP_load_sl_preset(bpy.types.Operator):
	'''operator to add a predefined serial link'''
	bl_idname = "rba.load_sl_preset"
	bl_label = "Add Serial Link"
	bl_options = {'INTERNAL',}
	preset: EnumProperty_sl_preset # type:ignore

	def execute(self, context:Context):
		if self.preset != 'LAST':
			bpy.ops.rba.add_sl_list_op(action='CLR')

		if self.preset == 'SCARA':
			preset_SCARA(context)

		elif self.preset == 'STANFORD':
			preset_stanford(context)

		elif self.preset == 'CYLINDRICAL':
			preset_cylindrical(context)

		elif self.preset == 'SPHERICAL_RRR':
			preset_spherical_rrr(context)

		elif self.preset == 'SPHERICAL_RRP':
			preset_spherical_rrp(context)

		elif self.preset == 'CARTESIAN':
			preset_cartesian(context)

		elif self.preset == 'EDIT':
			preset_modify(context)

		elif self.preset == 'EMPTY':
			pass

		return {'FINISHED'}

def add_joint():
	bpy.ops.rba.add_sl_list_op(action='ADD')

def z_first_convention(enable:bool=True):
	bpy.context.window_manager.sl_add_op_option.z_first=enable

def preset_SCARA(context:Context):
	ls:list[RBA_PG_joint_dh] = context.window_manager.sl_add_op_option.joints
	z_first_convention()

	add_joint()
	ls[-1].set(1, 0, 1,0)

	add_joint()
	ls[-1].set(.2, 0, 1, 0)

	add_joint()
	ls[-1].set(-.2, 0, 0, radians(180),True)
	ls[-1].constrain(True,-1.2,-.2)


def preset_stanford(context:Context):
	ls:list[RBA_PG_joint_dh] = context.window_manager.sl_add_op_option.joints
	z_first_convention()

	add_joint()
	ls[-1].set(1.4, 0, 0,radians(-90))

	add_joint()
	ls[-1].set(.2, radians(90), 0, radians(-90))
	ls[-1].constrain(True, radians(-90), radians(90))

	add_joint()
	ls[-1].set(1, radians(-90), 0, 0,True)
	ls[-1].constrain(True, 1,2)

	add_joint()
	ls[-1].set(.2, 0, 0, radians(-90))

	add_joint()
	ls[-1].set(0, 0, 0, radians(90))
	ls[-1].constrain(True, radians(-25), radians(25))

	add_joint()
	ls[-1].set(.2, 0, 0, 0)

def preset_cylindrical(context:Context):
	ls: list[RBA_PG_joint_dh] = context.window_manager.sl_add_op_option.joints
	z_first_convention()
	
	add_joint()
	ls[-1].set(0,0,0,0)

	add_joint()
	ls[-1].set(2.2,0,0,radians(90),True)
	ls[-1].constrain(True,.2,2.2)

	add_joint()
	ls[-1].set(1.4, 0, 0, 0,True)
	ls[-1].constrain(True,.4,1.4)

	add_joint()
	ls[-1].set(.2,0,0,0)
	
def preset_spherical_rrr(context:Context):
	ls: list[RBA_PG_joint_dh] = context.window_manager.sl_add_op_option.joints
	z_first_convention()
	
	add_joint()
	ls[-1].set(0, 0, 0, radians(90))

	add_joint()
	ls[-1].set(.2, radians(45), 1, 0)
	ls[-1].constrain(True,radians(-45),radians(45))

	add_joint()
	ls[-1].set(0, radians(-60), 1, 0)
	ls[-1].constrain(True,radians(-135),radians(135))
	pass

def preset_spherical_rrp(context: Context):
	ls: list[RBA_PG_joint_dh] = context.window_manager.sl_add_op_option.joints
	z_first_convention()
	
	add_joint()
	ls[-1].set(0, 0, 0, radians(90))

	add_joint()
	ls[-1].set(.2, radians(135), 0, radians(90))
	ls[-1].constrain(True,radians(45),radians(135))

	add_joint()
	ls[-1].set(2.5, 0, 0, 0,True)
	ls[-1].constrain(True,.5,3)

def preset_cartesian(context:Context):
	ls:list[RBA_PG_joint_dh] = context.window_manager.sl_add_op_option.joints
	z_first_convention()
	
	add_joint()
	ls[-1].set(2.5, radians(90), 0, radians(90),True)
	ls[-1].constrain(True,-5,5)

	add_joint()
	ls[-1].set(1, radians(90), 0,radians(90),True)
	ls[-1].constrain(True,-1,1)

	add_joint()
	ls[-1].set(1, 0, 0,0,True)
	ls[-1].constrain(True,0,2)

def preset_modify(context:Context):
	option: RBA_PG_add_sl_op = context.window_manager.sl_add_op_option
	ls:list[RBA_PG_joint_dh] = option.joints

	sc = SerialChain.create_from_base_empty(bpy.context.object)
	option.z_first = True if len(sc.joints)==0 else sc.joints[0].z_first

	for joint in sc.joints:
		add_joint()
		ls[-1].copy_from_joint(joint)
