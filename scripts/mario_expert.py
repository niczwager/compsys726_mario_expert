"""
This the primary class for the Mario Expert agent. It contains the logic for the Mario Expert agent to play the game and choose actions.

Your goal is to implement the functions and methods required to enable choose_action to select the best action for the agent to take.

Original Mario Manual: https://www.thegameisafootarcade.com/wp-content/uploads/2017/04/Super-Mario-Land-Game-Manual.pdf
"""

import json
import logging
import random
import time

import cv2
from mario_environment import MarioEnvironment
from pyboy.utils import WindowEvent

# Added libraries
import numpy as np

class MarioController(MarioEnvironment):
    """
    The MarioController class represents a controller for the Mario game environment.

    You can build upon this class all you want to implement your Mario Expert agent.

    Args:
        act_freq (int): The frequency at which actions are performed. Defaults to 10.
        emulation_speed (int): The speed of the game emulation. Defaults to 0.
        headless (bool): Whether to run the game in headless mode. Defaults to False.
    """

    def __init__(
        self,
        act_freq: int = 10,
        emulation_speed: int = 0,
        headless: bool = False,
    ) -> None:
        super().__init__(
            act_freq=act_freq,
            emulation_speed=emulation_speed,
            headless=headless,
        )

        self.act_freq = act_freq

        # Example of valid actions based purely on the buttons you can press
        valid_actions: list[WindowEvent] = [
            WindowEvent.PRESS_ARROW_DOWN,
            WindowEvent.PRESS_ARROW_LEFT,
            WindowEvent.PRESS_ARROW_RIGHT,
            WindowEvent.PRESS_ARROW_UP,
            WindowEvent.PRESS_BUTTON_A,
            WindowEvent.PRESS_BUTTON_B,
        ]

        release_button: list[WindowEvent] = [
            WindowEvent.RELEASE_ARROW_DOWN,
            WindowEvent.RELEASE_ARROW_LEFT,
            WindowEvent.RELEASE_ARROW_RIGHT,
            WindowEvent.RELEASE_ARROW_UP,
            WindowEvent.RELEASE_BUTTON_A,
            WindowEvent.RELEASE_BUTTON_B,
        ]

        self.valid_actions = valid_actions
        self.release_button = release_button

    def run_action(self, action: int, freq) -> None:
        """
        This is a very basic example of how this function could be implemented

        As part of this assignment your job is to modify this function to better suit your needs

        You can change the action type to whatever you want or need just remember the base control of the game is pushing buttons
        """

        #self.act_freq = freq if freq is not None else 10

        self.print_freq()

        # Simply toggles the buttons being on or off for a duration of act_freq
        self.pyboy.send_input(self.valid_actions[action])

        for _ in range(self.act_freq):
            self.pyboy.tick()

        self.pyboy.send_input(self.release_button[action])
    
    def set_freq(self, freq):
        self.act_freq = freq

    def print_freq(self):
        if self.act_freq != 10:
            print("Frequency is now: " + str(self.act_freq))

        
       


