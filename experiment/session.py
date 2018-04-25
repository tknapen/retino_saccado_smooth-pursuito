from __future__ import division
from psychopy import visual, clock
from psychopy import filters
import numpy as np
import sympy as sym
import os
import json
import glob
import copy
import scipy
import pickle
import math

import exptools
from exptools.core.session import EyelinkSession
from exptools.core.staircase import ThreeUpOneDownStaircase, OneUpOneDownStaircase

from trial import RSSPTrial

class RSSPSession(EyelinkSession):

    def __init__(self, subject_initials, index_number, tracker_on, *args, **kwargs):

        super(RSSPSession, self).__init__(subject_initials, index_number, tracker_on, *args, **kwargs)

        config_file = os.path.join(os.path.abspath(os.getcwd()), 'default_settings.json')

        with open(config_file) as config_file:
            config = json.load(config_file)

        self.config = config

        self.create_screen(full_screen=True, engine='pygaze')
        self.create_stimuli()
        self.create_trials()

        self.run_time = -1
        self.stopped = False

    def create_stimuli(self):
        size_fixation_pix = self.deg2pix(self.config['size_fixation_deg'])
        self.fixation = visual.GratingStim(self.screen,
                                           tex='sin',
                                           mask='raisedCos',
                                           size=size_fixation_pix,
                                           texRes=512,
                                           color='red',
                                           sf=0,
                                           pos=(0,0))
        
        self.instruction = visual.TextStim(self.screen, 
            text = 'maintain fixation on the dot, follow it if necessary.', 
            font = 'Helvetica Neue',
            pos = (0, 0),
            italic = True, 
            height = 30, 
            alignHoriz = 'center',
            color='red')
        self.instruction.setSize((500,150))



        self.retino_tex = np.array([[1,-1],[-1,1]])
        cycles=4
        self.retino_stim = visual.PatchStim(self.screen, tex=self.retino_tex, size=self.deg2pix(self.config['max_stimulus_size']), units='pix',
            sf=cycles/self.deg2pix(self.config['max_stimulus_size']), interpolate=False, mask='raisedCos')
  


    def create_trials(self):
        """creates trials by setting up staircases for background task, and prf stimulus sequence"""

        ##################################################################################
        ## timings etc for the bar passes
        ##################################################################################

        self.nr_trials = 3



    def close(self):
        super(RSSPSession, self).close()

    def run(self):
        """run the session"""
        # cycle through trials

        self.ti = 0
        while not self.stopped:

            parameters = copy.copy(self.config)
            trial = RSSPTrial(ti=self.ti,
                           config=self.config,
                           screen=self.screen,
                           session=self,
                           parameters=parameters,
                           tracker=self.tracker)
            trial.run()
            self.ti += 1

            if self.ti == self.nr_trials:
                self.stopped = True
            if self.stopped == True:
                break

        self.close()
