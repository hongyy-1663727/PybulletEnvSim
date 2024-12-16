import socket
import interfaces
import numpy as np
import math
import pybullet as p
import time

# switch to choose between socket-based control and keyboard control
use_socket = False

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_address = ('localhost', 5006)
# server_address = ('0.0.0.0', 5006)
print('starting up on {} port {}'.format(*server_address))
sock.bind(server_address)

interface = interfaces.DiscreteActionsRobot()
interface.mode = 3
interface.angle = 0
interface.debugLines = 0
interface.open()
interface.letterMode = 0

robot_open = 1
target_pos = np.array([0.0, 300.0, 0.0])
robot_pos = np.array([0.0, 0.0, 0.0])
robot_orn = np.array([0.0, 0.0, 0.0])
p = [0.0, 0.0, 0.0]

def process_command(command, val1, val2, val3=128, val4=0, val5=None, val6=None, val7=None, val8=None, val9=None, val10=None):
    """
    This function encapsulates the logic that was previously inside the main loop.
    You had a series of 'if command == X:' blocks. Move them here.

    For example (pseudocode):

    if command == 0:
        if val1 == 0: # Open Robot
            if robot_open == 0:
                interface.open()
                robot_open = 1
        elif val1 == 1: # Reset
            interface.reset()
        # ... and so on for all your other conditions.

    Adjust as needed. Make sure variables like robot_open are accessible.
    If needed, declare them global or pass them as parameters.
    """

    global robot_open, target_pos, p, target, robot_pos, robot_orn

    # Existing command logic from your original code goes here:
    if command == 0:
        if val1 == 0:  # Open Robot
            if robot_open == 0:
                interface.open()
                robot_open = 1
        if val1 == 1:  # Reset
            interface.reset()
        if val1 == 2:  # Change hold time on debug lines
            updateRate = 1.0 / val2
            interface.updateRefresh(updateRate)
            interface.updateRefresh(.2)
        if val1 == 3:  # Mode
            interface.updateMode(val2)
            print("MODE:", val2)
        if val1 == 4:  # Use debug lines
            interface.updateDebugLines(val2)
            print("DEBUG LINES", val2)
        if val1 == 5:  # Target type
            if interface.letterMode == 1:
                interface.create_targetLetter(target_pos, 0)
            elif interface.mode == 9:
                interface.create_targetRing(target_pos, 0)
            else:
                interface.create_target3D(target_pos, 0, 0)
        # ... Continue copying over all your logic from original code
        # for val1 == 6,7,8,... etc.

    elif command == 1:  # Set Target
        target_pos[0] = ((val1-1) * (val2 + val3/100))/1000
        target_pos[1] = -((val4-1) * (val5 + val6/100))/1000
        target_pos[2] = ((val7-1) * (val8 + val9/100))/1000
        target = val10
        if interface.letterMode == 1:
            interface.create_targetLetter(target_pos, 1)
        elif interface.mode == 9:
            interface.create_targetRing(target_pos, 1)
        else:
            interface.create_target3D(target_pos, 1, target)
    # ... and so on for command == 4, command == 7, etc.
    # Copy all your original 'if command == ...:' blocks here.

    # At the end of processing, step simulation if needed
    interface.robotenv.step()

