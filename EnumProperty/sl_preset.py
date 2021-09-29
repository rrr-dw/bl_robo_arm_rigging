import bpy
EnumProperty_sl_preset = bpy.props.EnumProperty(items=(
    ('EMPTY', "Empty", ""),
   	('SCARA', "SCARA", ""),
	('STANFORD',"Stanford Arm",""),
	('CARTESIAN',"Cartesian Coordinate (PPP)",""),
	('CYLINDRICAL',"Cylindrical Coordinate (RPPR)",""),
   	('SPHERICAL_RRR', "Spherical Coordinate (RRR)", ""),
   	('SPHERICAL_RRP', "Spherical Coordinate (RRP)", ""),
   	('LAST', "Clone Last Serial Link", ""),
   	('EDIT', "Modify Active Serial Link", ""),
))
