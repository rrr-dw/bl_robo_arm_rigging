from ..EnumProperty.sl_preset import EnumProperty_sl_preset # type: ignore
from math import radians
from typing import Any, Callable, Literal
import bpy
from bpy.types import Context, Event, UILayout
from ..RoboArmComponent import SerialChain,Joint


def setter_factory(variant:Literal['theta','d'],is_min):
	q_min_k = f"_q_min_{variant}"
	q_max_k = f"_q_max_{variant}"
	get_q_min = getter_factory(variant,True)
	get_q_max = getter_factory(variant,False)
	
	if is_min:
		def setter(self,val):
			if val>get_q_max(self):
				val = get_q_max(self)
			self[q_min_k] = val
		return setter

	else:
		def setter(self, val):
			if val < get_q_min(self):
				val = get_q_min(self)
			self[q_max_k] = val

		return setter


def getter_factory(variant: Literal['theta', 'd'], is_min):
	q_min_k = f"_q_min_{variant}"
	q_max_k = f"_q_max_{variant}"

	if is_min:
		return lambda self: float("-inf") if q_min_k not in self else self[q_min_k]
	else:
		return lambda self: float("inf") if q_max_k not in self else self[q_max_k]


def MinMaxProperty(variant: Literal['theta', 'd'], is_min):
	setter = setter_factory(variant, is_min)
	getter = getter_factory(variant, is_min)
	if variant=='theta':
		return bpy.props.FloatProperty(subtype='ANGLE', step=15, set=setter, get=getter)
	else:
		return bpy.props.FloatProperty(subtype='DISTANCE', set=setter, get=getter)


DistanceProperty = bpy.props.FloatProperty(subtype='DISTANCE')
AngleProperty = bpy.props.FloatProperty(subtype='ANGLE', step=15)
class RBA_PG_joint_dh(bpy.types.PropertyGroup):
	d: DistanceProperty # type:ignore
	theta: AngleProperty # type:ignore
	a: DistanceProperty # type:ignore
	alpha: AngleProperty # type:ignore
	is_prismatic: bpy.props.BoolProperty(name="is prismatic", default=False)  # type:ignore
	is_constrained: bpy.props.BoolProperty(name="is constrained",default=False)  # type:ignore
	q_min_theta: MinMaxProperty('theta',True) # type:ignore
	q_max_theta: MinMaxProperty('theta',False) # type:ignore
	q_min_d: MinMaxProperty('d',True) # type:ignore
	q_max_d: MinMaxProperty('d',False) # type:ignore

	def set(self,d,theta,a,alpha,is_prismatic=False):
		self.d=float(d)
		self.theta=float(theta)
		self.a=float(a)
		self.alpha=float(alpha)
		self.is_prismatic = is_prismatic

	def constrain(self,is_constrained:bool,q_min:float=float('-inf'),q_max:float=float('inf')):
		self.is_constrained = is_constrained
		self.q_min = float('-inf') if q_min==None else float(q_min)
		self.q_max = float('inf') if q_max==None else float(q_max)
	
	def copy_from_joint(self,joint:Joint):
		self.set(joint.d, joint.theta, joint.a, joint.alpha, joint.is_prismatic)
		if joint.is_constrained:
			self.constrain(joint.is_constrained,joint.q_min,joint.q_max)

	@property
	def q_min(self):
		if not self.is_constrained:
			return float('-inf')
		elif self.is_prismatic:
			return self.q_min_d
		else:
			return self.q_min_theta
	
	@q_min.setter
	def q_min(self,val):
		if self.is_prismatic:
			self.q_min_d=val
		else:
			self.q_min_theta=val

	@property
	def q_max(self):
		if not self.is_constrained:
			return float('inf')
		elif self.is_prismatic:
			return self.q_max_d
		else:
			return self.q_max_theta

	@q_max.setter
	def q_max(self,val):
		if self.is_prismatic:
			self.q_max_d=val
		else:
			self.q_max_theta=val
