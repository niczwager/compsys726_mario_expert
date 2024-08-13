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

    def run_action(self, action: int) -> None:
        """
        This is a very basic example of how this function could be implemented

        As part of this assignment your job is to modify this function to better suit your needs

        You can change the action type to whatever you want or need just remember the base control of the game is pushing buttons
        """

        # Simply toggles the buttons being on or off for a duration of act_freq
        self.pyboy.send_input(self.valid_actions[action])

        for _ in range(self.act_freq):
            self.pyboy.tick()

        self.pyboy.send_input(self.release_button[action])

        
       


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

        self.pipe_checker = False

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

        # Start searching from the bottom-right and move backward
        for i in range(rows - 1, -1, -1):  # Iterate from rows-1 to 0
            for j in range(cols - 1, -1, -1):  # Iterate from cols-1 to 0
                if current_environment[i][j] == sprite:
                    if sprite == self.mario_sprite:
                        sprite_position = [i, j]
                        return sprite_position, count
                    
                    sprite_position = [i, j]
                    count = count + 1
                    #return sprite_position  # Return as soon as a match is found

        return sprite_position, count

    def goopher_case(self, current_environment, mario_position):
        print("Bitch as goopher in frame bitch as fucker")

        # Checking if need to jump
        goopher_position = self.find_position(current_environment, self.goopher_sprite)

        # Checking if goopher in front of Mario and jump required
        if goopher_position[1] - mario_position[1] <= 3 and goopher_position[1] > mario_position[1]:
            print('jumping')
            return 4 # Jump
        else:
            return 2
        
    def pipe_case(self, current_environment, mario_position):
        print("Found that bitch as pipe wagwan")

        # Checking if pipe section hasn't been entered yet
        if self.pipe_checker == False:
            self.pipe_checker = True
            return 0 # Do nothing
        else:
            # Continue running forward
            return 2


    def choose_action(self):
        # For debugging
        time.sleep(0.1)

        state = self.environment.game_state()
        frame = self.environment.grab_frame()
        game_area = self.environment.game_area()

        current_environment = self.environment.pyboy.game_wrapper
        current_environment_arr = current_environment.game_area()
        
        print(current_environment.game_area())
        #print(current_environment)

        # Locating Mario's position
        mario_position, _ = self.find_position(current_environment, self.mario_sprite)

        # TODO: Anyone but pipe in front of Mario just jump, dont' need a special goopher case for this
        # TODO: implement pause when there is a pipe in front, run then jump - this will require a variable counter

        print("Mario's position: " + str(mario_position) + " In front of Mario: " + str(current_environment_arr[mario_position[0], mario_position[1]+1]))

        goopher_position, goopher_count = self.find_position(current_environment, self.goopher_sprite)

        print("Goopher position: " + str(goopher_position) + " Goopher count: " + str(goopher_count))

        dble_gpher_dist = 15
        gphr_pause = 10

        # If anything in front of Mario - jump
        if current_environment_arr[mario_position[0], mario_position[1]+1] != 0 and goopher_count != 2:
            print('Jumping')
            return 4 # jump
        
        # Special double goopher case
        elif goopher_count == 2:
            print("Two gophers")
            if goopher_position[1] - mario_position[1] <= dble_gpher_dist and goopher_position[1] - mario_position[1] >= dble_gpher_dist - gphr_pause:
                print("Pausing")
                return 0 # Do nothing
            elif current_environment_arr[mario_position[0], mario_position[1]+1] != 0:
                print('Jumping - in goopher')
                return 4
        
        # Speical need to jump over floor case
        elif current_environment_arr[mario_position[0]+1, mario_position[1]+2] != 10 and mario_position[0] == 13:
            print('Jumping over floor')
            print(current_environment_arr[mario_position[0+1], mario_position[1]+1])
            return 4


        '''
        # Checking if Goopher present
        if self.goopher_sprite in current_environment.game_area():
            print("Bitch as goopher in frame bitch as fucker")

            # Checking if need to jump
            goopher_position = self.find_position(current_environment, self.goopher_sprite)

            # Checking if goopher in front of Mario and jump required
            if goopher_position[1] - mario_position[1] <= 3 and goopher_position[1] > mario_position[1]:
                print('jumping')
                return 4 # Jump
           
        # Continue running and jumping over anything that isn't a pipe infront
        #elif current_environment_arr[mario_position[0], mario_position[1]+2] == self.goopher_sprite or current_environment_arr[mario_position[0], mario_position[1]+2] == self.floor_sprite:
        elif current_environment_arr[mario_position[0], mario_position[1]+2] != 0 and current_environment_arr[mario_position[0], mario_position[1]+2] != self.pipe_sprite:
            #self.pipe_checker = False
            print('jumping')
            print(current_environment_arr[mario_position[0], mario_position[1]+2])
            return 4 # Jumping over walls etc.

        # Special case for when pipe in front of Mario
        elif current_environment_arr[mario_position[0], mario_position[1]+2] == self.pipe_sprite:
            # Send do nothing for 2 goes
            # Then run foward and jump
            print('entered pipe in front section')
        '''


        #return random.randint(0, len(self.environment.valid_actions) - 1)
        return 2

    def step(self):
        """
        Modify this function as required to implement the Mario Expert agent's logic.

        This is just a very basic example
        """

        # Choose an action - button press or other...
        action = self.choose_action()

        # Run the action on the environment
        self.environment.run_action(action)

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