# Example: Convert keyboard input to (command, val1, val2) tuples
# You must define what keys map to which commands.
def keyboard_to_command(keys):
    # For demo:
    # 'w' moves robot forward => command=4, val1=? val2=?
    # 's' moves robot backward => also command=4 with different val
    # This depends on your existing command structure.

    # Let's say command=4 is Set Robot Position.
    # For simplicity, assume:
    # w: command=4, val1=2 (some value), val2=? to move forward
    # s: command=4, val1=2, val2=? to move backward
    # This is just an example. You must define how keys translate to your command structure.

    # We'll return a list of commands because multiple keys might be pressed.
    commands = []
    increment = 1

    # Just as a rough example:
    if ord('w') in keys and keys[ord('w')] & p.KEY_IS_DOWN:
        # Suppose 'w' means increase robot_pos[1]
        # Command 4 might be: Set Robot pos and val10=some key
        # We need to produce something similar to what the socket would send.
        # The original code sets robot pos with command=4 and uses val1..val10 to encode pos.
        # Let's choose a simple mapping: 
        # command=4, val1 controls x, val4 controls y, val7 controls z.
        # If we don't know exact encoding from your code, we must pick something consistent.

        # Let's say val1-1 is a multiplier, val2 + val3/100 is fractional part. We'll just use simple values.
        # Increase Y by a small step:
        # pos is ((val1-1)*(val2+val3/100))/1000 => we must produce something meaningful.
        
        # For simplicity, let's pick a direct encoding:
        # We'll set val1=2, val2=0 so (val1-1)=1 and (val2+0/100)=0 => 1*0/1000=0 no movement
        # We need a non-zero value. Let's try val2=100 to produce a 0.1 m movement in Y.
        
        # Actually, let's just pick a known pattern from your existing code. You must map keys to values that result in movement.
        # Suppose we interpret 'w' to produce (command=4, val1=2, val2=100, val4=2, val5=0, val6=0 ... ) 
        # This might be complex. Another approach: store a global robot position in meters and convert it to val1..val10 each time.

        # Let's store a global or local robot_pos and each key press updates robot_pos in meters, then convert to your packet format:
        # robot_pos updated by keys:
        global robot_pos
        robot_pos[1] += 0.01  # Move Y by +0.01 m
        # Convert robot_pos back to command format:
        # posX = ((val1-1)*(val2+val3/100))/1000
        # We want posX=robot_pos[0], similarly for posY and posZ
        # Solve for val1,val2: posX*1000 = (val1-1)*(val2 + val3/100)
        # Let's pick val3=0 for simplicity and just use val2 for integer cm:
        # val2 = posX*1000 since (val1-1)=1 means val1=2
        # So val1=2 means (val1-1)=1
        # val2 = int(posX*1000)
        # same for Y and Z using val4,val5...
        
        # We'll pick val3=0, val6=0,... always, to simplify:
        def meters_to_vals(m):
            # We want: m = ((2-1)*(val2 + 0))/1000 = val2/1000
            # val2 = m*1000
            # Make sure val2 fits in a byte (0-255):
            # We'll assume small movements.
            val1 = 2
            val2 = int(abs(m)*1000)
            if val2 > 255:
                val2 = 255
            # If m>0: (val1-1)*(val2)=m*1000 => val1=2 is fine since (2-1)=1
            # If m<0: we need (val4-1)*(val5+val6/100)/1000 = negative
            # Let's just handle positive for example. For negative, you'd adjust val1.
            return val1, val2

        # X:
        val1_x, val2_x = meters_to_vals(robot_pos[0])
        # Y is negative direction in code, so we must be careful:
        # posY = -((val4-1)*(val5+val6/100))/1000
        # If we want posY positive, we must carefully pick val4 and val5
        # Let's just pick val4=2, val5=int(robot_pos[1]*1000) and remember Y is negative in formula.
        # posY = -((val4-1)*val5)/1000
        # If robot_pos[1] is positive, we want val4 to represent that:
        # to get a positive robot_pos[1] from code: robot_pos[1] = ...
        # Actually, since posY = -((val4-1)*val5/1000), if we want a positive posY, we need (val4-1)*val5 negative
        # If (val4-1)=1 always, val5 positive => posY negative. 
        # To achieve positive Y, we can manipulate val4 and val5:
        # If we set val4=1, then (val4-1)=0 => always 0. Not good.
        # If we set val4=0, (val4-1)=-1. 
        # posY = -((-1)*val5/1000) = val5/1000 positive.
        # So val4=0 means (val4-1)=-1
        # val5 = int(robot_pos[1]*1000)
        
        val4 = 0
        val5 = int(abs(robot_pos[1]*1000))  
        
        # Z:
        # posZ = ((val7-1)*(val8+val9/100))/1000
        # For simplicity, just move in XY with 'w','s','a','d'.
        val7 = 2
        val8 = int(abs(robot_pos[2]*1000))

        # We'll set others to some default values:
        val3 = 0
        val6 = 0
        val9 = 0
        val10 = 0

        # command=4: sets robot pos?
        commands.append((4, val1_x, val2_x, val3, val4, val5, val6, val7, val8, val9, val10))

    # Similarly handle 's','a','d', etc. and append commands.

    return commands



