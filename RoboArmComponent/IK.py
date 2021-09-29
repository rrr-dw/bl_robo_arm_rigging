import numpy as np
from mathutils import Vector
from .SerialChain import SerialChain

def get_J_q(sc:SerialChain):
	vecs = []
	for i in range(len(sc.joints)):
		vecs.append(sc.dM_dqi(i).translation)
	return np.stack(vecs,1)


def get_J_p(sc: SerialChain):
	vecs = []
	for i in range(len(sc.joints)):
		vecs.append(sc.dM_dpi(i).translation)
	return np.stack(vecs, 1)

def solve_IK(sc:SerialChain, J:np.ndarray, target:Vector):
	d_pos = target-sc.global_mat(-1).translation
	J_pinv = np.linalg.pinv(J)
	res:Vector
	res = J_pinv @ d_pos

	return Vector(res)

def apply_IK(sc:SerialChain, target:Vector, iteration:int=1, constrained:bool=False, tolerance_min:float=0.00001):
	if len(target)!=3:
		return None

	best_q = None
	best_d_pos_sq = float('inf')
	for i in range(iteration):
		tip_prev = sc.global_mat(-1).translation
		if constrained:
			dp = solve_IK(sc, get_J_p(sc), target)
			mag_sq_avg = dp.length_squared/len(dp)
			sc.apply_dp(dp)
		else:
			dq = solve_IK(sc, get_J_q(sc), target)
			mag_sq_avg = dq.length_squared/len(dq)
			sc.apply_dq(dq)

		d_pos_sq = (target-sc.global_mat(-1).translation).length_squared
		if d_pos_sq<best_d_pos_sq:
			best_q = [joint.q for joint in sc.joints]

		d_tip: Vector = sc.global_mat(-1).translation - tip_prev

		# print("iteration",i,d_tip.length_squared,mag_sq_avg)

		if mag_sq_avg < tolerance_min:
		# if d_tip.length_squared < tolerance_min or mag_sq_avg < tolerance_min:
			break

	if best_q:
		for i,joint in enumerate(sc.joints):
			joint.q = best_q[i]