class MarioExpert:
    """
    The MarioExpert class represents an expert agent for playing the Mario game.

    Edit this class to implement the logic for the Mario Expert agent to play the game.

    Do NOT edit the input parameters for the __init__ method.

    Args:
        results_path (str): The path to save the results and video of the gameplay.
        headless (bool, optional): Whether to run the game in headless mode. Defaults to False.
    """

    def __init__(self, results_path: str, headless=False):
        self.results_path = results_path

        self.environment = MarioController(headless=headless)

        self.video = None

        self.initial_x_pos = self.environment.get_x_position()

        # Pre-defined sprite numbers based on pyboy documentation
        self.mario_sprite = 1
        self.goopher_sprite = 15
        self.floor_sprite = 10
        self.pipe_sprite = 14
        self.block_sprite = 10

        self.boolean_toggle = False

    '''
    def find_position(self, current_environment, sprite):
        Script to find the current location of Mario Sprite within the simplified game frame

        Mario is represented by:
        [1 1]
        [1 1]

        The potential search grid is 20 wide by 16 
    
        current_environment = np.array(current_environment.game_area())

        rows, cols = current_environment.shape

        for i in range(rows):
            for j in range(cols):
                if current_environment[i][j] == sprite:
                    sprite_position = [i,j]

        #print(sprite_position)

        return sprite_position
    '''
    def find_position(self, current_environment, sprite):
        '''
        Script to find the current location of Mario Sprite within the simplified game frame.

        Mario is represented by:
        [1 1]
        [1 1]

        The potential search grid is 20 wide by 16 high.
        '''
        current_environment = np.array(current_environment.game_area())

        rows, cols = current_environment.shape

        count = 0
        sprite_position = None


        # Single loop to find the sprite or floor gaps
        for i in range(rows - 1, -1, -1):
            for j in range(cols - 1, -1, -1):  # Iterate across all columns
                if current_environment[i][j] == sprite:
                    if sprite != self.goopher_sprite:
                        if sprite == 0: # Checking for gap in floor
                            if i != 15:
                                return None, count 
                            else:
                                if current_environment[i, j-1] == 0 and current_environment[i, j-2] == 0:
                                    return [i,j], 3
                                else:
                                    return [i,j], 2
                        else:
                            return [i, j], count  # Return immediately if Mario is found
                    
                    # Initialize sprite_position as a list if it is None
                    if sprite_position is None:
                        sprite_position = []

                    # Append the position to sprite_position
                    sprite_position.append([i, j])
                    count += 1

        return sprite_position, count

    def choose_action(self):
        # For debugging
        #time.sleep(0.01)

        state = self.environment.game_state()
        frame = self.environment.grab_frame()
        game_area = self.environment.game_area()

        current_environment = self.environment.pyboy.game_wrapper
        current_environment_arr = current_environment.game_area()
        
        print(current_environment.game_area())
        #print(current_environment)

        # Locating Mario's position
        mario_position, _ = self.find_position(current_environment, self.mario_sprite)

        print("Mario's position: " + str(mario_position) + " In front of Mario: " + str(current_environment_arr[mario_position[0], mario_position[1]+1]))

        goopher_position, goopher_count = self.find_position(current_environment, self.goopher_sprite)

        print("Current Mario y postion: " + str(mario_position[0]) + " What's below Mario: " + str(current_environment_arr[mario_position[0]+1, mario_position[1]]))

        floor_position, floor_count = self.find_position(current_environment, 0) # Right most position of a floor tile

        print("Floor position is: " + str(floor_position) + " Floor count: " + str(floor_count)) 

        # Checking floor is actually in front of Mario and close enough
        if floor_position is not None and abs(floor_position[1]-2 - mario_position[1]) >= 8: #and floor_position[1] <= mario_position[1]:# 
            print('Changing floor position')
            floor_position = None
            floor_count = 0

        print("Floor position is: " + str(floor_position) + " Floor count: " + str(floor_count)) 

        dble_gpher_dist = 15
        gphr_pause = 10

        self.environment.set_freq(10)

        # If anything in front of Mario - jump
        if current_environment_arr[mario_position[0], mario_position[1]+1] != 0 and goopher_count != 2:
            print('Jumping')
            return 4, None # jump
        
        # Special double goopher case
        elif goopher_count == 2 and current_environment_arr[mario_position[0]+1, mario_position[1]] == 10:
            print("Two gophers")
            if goopher_position[1][1] - mario_position[1] <= dble_gpher_dist and goopher_position[1][1] - mario_position[1] >= dble_gpher_dist - gphr_pause and goopher_position[1][1] >= mario_position[1] and goopher_position[0][1] >= mario_position[1]:
                print("Pausing")
                return 0, None # Do nothing
            elif current_environment_arr[mario_position[0], mario_position[1]+1] != 0:
                print('Jumping - in goopher')
                return 4, None
        
        # Speical need to jump over floor case
        elif (current_environment_arr[15, mario_position[1]+2] != 10 and mario_position[0] == 13 and floor_count == 2 or
        mario_position == [10, 9] and current_environment_arr[13, 12] == 10 and floor_count == 2):
        #elif floor_position[0] == 15 and floor_position[1] <= 12 and floor_position[1] - mario_position[1] >= 2:
            print('Jumping over floor')
            print(current_environment_arr[mario_position[0+1], mario_position[1]+1])
            return (4, 30) if current_environment_arr[mario_position[0], mario_position[1]+5] == 10 else (4, None) 
        
        # On any pipe small pipe - pause then jump
        #elif mario_position[0] < 13 and mario_position[0] > 10 and current_environment_arr[mario_position[0]+1, mario_position[1]] == 14:
        elif current_environment_arr[mario_position[0]+1, mario_position[1]] == 14 and goopher_position is not None:
            print('Entered pipe jump')
            if goopher_position[0][1] >= mario_position[1]:
                print('Entered 2')
                if abs(goopher_position[0][1] - mario_position[1]) <= 1:
                    print('Entered 3')
                    return 4, None
                else:
                    print('Entered 4')
                    return 0, None
                
        # Bouncy bug bitches in front of Mario
        elif current_environment_arr[mario_position[0]-2, mario_position[1]+4] == 18:
            print('Avoiding bug bitches')
            return 4, None
        
        elif floor_count == 3:
            self.environment.set_freq(37)

            if abs((floor_position[1]-2) - mario_position[1]) <= 1:
                print("Jumping - long section")
                return 4, None

        #return random.randint(0, len(self.environment.valid_actions) - 1)
        return 2, None

    def step(self):
        """
        Modify this function as required to implement the Mario Expert agent's logic.

        This is just a very basic example
        """

        # Choose an action - button press or other...
        action, freq = self.choose_action()

        # Run the action on the environment
        self.environment.run_action(action, freq)

    def play(self):
        """
        Do NOT edit this method.
        """
        self.environment.reset()

        frame = self.environment.grab_frame()
        height, width, _ = frame.shape

        self.start_video(f"{self.results_path}/mario_expert.mp4", width, height)

        while not self.environment.get_game_over():
            frame = self.environment.grab_frame()
            self.video.write(frame)

            self.step()

        final_stats = self.environment.game_state()
        logging.info(f"Final Stats: {final_stats}")

        with open(f"{self.results_path}/results.json", "w", encoding="utf-8") as file:
            json.dump(final_stats, file)

        self.stop_video()

    def start_video(self, video_name, width, height, fps=30):
        """
        Do NOT edit this method.
        """
        self.video = cv2.VideoWriter(
            video_name, cv2.VideoWriter_fourcc(*"mp4v"), fps, (width, height)
        )

    def stop_video(self) -> None:
        """
        Do NOT edit this method.
        """
        self.video.release()
