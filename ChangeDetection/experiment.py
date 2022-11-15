# -*- coding: utf-8 -*-

__author__ = "Austin Hurst"

import time
import math
import random
from copy import copy

import klibs
from klibs import P
from klibs.KLEventQueue import pump, flush
from klibs.KLGraphics import fill, blit, flip
from klibs.KLGraphics import KLDraw as kld
from klibs.KLTime import CountDown
from klibs.KLEventInterface import TrialEventTicket as TrialEvent
from klibs.KLUserInterface import key_pressed, ui_request, any_key
from klibs.KLCommunication import message
from klibs.KLUtilities import deg_to_px
from klibs.KLUtilities import line_segment_len as lsl
from klibs.KLResponseCollectors import ResponseCollector, KeyPressResponse


# Define square colors
YELLOW = (255, 255, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
PURPLE = (255, 0, 255)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

COLOR_PALETTE = {
    'yellow': YELLOW,
    'blue': BLUE,
    'green': GREEN,
    'red': RED,
    'purple': PURPLE,
    'white': WHITE,
    'black': BLACK,
}

CENTERED = 5

# NOTE: Harris et al. (2020) says stimulus display was 1280x1024
# at a distance of 44 cm (no size, but going to guess 19")
# Given these assumptions, screen height was 37.8 dva, so:
#  - 80% screen height = 30.2 dva
#  - Square size (15% height) = 5.33 dva
#  - Square padding (2% height) = 0.75 dva
#
# For simplicity, could set square range to 30°, squares to 5°,
# and padding to 1°? The 2% height is the minimum padding, so that
# would be the padding between jitters.


class ChangeDetection(klibs.Experiment):

    def setup(self):
        # Specify simulus sizes
        canvas_height = P.screen_y
        self.square_size = int(canvas_height * 0.15)
        self.demo_size = int(canvas_height * 0.05)
        self.square_pad_min = int(canvas_height * 0.02)

        # Stimulus layout
        stim_region_w = int(canvas_height * 0.8)
        self.stim_rect = (
            [c - (stim_region_w / 2) for c in P.screen_c],
            [c + (stim_region_w / 2) for c in P.screen_c],
        )
        self.square_pad = int(canvas_height * 0.04)

        # Feedback text
        self.txtm.add_style("correct", "1.5deg", color=GREEN)
        self.txtm.add_style("incorrect", "1.5deg", color=RED)
        self.txtm.add_style("title", "1.5deg")
        self.feedback = {
            'correct': message("Correct!", style="correct", blit_txt=False),
            'incorrect': message("Incorrect!", style="incorrect", blit_txt=False),
        }

        self.key_listener = KeyPressResponse()
        self.key_listener.key_map = {
            's': "same",
            'd': "different",
        }

        # Insert practice blocks
        if P.run_practice_blocks:
            num = P.trials_per_practice_block
            self.insert_practice_block(1, trial_counts=num)
            self.insert_practice_block(3, trial_counts=num)
            self.insert_practice_block(5, trial_counts=num)

        # Run task instructions
        self.instructions()
        

    def instructions(self):

        iheader = message("Instructions", style="title", blit_txt=False, align='center')
        imsg1 = message("In the task you will breifly see displays of colourful squares.", blit_txt=False, align='center')
        imsg2 = message("Each display will be quickly followed by a single square\nthat "
                        "will occupy the same position as one of the previous display squares.",blit_txt=False, align='center')
        imsg3 = message("The single square may or may not be the same colour as the\n square that "
                        "was previously shown in that location.",blit_txt=False, align='center')
        imsg4 = message("Your task is to respond to if you think the square is the\n" 
                        "same colour or a different colour.",blit_txt=False, align='center')
        imsg5 = message("You will press the 's' key if you think the colour is the same.", blit_txt=False, align='center')
        imsg6 = message("You will press the 'd' key if you think the colour is different.",blit_txt=False, align='center')
        
          
                
        # Create the square object
        
        squares_demo= [DetectionSquare((900, 850), self.demo_size, 'blue'),
                        DetectionSquare((700, 700), self.demo_size, 'green'),
                        DetectionSquare((639, 820), self.demo_size, 'purple'),
                        DetectionSquare((920, 780), self.demo_size, 'yellow'),
        ]

        squares_demo_same= [DetectionSquare((700, 700), self.demo_size, 'green'),
        ]

        squares_demo_diff= [DetectionSquare((700, 700), self.demo_size, 'purple'),
        ]
       

        fill()
        for square in squares_demo:
                square.draw()
        blit(iheader, CENTERED, (int(P.screen_x / 2), int(P.screen_y * 0.2)))
        blit(imsg1, CENTERED, (int(P.screen_x / 2), int(P.screen_y * 0.4)))
        blit(imsg2, CENTERED, P.screen_c)
        flip()
        flush()
        any_key()
        
        fill()
        for square in squares_demo:
                square.draw()
        blit(iheader, CENTERED, (int(P.screen_x / 2), int(P.screen_y * 0.2)))
        blit(imsg3, CENTERED, (int(P.screen_x / 2), int(P.screen_y * 0.4)))
        blit(imsg4, CENTERED, (int(P.screen_x / 2), int(P.screen_y * 0.55)))
        flip()
        flush()
        any_key()

        fill()
        for square in squares_demo_same:
                square.draw()
        blit(imsg5, CENTERED, (int(P.screen_x / 2), int(P.screen_y * 0.4)))
        flip()
        flush()
        any_key()

        fill()
        for square in squares_demo_diff:
                square.draw()
        blit(imsg6, CENTERED, (int(P.screen_x / 2), int(P.screen_y * 0.4)))
        flip()
        flush()
        any_key()

    def block(self):
        block = P.block_number
        block_num = int((block + 1) / 2) if P.run_practice_blocks else block
        self.num_squares = 4 + (block_num - 1) * 2
        
        # Show block start message
        header = message("Block {} of 3".format(block_num), style="title", blit_txt=False)
        if P.practicing:
            header = message("This is a practice block", style="title", blit_txt=False)
        msg1 = message(
            "For this block, there will be {} squares at a time.".format(self.num_squares),
            blit_txt=False
        )
        msg2 = message("Press any key to begin.", blit_txt=False)
        fill()
        blit(header, CENTERED, (int(P.screen_x / 2), int(P.screen_y * 0.2)))
        blit(msg1, CENTERED, P.screen_c)
        blit(msg2, CENTERED, (int(P.screen_x / 2), int(P.screen_y * 0.65)))
        flip()
        flush()
        any_key()



    def setup_response_collector(self):
        self.key_listener._rc_start = None
        self.key_listener.reset()
        self.key_listener.init()


    def trial_prep(self):

        # Get colours for the trial
        colorset = list(COLOR_PALETTE.keys())
        random.shuffle(colorset)

        square_locs = randomize_squares(
            self.num_squares, self.square_size, self.stim_rect, self.square_pad_min
        )
        self.squares = []
        for loc_x, loc_y in square_locs:
            # Get color for the square
            if len(colorset) == 0:
                colorset = list(COLOR_PALETTE.keys())
                random.shuffle(colorset)
            color = colorset.pop()
            # Create the square object
            self.squares.append(
                DetectionSquare((loc_x, loc_y), self.square_size, color)
            )

        # Get target square
        target_square = random.choice(self.squares)
        if self.probe_color == "same":
            target_color = target_square.color
        else:
            nontarget_colors = list(set([s.color for s in self.squares]))
            nontarget_colors.remove(target_square.color)
            target_color = random.choice(nontarget_colors)
        self.target = DetectionSquare(
            target_square.loc, self.square_size, target_color
        )
        
        # Register sequence of trial events
        self.evm.register_tickets([
            TrialEvent('squares_off', P.square_duration),
            TrialEvent('probe_on', P.square_duration + P.retention_interval),
        ])


    def trial(self):

        while self.evm.before('squares_off'):
            ui_request()
            fill()
            for square in self.squares:
                square.draw()
            flip()

        fill()
        flip()
        while self.evm.before('probe_on'):
            ui_request()

        fill()
        self.target.draw()
        flip()
        self.key_listener._rc_start = self.evm.trial_time_ms
        response = None
        while not response:
            q = pump(True)
            ui_request(queue=q)
            response = self.key_listener.listen(q)

        # Display feedback
        err = (response.value != self.probe_color)
        feedback_time = CountDown(P.feedback_duration)
        feedback = self.feedback["incorrect" if err else "correct"]
        while feedback_time.counting():
            ui_request()
            fill()
            blit(feedback, 5, P.screen_c)
            flip()

        # Log square info to database
        square_num = 0
        for s in self.squares:
            square_num += 1
            dat = {
                "participant_id": P.p_id,
                "block_num": P.block_number,
                "trial_num": P.trial_number,
                "square_num": square_num,
                "loc":str(s.loc),
                "colour": s.color,
            }
            self.db.insert(dat, "squares")

        return {
            "block_num": P.block_number,
            "trial_num": P.trial_number,
            "target_col": self.target.color,
            "target_loc": str(self.target.loc),
            "response": response.value,
            "rt": response.rt,
            "response_probe": self.probe_color,
            "accuracy": response.value == self.probe_color
        }

    def trial_clean_up(self):
        pass

    def clean_up(self):
        pass



class DetectionSquare(object):

    def __init__(self, loc, size, color):
        self.loc = loc
        self.size = size
        self.color = color
        self._shape = kld.Rectangle(size, fill=COLOR_PALETTE[color])

    def draw(self):
        blit(self._shape, 5, self.loc)



def randomize_squares(count, size, canvas_rect, min_pad):

    # Get minimum distance of guaranteed non-overlap (corner-to-corner)
    min_dist = math.sqrt(size ** 2 + size ** 2)

    # Get boundaries of canvas
    x1, y1 = canvas_rect[0]
    x2, y2 = canvas_rect[1]
    min_x = x1 + int(0.5 * size)
    min_y = y1 + int(0.5 * size)
    max_x = x2 - int(0.5 * size)
    max_y = y2 - int(0.5 * size)

    # Randomly generate non-overlapping squares
    squares = []
    attempts = 0
    while len(squares) < count:

        # Generate a random location and see whether it's far enough from
        # the centers of all the other squares
        viable = True
        sq_x = random.randint(min_x, max_x)
        sq_y = random.randint(min_y, max_y)
        for s in squares:
            if lsl((sq_x, sq_y), s) < (min_dist + min_pad):
                attempts += 1
                viable = False
                break
                
        # If the square isn't too close to any other, add it
        if viable:
            attempts = 0
            squares.append((sq_x, sq_y))

        # Otherwise, if 50 locations have been tried for a square without success,
        # reset the list of squares and try again
        elif attempts >= 50:
            attempts = 0
            squares = []

    return squares
