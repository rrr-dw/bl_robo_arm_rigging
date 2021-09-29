from math import radians
import bpy
from bpy.types import Context, Event

class RBA_MT_add_sl(bpy.types.Menu):
	"""Add Serial Link"""
	bl_label = "Serial Link"
	bl_idname = "RBA_MT_add_sl"

	def draw(self, context:Context):
		layout = self.layout
		layout.operator_context='INVOKE_DEFAULT'
		layout.operator_enum("rba.add_sl", "preset")
	
def RBA_add_sl_draw_func(self:bpy.types.Menu, context):
	layout = self.layout
	layout.separator()
	layout.menu("RBA_MT_add_sl",text="Serial Link")
