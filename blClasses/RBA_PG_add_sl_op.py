from .RBA_PG_joint_dh import RBA_PG_joint_dh
import bpy

class RBA_PG_add_sl_op(bpy.types.PropertyGroup):
	joints: bpy.props.CollectionProperty(type=RBA_PG_joint_dh) # type: ignore
	z_first: bpy.props.BoolProperty(name="Apply variable screw before constant screw",
	                                description="This option is for the alternative convention. You may want to enable it", default=True)  # type: ignore
	
