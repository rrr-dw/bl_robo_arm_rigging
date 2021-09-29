from typing import Callable, Optional, Union
import bpy
import re
from bpy.types import Object
from mathutils import Vector,Matrix
from .Joint import Joint
from functools import reduce
from itertools import islice


def add_empty(collection:Optional[bpy.types.Collection], name:str, locMat:Matrix, show_name:bool, parent:Optional[Object]):
	o:bpy.types.Object = bpy.data.objects.new(name, None)
	o.empty_display_type='ARROWS'
	if collection:
		collection.objects.link(o)
	return o

def iterate_successive_two_child_empty(base:bpy.types.Object):
	children = [c for c in base.children if c.data == None]
	for child in children:
		grandchildren = [c for c in child.children if c.data ==None]

		for gchild in grandchildren:
			yield child,gchild

def iterate_child_joint(base:bpy.types.Object):
	for e1,e2 in iterate_successive_two_child_empty(base):
		joint = Joint.get_joint_from_two_empties(e1,e2)
		if joint!=None:
			yield joint,e2

def walk_chained_joints(base:bpy.types.Object):
	while True:

		joint,base = next(iterate_child_joint(base),(None,None))
		if joint == None:
			break
		yield joint

def walk_chained_empties(base: bpy.types.Object):
	if base == None or base.data !=None:
		return
	while True:

		children = [c for c in base.children if c.data == None]
		if len(children)==0:
			yield base
			return
		else:
			prev_base = base
			base = children[0]
			yield prev_base

class SerialChain:
	joints: list[Joint]
	_base:Union[Matrix,Callable[[],Matrix]]
	
	def __init__(self,joints=[], base=None):
		self.joints = joints
		if base:
			self._base = base
		else:
			self._base = Matrix.Identity(4)

	@classmethod
	def create_from_base_empty(cls, obj:bpy.types.Object):
		if obj.data != None:
			return None
		joints = [j for j in walk_chained_joints(obj)]
		return cls(joints,obj.matrix_local)
		

	def global_mat(self,i:int):
		if i<0:
			i = len(self.joints)+i

		return reduce(lambda prv,nxt: prv @ nxt, islice(self.mats(),i+2))

	def mats(self):
		return self.base, *(j.mat() for j in self.joints)

	def dM_dqi(self,i:int):
		res = self.base
		for j,joint in enumerate(self.joints):
			if j == i:
				res = res @ joint.dmat_dq()
			else:
				res = res @ joint.mat()

		return res

	def dM_dpi(self,i:int)->Matrix:
		return self.dM_dqi(i) * self.joints[i].dq_dp

	def apply_dq(self,dq:Vector):
		for i,joint in enumerate(self.joints):
			joint.q = joint.q+dq[i]

	def apply_dp(self,dp:Vector):
		for i,joint in enumerate(self.joints):
			joint.p = joint.p+dp[i]

	@property
	def base(self):
		if callable(self._base):
			return self._base()
		else:
			return self._base
	@base.setter
	def base(self,val):
		self._base = val

	def as_empties(self, col:Optional[bpy.types.Collection], show_name:Optional[bool]=None, generate_driver:bool=True, lock_constant:Optional[bool]=None, original_base:Optional[Object]=None, insert_keyframe:bool=False):
		res:list[bpy.types.Object] = []

		originals = walk_chained_empties(original_base)
		prev = next(originals,None) or bpy.data.objects.new("Serial Link", None)
		prev.matrix_local=self.base
		if show_name is not None:
			prev.show_name = show_name
		if col and prev.name not in col.objects:
			col.objects.link(prev)
		res.append(prev)

		for k in res[0].keys():
			if re.fullmatch(r"q[0-9]+",k):
				del res[0][k]

		for i,joint in enumerate(self.joints):
			empties,driver_variable = joint.as_empties(generate_driver,lock_constant,originals)
			empties[0].name = "joint_base_"+"{:0>3d}".format(i)
			empties[1].name = "joint_"+"{:0>3d}".format(i)
			if show_name is not None:
				empties[1].show_name = show_name

			for empty in empties:
				if col and empty.name not in col.objects:
					col.objects.link(empty)
			
			if generate_driver:
				res[0][f"q{i}"] = joint.q
				driver_variable.targets[0].id = res[0]
				driver_variable.targets[0].data_path=f'["q{i}"]'

				if insert_keyframe:
					res[0].keyframe_insert(f'["q{i}"]')

			empties[0].parent = prev
			prev = empties[1]
			res.extend(empties)

		if generate_driver:
			res[0]['_RNA_UI'] ={f"q{i}":{"max":joint.q_max,"min":joint.q_min} for i,joint in enumerate(self.joints)}

		for left_original in originals:
			bpy.data.objects.remove(left_original)
		return res
