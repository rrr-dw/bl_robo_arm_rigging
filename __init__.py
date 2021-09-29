# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

bl_info = {
    "name": "Robo Arm :: Rigging",
    "author": "nw",
    "description": "Construct Serial Link from DH parameters using only vanilla features.",
    "blender": (2, 80, 0),
    "version": (0, 0, 1),
    "location": "View 3D > Add > Serial Link",
    "warning": "",
    "category": "Rigging"
}

from .blClasses import *
import bpy


def register():
    for c in blClasses:
        bpy.utils.register_class(c)
    bpy.types.WindowManager.sl_add_op_option = bpy.props.PointerProperty(type=RBA_PG_add_sl_op)
    bpy.types.VIEW3D_MT_add.append(RBA_add_sl_draw_func)

def unregister():
    bpy.types.VIEW3D_MT_add.remove(RBA_add_sl_draw_func)
    del bpy.types.WindowManager.sl_add_op_option
    for c in blClasses:
        bpy.utils.unregister_class(c)
