import pybullet as p
import pybullet_data
import time
import numpy as np

from interfaces import DiscreteActionsRobot

def main():
    # Create the robot control interface
    interface = DiscreteActionsRobot()
    interface.mode = 3       # Example mode; can vary depending on your environment setup
    interface.angle = 0
    interface.debugLines = 1 # Enable debug lines if desired
    interface.open()          # This initializes JacoEnv and sets up the simulation environment

    # Initial end-effector position (relative to center)
    robot_pos = np.array([0.0, 0.0, 0.0])
    key_mapping_pos = {
        'd': (0.01, 0.0, 0.0),   # Move +X
        'a': (-0.01, 0.0, 0.0),  # Move -X
        'w': (0.0, 0.01, 0.0),   # Move +Y
        's': (0.0, -0.01,0.0),   # Move -Y
        'q': (0.0, 0.0, 0.01),   # Move +Z
        'e': (0.0, 0.0, -0.01)   # Move -Z
    }

    print("Controls:")
    print("  Position Mode (default):")
    print("    a/d: Move end-effector along X (-/+)")
    print("    s/w: Move end-effector along Y (-/+)")
    print("    q/e: Move end-effector along Z (-/+)")
    print("  Gripper Mode:")
    print("    o: Open gripper")
    print("    c: Close gripper")
    print("  Press 'm' to toggle modes (position <-> gripper)")
    print("  Press 'x' to exit.")
    
    position_mode = True

    # Main simulation loop
    while True:
        keys = p.getKeyboardEvents()
        

        # Check for key inputs
        for k, v in keys.items():
            print("Key:", k, "Value:", v)
            if (v == 4):
                char = chr(k)
                print(char)
                # Handle mode switching
                if char == 'm':
                    position_mode = not position_mode
                    mode_name = "Position" if position_mode else "Gripper"
                    print(f"Switched to {mode_name} mode")

                elif char == 'x':
                    p.disconnect()
                    return

                if position_mode:
                    # Position control keys
                    if char in key_mapping_pos:
                        delta = np.array(key_mapping_pos[char])
                        robot_pos += delta
                        interface.updateRobotPos(robot_pos, 0)
                else:
                    # Gripper mode keys
                    if char == 'o':
                        # Open gripper - depending on your environment code, adjust fingers
                        # Typically, interface.setFing(value) sets finger openness
                        # Smaller value = more open, larger = more closed, depending on JacoEnv
                        interface.setFing(0.0)
                        print("Gripper opened")
                    elif char == 'c':
                        # Close gripper
                        interface.setFing(1.3)  # Example close position
                        print("Gripper closed")

        # Step simulation and let the interface handle IK and motion
        interface.render()
        time.sleep(1./240.)

if __name__ == "__main__":
    main()