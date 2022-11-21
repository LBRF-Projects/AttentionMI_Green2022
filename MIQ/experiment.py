# -*- coding: utf-8 -*-

__author__ = "Darby Green"

import time
import math
import random
from copy import copy

import os
import klibs
from klibs import P
from klibs.KLEventQueue import pump, flush
from klibs.KLGraphics import fill, flip, blit, NumpySurface
from klibs.KLGraphics import KLDraw as kld
from klibs.KLTime import CountDown
from klibs.KLEventInterface import TrialEventTicket as TrialEvent
from klibs.KLUserInterface import any_key, key_pressed, ui_request
from klibs.KLCommunication import message

from klibs.KLUtilities import deg_to_px, pump, flush, show_mouse_cursor, hide_mouse_cursor
from klibs.KLUtilities import line_segment_len as lsl
from klibs.KLResponseCollectors import KeyPressResponse, Response
from klibs.KLTime import CountDown, precise_time

import sdl2
from InterfaceExtras import LikertType, Slider, Button

from PIL import Image

CENTERED = 5

class MIQ(klibs.Experiment):

    def setup(self):
         # Initialize text styles
        self.txtm.add_style('normal', '0.7deg')
        self.txtm.add_style('title', '1.5deg')
        self.txtm.add_style("timer", "1deg", color=(255, 0, 0))
