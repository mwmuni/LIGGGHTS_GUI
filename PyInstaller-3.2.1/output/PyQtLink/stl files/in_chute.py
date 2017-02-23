# TUNRA BULK SOLIDS LIGGGHTS DEM SImulation Template
# For technical support, please contact
# Wei Chen: W.Chen@newcastle.edu.aus

#-------------------------------------------------------------------------------------------------
#variable 	NTHREADS equal 8										# OpenMP Threads
#package 	omp ${NTHREADS} force/neigh thread-binding verbose		           # OpenMp Threads binding

# Variables - Declaration & Passon to Simulations
variable	pi  	equal 3.141592654     	# PI
variable 	a	equal	1			# Test number

# Variables - Timestep & Dumpstep
variable 	dt	  	equal	 1e-4				 # Time step
variable 	factor	equal	 1/${dt}                # Steps per second
variable 	dumpstep 	equal	 0.05*${factor}         # save results every dumpstep


# Variable - Particle size distribution
variable 	d1 			equal 	40   	# d=10mm
variable 	d2 			equal 	40   	# d=12mm
variable 	d3 			equal 	40   	# d=14mm
variable 	d4 			equal 	40   	# d=16mm
variable 	d5 			equal 	40   	# d=18mm

variable 	r1 			equal 	${d1}/2000
variable 	r2 			equal 	${d2}/2000
variable 	r3 			equal 	${d3}/2000
variable 	r4 			equal 	${d4}/2000
variable 	r5 			equal 	${d5}/2000

# Variable - particle size fractions
variable 	frac1 		equal 	0.2  
variable 	frac2 		equal 	0.2 
variable 	frac3 		equal 	0.2     
variable 	frac4 		equal 	0.2
variable 	frac5 		equal 	0.2

# Define contact searching distance
variable 	cutoff 		equal 	0.02


# Variables - Particle and wall properties
variable 	cor 	  	equal	0.3     # coefficient of restitution
variable 	dens	  	equal	4400    # Particle density (bulk density * porosity)
variable 	poiss	  	equal	0.3     # Poissons ratio
variable 	youngmod 	equal 1e7     # Young modulus
variable 	ff	  	equal 0.9		# Particle particle friction
variable 	wf 	  	equal	0.4		# Particle wall friction
variable 	rf	  	equal 0.5		# Rolling friction
variable 	CED	  	equal	1e4		# Cohesion Energy Density - [J/m3]
variable 	AED	  	equal	1e4		# Adhesion Energy Density - [J/m3]
variable 	SLR	  	equal	40		# Surfacial liquid volume to solids volume - [%]
variable 	SFT	  	equal	1e5		# Surface tension between solid and liquid - [N/m]
variable 	WFV	  	equal	8.9e-4	# Water fluid viscosity [Pa s]

# Variables - Mass flow rate
variable 	m 	  	equal 	6999	   		# Total Mass to be inserted
variable 	tfill	  	equal 	10	   		# Time for generating particles [s]
variable 	Q	  	equal 	${m}/${tfill} 	# Mass flow rate @ 5000 t/h

# Variables - Definition of times (points when simulation behaviour changes)
variable 	t1       	equal   ${tfill}       	# time for inserting particles
variable 	steps1   	equal   ${t1}*${factor}    	# Convert time to computational steps

######################################################################################################################

# Granular Model and Computational Setting
atom_style		granular	              # Granular style for LIGGGHTS

atom_modify		map array           # The map keyword determines how atom ID lookup is done for molecular problems.
                                     # When the array value is used, each processor stores a lookup table of length N, 
                                     # where N is the total # of atoms in the system. This is the fastest method, 
				              # but a processor can run out of memory to store the table for large simulations. 

boundary		f f f               # Boundary definition in x y z (f=fixed bound., particles will be deleted,
				      	   # m = modified bound., boundaries will be extended,
				      	   # p = periodic bound.)

newton			off                 # This command turns Newton's 3rd law on or off for pairwise interactions. 

communicate		single vel yes	    # This command sets the style of inter-processor communication 
                                      # that occurs each timestep as atom coordinates and other properties 
                                      # are exchanged between neighboring processors.

units			si		      		# [s] [m] [kg] [N]

region			reg block -3.7 1.82 -1.1 10 -2.6 2.2 units box   	# Defines rectangular boundaries in x y z [m]
create_box		2 reg  									# Numbers of atome (particle / wall) types
# type 1: inserted particles
# type 2: belts and walls

neighbor		${cutoff} bin	# Defines parameter for contact searching
neigh_modify	delay 0 		# Define the neighbor list building time

# Material properties required for new pair styles
fix 		m1 all property/global youngsModulus peratomtype ${youngmod} ${youngmod}
fix 		m2 all property/global poissonsRatio peratomtype ${poiss} ${poiss}
fix 		m3 all property/global coefficientRestitution peratomtypepair 2 ${cor} ${cor} &
																			${cor} ${cor}
fix 		m4 all property/global coefficientFriction peratomtypepair 2 ${ff} ${wf}&
									     								 ${wf} 0
fix 		m5 all property/global coefficientRollingFriction peratomtypepair 2 ${rf} ${rf}&
										    									${rf} 0
fix 		m6 all property/global cohesionEnergyDensity peratomtypepair 2 ${CED} ${AED}&
										    							   ${AED} 0
fix		m7 all property/global k_finnie peratomtypepair 2 1.0 1.0 1.0 1.0  # for wear analysis