while True:
	data, address = sock.recvfrom(4096)

	command = data[0]
	val1 = data[1]
	val2 = data[2]

	if len(data) > 3:
		val3 = data[3]
	else:
		val3 = 128
	if len(data) > 4:
		val4 = data[4]
	if len(data) > 5:
		val5 = data[5]
		val6 = data[6]
		val7 = data[7]
		val8 = data[8]
		val9 = data[9]
		val10 = data[10]

	else:
		val4 = 0

	if command == 0:
		if val1 == 0:		# Open Robot 
			if robot_open == 0:
				interface.open()
				robot_open = 1
		if val1 == 1:		# Reset 
			interface.reset()
		if val1 == 2:		# Change hold time on debug lines
			updateRate = 1.0 /val2
			interface.updateRefresh(updateRate)
			interface.updateRefresh(.2)
		if val1 == 3:		# Mode
			interface.updateMode(val2)
			print("MODE:", val2)
		if val1 == 4:		# Use debug lines
			interface.updateDebugLines(val2)
			print("DEBUG LINES", val2)
		if val1 == 5:		# Target type
			if interface.letterMode == 1:
				interface.create_targetLetter(target_pos, 0)
			elif interface.mode == 9:
				interface.create_targetRing(target_pos,0)
			else:
				interface.create_target3D(target_pos, 0, target)

		if val1 == 6:
			if interface.letterMode == 1:
				interface.create_targetLetter(target_pos, 2)
			elif interface.mode == 9:
				interface.create_targetRing(target_pos,2)
			else:
				interface.create_target3D(target_pos, 2, target)
		if val1 == 7:
			if interface.letterMode == 1:
				interface.create_targetLetter(target_pos, 3)
			elif interface.mode == 9:
				interface.create_targetRing(target_pos,3)
			else:
				interface.create_target3D(target_pos,3, target)
		if val1 == 8:
			interface.setMode(val2)
		if val1 == 9:
			interface.grabCube()
		if val1 == 15:
			interface.update_color(target_pos, val2)
		if val1 == 16:
			interface.targetID = val2
		if val1 == 17:
			interface.letterMode = val2
		if val1 == 18:
			interface.setTargetRad(val2/1000.0)
		if val1 == 19:
			interface.setPath(val2)
			interface.drawPath()
		if val1 == 20:
			interface.setGoCue(val2)
		if val1 == 21:
			interface.drawPath()
		if val1 == 22:
			interface.robotenv.removeDebug()
		if val1 == 23:
			betaVal = ((val2-1) *(val3 + val4/100))
			print(betaVal)
			interface.robotenv.drawBetaLine(betaVal)
		if val1 == 24:
			startOrn = val2
			if startOrn == 1:
				interface.robotenv.set_robotOrn([math.pi, 0, math.pi])
			if startOrn == 2:
				interface.robotenv.set_robotOrn([0, -math.pi/2, 0])
			interface.render()
		if val1 == 25: # robot view
			interface.robotenv.view2 = val2
			print ("VIEW2, ", val2)
		if val1 == 26: #cube directions
			interface.out_dir = [val2-1, val3-1, val4-1] 
			interface.robotenv.set_cubeSideColor(interface.out_dir)
		if val1 == 27: #cube directions
			interface.robotenv.set_center(val2)

	if command == 1:	# Set Target
		target_pos[0] = ((val1-1) *(val2 + val3/100))/ 1000
		target_pos[1] = -((val4-1) *(val5 + val6/100))/ 1000
		target_pos[2] = ((val7-1) *(val8 + val9/100))/ 1000
		target = val10
		if interface.letterMode == 1:
			interface.create_targetLetter(target_pos, 1)
		elif interface.mode == 9:
			interface.create_targetRing(target_pos,1 )
		else:
			interface.create_target3D(target_pos, 1, target)


	if command == 11:	# Set Target
		target_pos[0] = ((val1-1) *(val2 + val3/100))/ 1000
		target_pos[1] = -((val4-1) *(val5 + val6/100))/ 1000
		target_pos[2] = ((val7-1) *(val8 + val9/100))/ 1000
		print(target_pos)
		interface.create_target(target_pos)

	if command == 4:	
		if interface.mode == 10 or interface.mode == 12:
			interface.robotenv.drawMode(1)
		key = val10
		robot_pos[0] = ((val1-1) *(val2 + val3/100))/ 1000
		robot_pos[1] = -((val4-1) *(val5 + val6/100))/ 1000
		robot_pos[2] = ((val7-1) *(val8 + val9/100))/ 1000
		interface.robotenv.opMode = 0
		interface.updateRobotPos(robot_pos,key )
		print(key)
		interface.render()

	
	if command == 7:	
		interface.robotenv.drawMode(2)
		key = val10
		
		robot_ornz = ((val1-1) *(val2 + val3/100))/10

		# interface.robotenv.opMode = 1
		# interface.robotenv.set_robotOrn([math.pi, 0, robot_ornz])

		interface.robotenv.set_robotOrn([robot_ornz,-math.pi/2,0])

		print(robot_ornz)

		grasp =  val5

		if grasp == 1:
			interface.robotenv.setFing(0)
		elif grasp == 2:
			interface.robotenv.setFing(1.3)

		interface.render()

	if command == 5:
		interface.displayCue(val1,val2)

	if command == 6:	# Set Target
		fing = ((val1-1) *val2 + val3/100)/80
		interface.setFing(fing)
		# print(fing)
		interface.render()

	if command == 9:	
		
		robot_orn[0] = (val1-1) *(val2 + val3/100)/10
		robot_orn[1] = -(val4-1) *(val5 + val6/100)/10
		robot_orn[2] = (val7-1) *(val8 + val9/100)/10

		robot_pos

		print(robot_orn)
		interface.robotenv.set_robotOrn(robot_orn)
		interface.render()

	if command == 14:	
		key = val10
		robot_pos[0] = ((val1-1) *(val2 + val3/100))/ 1000
		robot_pos[1] = -((val4-1) *(val5 + val6/100))/ 1000
		robot_pos[2] = ((val7-1) *(val8 + val9/100))/ 1000
		interface.updateRobotPos(robot_pos,key )
		print(robot_pos)
		interface.render()

	if command == 15:		#set path coordinates
		ind = val10
		p[0] = ((val1-1) *(val2 + val3/100))/ 1000
		p[1] = -((val4-1) *(val5 + val6/100))/ 1000
		p[2] = ((val7-1) *(val8 + val9/100))/ 1000
		interface.setPath_ES(p, ind)


	if command == 16:		#set robot orn
		ind = val10
		robot_theta_delta = ((val1-1) *(val2 + val3/100))/100
		interface.robotenv.set_robotRotation(1, robot_theta_delta)
		print(robot_theta_delta)
		interface.render()

sock.shutdown()
sock.close() 
