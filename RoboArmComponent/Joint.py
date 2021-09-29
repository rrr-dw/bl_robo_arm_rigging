import math
from .. import my_math
from typing import Generator, Optional
import bpy
from bpy.types import Driver, Object
from mathutils import Vector,Matrix
from math import cos, radians, sin

abs_epsilon:float = 0.001

def new_empty(locMat: Matrix, iter: Generator[Object, None, None]):
	o: bpy.types.Object = next(iter,None) or bpy.data.objects.new("T", None)
	o.empty_display_type = 'ARROWS'
	o.matrix_local = locMat
	o.parent=None
	return o

class Joint:
	d:float
	theta:float
	a:float
	alpha:float
	is_prismatic:bool
	q_min:float
	q_max:float
	z_first:bool

	def __init__(self,d,theta,a,alpha,is_prismatic=True,q_min=float('-inf'),q_max=float('inf'),z_first=True):
		self.d = d
		self.theta = theta
		self.a = a
		self.alpha = alpha
		self.is_prismatic = is_prismatic
		self.q_min = float('-inf') if q_min==None else q_min
		self.q_max = float('inf') if q_max==None else q_max
		self.z_first=z_first
	
		
	@staticmethod
	def get_x_half_joint_from_empty(obj:bpy.types.Object):
		if obj.data != None:
			return None

		if not math.isclose(obj.location[1], 0, abs_tol=abs_epsilon) or not math.isclose(obj.location[2], 0, abs_tol=abs_epsilon):
			return None
		
		if obj.rotation_mode == 'QUATERNION' or obj.rotation_mode == 'AXIS_ANGLE':
			return None
		if not math.isclose(obj.rotation_euler[1],0,abs_tol=abs_epsilon) or not math.isclose(obj.rotation_euler[2],0,abs_tol=abs_epsilon):
			return None


		a = obj.location[0]
		alpha = obj.rotation_euler[0]
		return a,alpha

	
	@staticmethod
	def get_z_half_joint_from_empty(obj:bpy.types.Object):
		if obj.data != None:
			return None

		if not math.isclose(obj.location[0], 0, abs_tol=abs_epsilon) or not math.isclose(obj.location[1], 0, abs_tol=abs_epsilon):
			return None
		
		if obj.rotation_mode == 'QUATERNION' or obj.rotation_mode == 'AXIS_ANGLE':
			return None
		if not math.isclose(obj.rotation_euler[0], 0, abs_tol=abs_epsilon) or not math.isclose(obj.rotation_euler[1], 0, abs_tol=abs_epsilon):
			return None
		if obj.lock_location[2] and obj.lock_rotation[2]:
			return None

		is_rot_drived = obj.animation_data.drivers.find("rotation_euler", index=2)!=None
		is_loc_drived = obj.animation_data.drivers.find("location", index=2)!=None
		if not is_rot_drived and not is_loc_drived:
			return None

		d = obj.location[2]
		theta = obj.rotation_euler[2]
		is_prismatic = is_loc_drived

		if len(obj.constraints)==0:
			return d,theta,is_prismatic,None,None
		elif len(obj.constraints)>1:
			return None
		
		if is_prismatic and obj.constraints[0].type == 'LIMIT_LOCATION':
			c = obj.constraints[0]
			if c.owner_space != 'LOCAL':
				return None
			min_q, max_q = None, None
			if c.use_min_z:
				min_q = c.min_z
			if c.use_max_z:
				max_q = c.max_z
			return d, theta, is_prismatic, min_q, max_q

		elif not is_prismatic and obj.constraints[0].type == 'LIMIT_ROTATION':
			c = obj.constraints[0]
			if c.use_limit_z and c.owner_space=='LOCAL':
				return d,theta,is_prismatic,c.min_z,c.max_z
			else:
				return None
			

		else:
			return None

	@classmethod
	def get_joint_from_two_empties(cls,obj_prev:bpy.types.Object,obj_next:bpy.types.Object):
		z = cls.get_z_half_joint_from_empty(obj_prev)
		z_first = True
		if z==None:
			z = cls.get_z_half_joint_from_empty(obj_next)
			z_first = False
		if z==None:
			return None
		x = cls.get_x_half_joint_from_empty(obj_next if z_first else obj_prev)
		if x==None:
			return None

		a,alpha = x
		d,theta,is_prismatic,min_q,max_q = z

		return cls(d,theta,a,alpha,is_prismatic,min_q,max_q,z_first)
		
	@property
	def is_revolute(self):
		return not self.is_prismatic

	@is_revolute.setter
	def is_revolute(self, isRevolute:bool):
		self.is_prismatic = not isRevolute

	@property
	def is_constrained(self):
		return self.is_bounded_below or self.is_bounded_above

	@property
	def is_bounded_below(self):
		return self.q_min != float("-inf")

	@property
	def is_bounded_above(self):
		return self.q_max != float("inf")

	@property
	def q(self):
		return self.d if self.is_prismatic else self.theta

	@q.setter
	def q(self, q:float):
		if q<self.q_min:
			q=self.q_min
		elif q>self.q_max:
			q=self.q_max

		if self.is_prismatic:
			self.d = q
		elif self.is_revolute:
			self.theta = q

	@property
	def p(self):
		if not self.is_constrained:
			return self.q
		elif self.is_bounded_above and self.is_bounded_below:
			return my_math.q_bounded_both_inv(self.q,self.q_min,self.q_max)
		elif self.is_bounded_above:
			return my_math.q_bounded_above_inv(self.q,self.q_max)
		else:
			return my_math.q_bounded_below_inv(self.q,self.q_min)
	
	@p.setter
	def p(self, p:float):
		if not self.is_constrained:
			self.q=p
		elif self.is_bounded_above and self.is_bounded_below:
			self.q = my_math.q_bounded_both(p,self.q_min,self.q_max)
		elif self.is_bounded_above:
			self.q = my_math.q_bounded_above(p, self.q_max)
		else:
			self.q = my_math.q_bounded_below(p,self.q_min)

	@property
	def dq_dp(self):
		if not self.is_constrained:
			return 1
		elif self.is_bounded_above and self.is_bounded_below:
			return my_math.q_bounded_both_1(self.p, self.q_min, self.q_max)
		elif self.is_bounded_above:
			return my_math.q_bounded_above_1(self.p)
		else:
			return my_math.q_bounded_below_1(self.p)

	def dMat(self):
		return Matrix.Translation((0,0,self.d))

	def ddMat_dq(self):
		return Matrix.Translation((0,0,1))

	def thetaMat(self):
		return Matrix.Rotation(self.theta,4,'Z')

	def dthetaMat_dq(self):
		return Matrix(
			((-sin(self.theta),-cos(self.theta),0,0),
			(cos(self.theta), -sin(self.theta), 0, 0),
			(0,0,0,0),
			(0,0,0,0))
		)

	def aMat(self):
		return Matrix.Translation((self.a,0,0))

	def alphaMat(self):
		return Matrix.Rotation(self.alpha,4,'X')

	def zScMat(self)->Matrix:
		return self.dMat() @ self.thetaMat()

	def dzScMat_dq(self)->Matrix:
		if self.is_prismatic:
			return self.ddMat_dq() @ self.thetaMat()
		else:
			return self.dMat() @ self.dthetaMat_dq()

	def xScMat(self)->Matrix:
		return self.aMat() @ self.alphaMat()

	def mat(self)->Matrix:
		if self.z_first:
			return self.zScMat() @ self.xScMat()
		else:
			return self.xScMat() @ self.zScMat()

	def dmat_dq(self) -> Matrix:
		if self.z_first:
			return self.dzScMat_dq() @ self.xScMat()
		else:
			return self.xScMat() @ self.dzScMat_dq()

	def empty_x(self, lock_constant: bool, iter: Generator[Object, None, None]):
		empty = new_empty(self.xScMat(),iter)
		empty.lock_location[0:2] = [True, True]
		empty.lock_rotation[0:2] = [True, True]
		if lock_constant is not None:
			empty.lock_location[2] = lock_constant
			empty.lock_rotation[2] = lock_constant

		return empty
	
	def empty_z(self, generate_driver: bool, lock_constant: Optional[bool], iter: Generator[Object, None, None]):
		empty = new_empty(self.zScMat(),iter)
		empty.lock_location[0:2] = [True,True]
		empty.lock_rotation[0:2] = [True,True]
		if lock_constant is not None:
			empty.lock_location[2]=lock_constant
			empty.lock_rotation[2]=lock_constant

		if self.is_prismatic:
			empty.lock_location[2]=False
		else:
			empty.lock_rotation[2]=False

		if generate_driver:
			if self.is_prismatic:
				empty.driver_remove("location",2)
				driver = empty.driver_add("location",2).driver
			else:
				empty.driver_remove("rotation_euler",2)
				driver= empty.driver_add("rotation_euler",2).driver

			driver.type='SUM'
			v = driver.variables.new()
			v.type='SINGLE_PROP'

		CONSTR_NAME = "_RBA_joint"
		prev_joint = empty.constraints.get(CONSTR_NAME)
		if self.is_constrained:
			if self.is_prismatic:
				new_joint = empty.constraints.new(type='LIMIT_LOCATION')
				new_joint.owner_space = 'LOCAL'
				if self.q_min != float("-inf"):
					new_joint.use_min_z = True
					new_joint.max_z = self.q_max

				if self.q_max != float("inf"):
					new_joint.use_max_z = True
					new_joint.min_z = self.q_min

			else:
				new_joint = empty.constraints.new(type='LIMIT_ROTATION')
				new_joint.owner_space = 'LOCAL'
				new_joint.use_limit_z = True
				new_joint.max_z = self.q_max
				new_joint.min_z = self.q_min

			if prev_joint:
				from_index = empty.constraints.find(new_joint.name)
				to_index = empty.constraints.find(prev_joint.name)
				if to_index == -1 or from_index == -1:
					raise AssertionError("Failed to setup constraints")
				empty.constraints.move(from_index, to_index)
				empty.constraints.remove(prev_joint)

			new_joint.name = CONSTR_NAME
		elif prev_joint is not None:
			empty.constraints.remove(prev_joint)


		return empty

	def as_empties(self, generate_driver:bool, lock_constant:Optional[bool],iter:Generator[Object,None,None]):
		if self.z_first:
			empties = [
				self.empty_z(generate_driver, lock_constant, iter),
				self.empty_x(lock_constant, iter),
			]
			empty_z = empties[0]
		else:
			empties = [
				self.empty_x(lock_constant,iter),
				self.empty_z(generate_driver,lock_constant,iter)
			]
			empty_z = empties[1]

		
		empties[0].empty_display_type='SPHERE'
		empties[0].empty_display_size=0.1
		empties[1].parent = empties[0]
		if generate_driver:
			return empties,empty_z.animation_data.drivers[0].driver.variables[0]
		else:
			return empties, None