#-----------------------LIQUID BRIDGING CONTACT MODEL
#fix 		m7 all property/global minSeparationDistanceRatio scalar 1.01
#    (value=value for the minimum separation distance, recommended as 1.01)
#fix 		m8 all property/global maxSeparationDistanceRatio scalar 1.1
#    (value=value for the maximum separation distance, recommended as 1.1)
#fix 		m9 all property/global surfaceLiquidContentInitial scalar ${MC}
#    (value=value for the initial surface liquid volume in % of the solid volume)
#fix 		m10 all property/global surfaceTension scalar ${ST}
#    (value=value for the surface tension of liquid (SI units N/m))
#fix 		m11 all property/global fluidViscosity scalar 0.00089
#    (value=value for the fluidViscosity (SI units Pas))
#fix 		m12 all property/global contactAngle peratomtype 60 60 60
#    (value_i=value for contact angle of atom type i and fluid)


# New pair style
pair_style 	gran	 model hertz tangential history cohesion sjkr2 rolling_friction epsd2 
										# Defining contact models options:
								        # rolling_friction CDT/epsd/epsd2 
										# cohesion sjkr/sjkr2/easo/washino
pair_coeff	* *

# Set time step = always constant/ For variable timestep refer to fix dt/reset
timestep	${dt}

# Set gravity
fix			gravi all gravity	 9.81 vector 0.0 0.0 -1.0

# Load Balancing Setting
#partitioner_style     zoltan OBJ_WEIGHT_DIM 1

# Define granular walls
fix		deliver_belt_1 all mesh/surface	 file CAD/deliver_belt_1.stl type 2 surface_vel 0 -5 0 curvature 1e-6
fix		deliver_belt_2 all mesh/surface	 file CAD/deliver_belt_2.stl type 2 surface_vel 0 -4.8 1.42 curvature 1e-6
fix		receive_belt all mesh/surface/stress  file CAD/receive_belt.stl type 2 surface_vel -4.87 0 1.12 wear finnie
fix		chute all mesh/surface/stress file CAD/chute.stl type 2 heal auto_remove_duplicates curvature_tolerant yes wear finnie 


fix		wall all wall/gran	model hertz tangential history cohesion sjkr2 rolling_friction epsd2 mesh n_meshes 4 meshes& 
				 deliver_belt_1 deliver_belt_2 receive_belt chute

# particle distributions for insertion
fix		pts1 all particletemplate/sphere 1 atom_type 1 density constant ${dens} radius constant ${r1} 
fix		pts2 all particletemplate/sphere 1 atom_type 1 density constant ${dens} radius constant ${r2}
fix		pts3 all particletemplate/sphere 1 atom_type 1 density constant ${dens} radius constant ${r3}
fix		pts4 all particletemplate/sphere 1 atom_type 1 density constant ${dens} radius constant ${r4}
fix		pts5 all particletemplate/sphere 1 atom_type 1 density constant ${dens} radius constant ${r5}

# 
fix		pdd1 all particledistribution/discrete 1. 5 pts1 ${frac1} pts2 ${frac2} pts3 ${frac3} pts4 ${frac4} pts5 ${frac5}

fix		ins_mesh1 all mesh/surface/omp file CAD/gen_face.stl type 2 curvature 1e-6
# 
fix		ins1 all insert/stream seed 5330 distributiontemplate pdd1 &
		maxattempt 100 mass ${m} massrate ${Q} overlapcheck yes vel constant 0 0 -1.&
        insertion_face ins_mesh1 extrude_length 1.5

fix		integr all nve/sphere	

#output settings, include total thermal energy
fix			ts all check/timestep/gran 1000 0.1 0.1
compute		rke all erotate/sphere
#compute 	fc all pair/gran/local pos id force
thermo_style	custom step atoms ke c_rke f_ts[1] f_ts[2] vol
thermo		1000
thermo_modify	lost ignore norm no
compute_modify	thermo_temp dynamic yes


shell rm post                  				# deleting existing link to a virtual post directory
shell mkdir post_ff_${ff}_rf_${rf}      	# creating a directory for the simulation results (LINUX bash command) 
shell ln -s post_ff_${ff}_rf_${rf}   post 	# create a symbolic link to the saving directory 


dump 		dumpstl1 all mesh/stl 1 post_ff_${ff}_rf_${rf}/static*.stl deliver_belt_1 deliver_belt_2 receive_belt chute

# Writing particle information in a file
dump		dmp_m all custom ${dumpstep} post_ff_${ff}_rf_${rf}/dump_*.liggghts&
 					  id type x y z ix iy iz vx vy vz fx fy fz omegax omegay omegaz radius

# Dump stress on chute walls
dump 		dumpstress_chute all mesh/gran/VTK ${dumpstep} post_ff_${ff}_rf_${rf}/dump_chute*.vtk stress wear chute

# Dump stress on receive belt
dump 		dumpstress_belt all mesh/gran/VTK ${dumpstep} post_ff_${ff}_rf_${rf}/dump_belt*.vtk stress wear receive_belt

#dump 		dmpfc all local ${dumpstep} post_Calib_{CED}_RMP200/fc*.dump &
			c_fc[1] c_fc[2] c_fc[3] c_fc[4] c_fc[5] c_fc[6] c_fc[7] c_fc[8] c_fc[9] c_fc[10] c_fc[11] c_fc[12] 
			#[x,y,z],[x,y,z],id1,id2,periodic_flag,Fx,Fy,Fz

run		1         						# run simulation for 1 step for any bugs
undump 		dumpstl1  					# no further saving of the "static.stl" file needed


run ${steps1}    						# perform simulation

write_restart	anyname.restart			# Write a restar file for further operation


 