#Need this here not sure why (HLJT format didn't work)    
        # self.instructions()

    #Initialize the response collector
        self.key_listener = KeyPressResponse()
        self.key_listener.key_map = {
            'space': "go",
            
        }

    # Initialize runtime variables
        self.trials_since_break = 0
    


    # Experiment start message


        # Run task instructions
        msg = message("Press any key to begin.", blit_txt=False)
        fill()
        blit(msg, 5, P.screen_c)
        flip()
        flush()
        any_key()

        msg_demo1 = message("Welcome to the Motor Imagery Questionaire!", blit_txt=False)
        fill()
        blit(msg_demo1, 5, P.screen_c)
        flip()
        flush()
        any_key()

        msg_demo2 = message ("This questionaire consists of 14 questions each stating a movement.\n You will first perform the movement as described.\n Then, you will use motor imagery to perform the movement a second time.\n Lastly you will rate the ease/difficulty with which you were able to do the task.", blit_txt=False, align='center')

        fill()
        blit(msg_demo2, 5, P.screen_c)
        flip()
        flush()
        any_key()

        start= message ("Starting Position:", style="title", blit_txt=False, align='center')

        starti= message ("First you will read the postion you should start the movement in.\n" 
                        "During motor imagery this is also the position you will be in.", blit_txt=False, align='center')
        
        flush()
        fill() 
        blit(start, CENTERED, (int(P.screen_x / 2), int(P.screen_y * 0.2)))
        blit(starti, CENTERED, (int(P.screen_x / 2), int(P.screen_y * 0.4)))
        flip()
        any_key()


        action= message ("Action:", style="title", blit_txt=False, align='center')

        actioni= message ("Next you will be given the movement, before starting your movement\n you will press the space bar to begin\n and once you have completed to movement\n you will press the spacebar again to inicate you have completed the movement.\n Remember to only perform the movement a single time.", blit_txt=False, align='center')

        flush()
        fill() 
        blit(action, CENTERED, (int(P.screen_x / 2), int(P.screen_y * 0.2)))
        blit(actioni, CENTERED, (int(P.screen_x / 2), int(P.screen_y * 0.4)))
        flip()
        any_key()

        mental_task= message ("Mental Task:", style="title", blit_txt=False, align='center')

        mental_taski= message ("Next you will be asked to perform the movement again using motor imagery.\n The statement will indicate whether you will form as clear and vivid\n  a visual image as possible of the movement just performed,\n or attempt to feel yourself making the movement.\n You will again use the spacebar to indicate when you have began and finished the movement.", blit_txt=False, align='center')

        flush()
        fill() 
        blit(mental_task, CENTERED, (int(P.screen_x / 2), int(P.screen_y * 0.2)))
        blit(mental_taski, CENTERED, (int(P.screen_x / 2), int(P.screen_y * 0.4)))
        flip()
        any_key()

        demo_msg = message("Lastly you will rate the ease/difficulty with which you were able\n to do the mental task on a Kinesthetic or visual scale.", blit_txt=False, align='center')
        feel_likert= LikertProbe(
                        1, 7, demo_msg, int(P.screen_x * 0.6), (P.screen_c[0], int(P.screen_y * 0.3))
                    )
    
        response = feel_likert.collect()

       
        fill()
        flip()
        flush()
        any_key()

        begin= message ("The task will now start!", style="title", blit_txt=False, align='center')
        fill()
        blit(begin, 5, P.screen_c)
        flip()
        flush()
        any_key()

    def run_MIQ(self):
        pass
    def block(self):
        pass

    def setup_response_collector(self):
        self.key_listener._rc_start = None
        self.key_listener.reset()
        self.key_listener.init()

    def trial_prep(self):
        pass

    def trial(self):

        #message lines that will be repeated throughout
        
        start= message ("Starting Position:", style="title", blit_txt=False, align='center')

        action= message ("Action:", style="title", blit_txt=False, align='center')

        mental_task= message ("Mental Task:", style="title", blit_txt=False, align='center')

        timer_msg= message("Press spacebar to start and stop timer", style="timer", blit_txt=False, align='center')

        mental_feel= message ("Assume the starting position.\n Attempt to FEEL yourself making the movement just\n" 
                               " performed without actually doing it.", blit_txt=False, align='center')

        mental_visual= message ("Assume the starting position.\n Attempt to SEE yourself making the movement just\n" 
                                " performed with as clear and vivid a visual image as possible.", blit_txt=False, align='center')

        #Starting positions and movements

        q_text = {
            "q1": [
                "Stand with your feet and legs together and your arms at your sides.",
                ("Raise your one knee as high as possible so that you are standing\n" 
                 "on one leg with your other leg flexed (bent) at the knee. Now lower your\n" 
                 "leg so that you are again standing on two feet."),
            ],
            "q2": [
                "While sitting, put your hand on your lap and make a fist.",
                ("Raise until hand above your head until your arm is fully extended,\n" 
                 "keeping your fingers in a fist.\n Next, "
                 "lower your hand back to your lap while maintaining a fist. "),
            ],
            "q3": [ 
                "Extend your arm straight out to your side so that it is parallel to the ground,\n" 
                "with your fingers extended and your palm down. ",
                ("Move your arm forward until it is directly in front of your body\n" 
                "(still parallel to the ground).\n" 
                "Keep your arm extended during the movement and make the movement slowly.\n" 
                "Now move your arm back to the starting position, straight out to your side."),
            ],
            "q4": [ 
                "Stand with your arms fully extended above your head.",
                ("Slowly bend forward at the waist and try and touch your toes with your fingertips.\n" 
                "Now return to the starting position,\n" 
                "standing erect with your arms extended above your head."),
                
            ],
            "q5": [ 
                "Put your hand in front of you about shoulder\n"
                "height as if you are about to push open\n"
                "a swinging door. Your fingers should be pointing upwards.",
                ("Extend your arm fully as if you are pushing open the door,\n" 
                "keeping your fingers pointing upwards. Now let the swinging door close\n" 
                "by returning your hand and arm to the starting position."),
            ],
            "q6": [ 
                "While sitting, put your hand in your lap.\n" 
                "Pretend you see a drinking glass on a table directly in front of you.",
                ("Reach forward, grasp the glass and lift it slightly off the table.\n" 
                "Now place it back on the table and return your hand to your lap."),
                
            ],
            "q7": [ 
                "Your hand is at your side.\n" 
                "Pretend there is a door in front of you that is closed.",
                ("Reach forward, grasp the door handle and pull open the door.\n" 
                       "Now gently shut the door, let go of the door handle and\n return your arm to your side."),
            ]
        }

        question_seq = [
            ("q1", "feel"),
            ("q2", "visual"),
            ("q3","feel"),
            ("q4","visual"),
            ("q5","visual"),
            ("q6","feel"),
            ("q7","feel"),
            ("q1", "visual"),
            ("q2", "feel"),
            ("q3","visual"),
            ("q4","feel"),
            ("q5","feel"),
            ("q6","visual"),
            ("q7","visual")
        ]

        for q, modality in question_seq:
            txt1, txt2 = q_text[q]
            msg1 = message(txt1, blit_txt=False, align='center')
            msg2 = message(txt2, blit_txt=False, align='center')

            #Starting position
            msg = message("Press any key to begin.", blit_txt=False)
            fill()
            blit(msg, 5, P.screen_c)
            flip()
            flush()
            any_key()

            flush()
            fill() 
            blit(start, CENTERED, (int(P.screen_x / 2), int(P.screen_y * 0.2)))
            blit(msg1, CENTERED, (int(P.screen_x / 2), int(P.screen_y * 0.5)))
            flip()
            any_key()
        
            #Action
            flush()
            fill() 
            blit(action, CENTERED, (int(P.screen_x / 2), int(P.screen_y * 0.2)))
            blit(msg2, CENTERED, (int(P.screen_x / 2), int(P.screen_y * 0.4)))
            blit(timer_msg, CENTERED, (int(P.screen_x / 2), int(P.screen_y * 0.7)))
            flip()
            rt1 = self.get_movement_time()

            if modality == "visual":
                #Mental task
                flush()
                fill() 
                blit(mental_task, CENTERED, (int(P.screen_x / 2), int(P.screen_y * 0.2)))
                blit(mental_visual, CENTERED, (int(P.screen_x / 2), int(P.screen_y * 0.4)))
                blit(timer_msg, CENTERED, (int(P.screen_x / 2), int(P.screen_y * 0.7)))
                flip()
                rt2 = self.get_movement_time()

                #Visual Likert
                visual_msg = message("Now rate the ease/difficulty with which you were able\n to do this mental task, on the visual scale.", blit_txt=False)
                visual_likert = LikertProbe(
                        1, 7, visual_msg, int(P.screen_x * 0.6), (P.screen_c[0], int(P.screen_y * 0.3))
                    )
                response = visual_likert.collect()
            else:
                #Mental task
                flush()
                fill() 
                blit(mental_task, CENTERED, (int(P.screen_x / 2), int(P.screen_y * 0.2)))
                blit(mental_feel, CENTERED, (int(P.screen_x / 2), int(P.screen_y * 0.4)))
                blit(timer_msg, CENTERED, (int(P.screen_x / 2), int(P.screen_y * 0.7)))
                flip()
                rt2 = self.get_movement_time()

                #Feel Likert
                feel_msg = message("Now rate the ease/difficulty with which you were able\n to do this mental task, on the Kinesthetic scale.", blit_txt=False)
                feel_likert = LikertProbe(
                        1, 7, feel_msg, int(P.screen_x * 0.6), (P.screen_c[0], int(P.screen_y * 0.3))
                    )

                response = feel_likert.collect()
            dat= {
                #add question number 
                "block_num": P.block_number,
                "trial_num": P.trial_number,
                "participant_id": P.p_id,
                "question": q,
                "rt1": rt1, 
                "rt2": rt2, 
                "likert": response.value,
                "modality": modality 
                }
            self.db.insert(dat, "trials")


    def trial_clean_up(self):
        pass

    def clean_up(self):
        pass

    def get_movement_time(self):
        onset = None
        rt = None
        while not rt:
            q = pump(True)
            if key_pressed("space", queue=q):
                if onset:
                    rt = precise_time() - onset
                else:
                    onset = precise_time()
        return rt


