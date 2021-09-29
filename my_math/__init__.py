from math import sin,cos,radians,asin,acos

EPSILON = 0.0001

# p-> normalized bounded q
def identity_sin(p:float):
	print("identity_sin",p)
	if p<0:
		return p
	elif p<radians(90):
		return sin(p)
	else:
		return 1

def sin_identity(p: float):
	print("sin_identity",p)
	if 0<p:
		return p
	elif radians(-90)<p:
		return sin(p)
	else:
		return -1

def sin_sin(p:float):
	print("sin_sin",p)
	if radians(-90)<p<radians(90):
		return sin(p)
	elif p<0:
		return -1
	else:
		return 1

# p-> normalized bounded q'
def identity_sin_1(p: float):
	print("identity_sin_1",p)
	if p < 0:
		return 1
	elif p < radians(90):
		return max(EPSILON,cos(p))
	else:
		return max(EPSILON,0)

def sin_identity_1(p: float):
	print("sin_identity_1",p)
	if 0 < p:
		return 1
	elif radians(-90) < p:
		return max(EPSILON,cos(p))
	else:
		return max(EPSILON, 0)

def sin_sin_1(p:float):
	print("sin_sin_1",p)
	if radians(-90) < p < radians(90):
		return max(EPSILON, cos(p))
	else:
		return max(EPSILON, 0)

# normalized bounded q -> p
def sin_sin_inv(q: float):
	print("sin_sin_inv",q)
	if -1.0 <= q <= 1.0:
		return asin(q)
	elif q<0:
		return float('-inf') #radians(-90)
	else:
		return float('inf') #radians(90)

def identity_sin_inv(q: float):
	print("identity_sin_inv",q)
	if q<0:
		return q
	elif q<=1:
		return asin(q)
	else:
		return float('inf') #radians(90)

def sin_identity_inv(q: float):
	print("sin_identity_inv",q)
	if 0<q:
		return q
	elif 1<=q:
		return asin(q)
	else:
		return float('-inf') #radians(-90)

# p -> bounded q
def q_bounded_above(p:float,upper_bound:float):
	print("q_bounded_above",p)
	return identity_sin(p)+upper_bound-1

def q_bounded_below(p: float, lower_bound: float):
	print("q_bounded_below",p)
	return sin_identity(p)+1-lower_bound

def q_bounded_both(p:float, lower_bound:float, upper_bound:float):
	print("q_bounded_both",p)
	radius = (upper_bound-lower_bound)/2
	return radius*sin_sin(p/radius) + (upper_bound+lower_bound)/2

# bounded q -> p
def q_bounded_above_inv(q:float,upper_bound:float):
	print("q_bounded_above_inv",q)
	return identity_sin_inv(q+1-upper_bound)

def q_bounded_below_inv(q: float, lower_bound: float):
	print("q_bounded_below_inv",q)
	return sin_identity_inv(q-1+lower_bound)

def q_bounded_both_inv(q:float, lower_bound:float, upper_bound:float):
	print("q_bounded_both_inv",q)
	radius = (upper_bound-lower_bound)/2
	return radius*sin_sin_inv((q-(upper_bound+lower_bound)/2)/radius)

# p => bounded q'

def q_bounded_above_1(p:float):
	print("q_bounded_above_1",p)
	return identity_sin_1(p)

def q_bounded_below_1(p: float):
	print("q_bounded_below_1",p)
	return sin_identity_1(p)

def q_bounded_both_1(p:float, lower_bound:float, upper_bound:float):
	print("q_bounded_both_1",p)
	radius = (upper_bound-lower_bound)/2
	return sin_sin_1(p/radius)
