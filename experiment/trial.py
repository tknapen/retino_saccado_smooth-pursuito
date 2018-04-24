from __future__ import division
from exptools.core.trial import Trial
import os
import exptools
import json
from psychopy import logging, visual, event
import math
import numpy as np


class RSSPTrial(Trial):

    def __init__(self, ti, config, stimulus=None, parameters=None, *args, **kwargs):

        self.ID = ti

        phase_durations = [-0.001, parameters['fix_time'], parameters['stim_time'], parameters['post_fix_time']]

        super(
            RSSPTrial,
            self).__init__(
            phase_durations=phase_durations,
            *args,
            **kwargs)

        self.parameters = parameters
        # these are placeholders, to be filled in later
        self.parameters['answer'] = -1

        if self.ID in (0,2):
            # create jump times:
            self.transition_times = np.r_[0,np.cumsum(np.random.exponential(self.session.config['back_and_forth_period']/10, size=50000)+0.25)]
            self.transition_times = self.transition_times[self.transition_times < parameters['stim_time']]


    def get_stimulus_pos(self, time):
        rotation_period = (self.session.config["stim_time"]/self.session.config["nr_periods"])

        if self.ID in (0,1):  # Smooth Pursuit
            time_in_rotation_period = time # math.fmod(time, rotation_period)
            continuous_time = time
        elif self.ID == 2:  # Retinotopy and Saccades go in jumps
            time_in_rotation_period = math.fmod(self.transition_times[self.transition_times<time][-1], rotation_period)
            continuous_time = time_in_rotation_period
            
        phase_in_rotation_period = math.pi*time_in_rotation_period/rotation_period
        # rotation_angle = math.sin(phase_in_rotation_period)
        c, s = np.cos(phase_in_rotation_period), np.sin(phase_in_rotation_period)
        R = np.array(((c,-s), (s, c)))

        phase_in_back_and_forth_period = 2.0*math.pi*continuous_time / self.session.config['back_and_forth_period']
        back_and_forth_x = math.sin(phase_in_back_and_forth_period) * self.session.deg2pix(self.session.config['max_amplitude'])
        xy = np.array([back_and_forth_x, 0])
        xy_pos = np.dot(xy, R)
        return xy_pos

    def get_stimulus_scale(self, pos):
        norm_ecc = np.linalg.norm(pos) / self.session.deg2pix(self.parameters['max_amplitude'])
        rr = self.parameters['max_stimulus_size'] - self.parameters['min_stimulus_size']
        return self.session.deg2pix(self.parameters['min_stimulus_size'] + (norm_ecc*rr))


    def draw(self, *args, **kwargs):

        # draw additional stimuli:
        if (self.phase == 0 ) * (self.ID == 0):
            self.session.instruction.draw()

        if self.phase == 1:
            self.session.fixation.setPos([0,0])

        if self.phase == 2:
            if self.ID == 0:
                self.session.fixation.setPos([0,0])
                self.session.retino_stim.setPos(self.get_stimulus_pos(self.this_phase_time))
                self.session.retino_stim.setSize(self.get_stimulus_scale(self.get_stimulus_pos(self.this_phase_time)))
                time_tex = self.session.retino_tex * np.sin(self.this_phase_time * 2 * math.pi * self.parameters['stim_flicker_frequency'] )
                self.session.retino_stim.setTex(time_tex)
                self.session.retino_stim.draw()
            else:
                self.session.fixation.setPos(self.get_stimulus_pos(self.this_phase_time))

        if self.phase == 3:
            self.session.fixation.setPos([0,0])

        self.session.fixation.draw()          # always draw fixation
        super(RSSPTrial, self).draw()


    def event(self):

        for ev in event.getKeys():
            if len(ev) > 0:
                if ev in ['esc', 'escape', 'q']:
                    self.events.append(
                        [-99, self.session.clock.getTime() - self.start_time])
                    self.stop()
                    self.session.stopped = True
                    print 'run canceled by user'
                if ev in ['space', ' ', 't']:
                    if self.phase == 0:
                        if self.ID == 0:
                            self.session.run_time = self.session.clock.getTime()
                        self.t_time = self.session.clock.getTime()
                        self.phase_forward()
            super(RSSPTrial, self).key_event(ev)