class LikertProbe(object):
    """

    Args:
        first (int): The first number in the Likert scale.
        last (int): The last number in the Likert scale.
        question: A message containing the text to present on screen with the
            scale.
        width (int): The width of the full Likert scale in pixels (e.g.
            int(P.screen_x * 0.7)).
        origin (tuple): The coordinates at which to place the top-middle
            of the probe (e.g. (P.screen_c[0], int(P.screen_y * 0.3))).

    """
    def __init__(self, first, last, question, width, origin):

        self.q = question
        self.width = width
        self.origin = origin

        height = width / (len(range(first, last+1)) + 2)
        self.scale = LikertType(first, last, width, height, style='normal')

    def collect(self):
        """Displays the probe and waits for a response.

        """
        show_mouse_cursor()
        onset = time.time()

        while self.scale.response == None:
            q = pump(True)
            ui_request(queue=q)
            fill()
            blit(self.q, location=self.origin, registration=8)
            self.scale.response_listener(q)
            flip()

        response = self.scale.response
        rt = time.time() - onset
        hide_mouse_cursor()
        self.scale.response = None # reset for next time
        return Response(response, rt)
        # two likert scales- visual imagery scale 
#1- Very hard to see
#2- Hard to see
#3- Somewhat hard to see
#4- Neutral (not easy not hard)
#5- Somewhat easy to see
#6- Easy to see
#7- Very easy to see

# Kinesthetic Imagery Scale
#1- Very hard to feel
#2- Hard to feel
#3- Somewhat hard to feel
#4- Neutral (not easy not hard)
#5- Somewhat easy to feel 
#6- Easy to feel
#7- Very easy to feel 
