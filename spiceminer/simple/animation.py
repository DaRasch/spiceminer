#!/usr/bin/env python
#-*- coding:utf-8 -*-

import numpy
import matplotlib.animation as anim

from ..time_ import Time


class PlaybackController(anim.TimedAnimation):
    '''Mixin class to add playback control keys.'''
    def __init__(self, fig, frame_count, current_frame=1, paused=False, **animargs):
        self.frame_count = frame_count
        self.current_frame = frame_count
        self.paused = paused
        fig.canvas.mpl_connect('key_press_event', self.playback_handler)
        anim.TimedAnimation.__init__(self, fig, **animargs)

    def playback_handler(self, event, *args):
        {
        ' ': self._pause,
        'down': lambda: self._rewind(self.frame_count // 10),
        'up': lambda: self._skip(self.frame_count // 10)
        }.get(event.key, lambda: None)()

    def _pause(self):
            self.paused ^= True
    def _restart(self):
        self.current_frame = 1
    def _rewind(self, amount):
        self.current_frame = max(1, self.current_frame - amount)
    def _skip(self, amount):
        self.current_frame = min(self.frame_count - 1, self.current_frame + amount)

    def new_frame_seq(self):
        return self._iter_frames()

    def _iter_frames(self):
        '''A hack to allow jumping around in the animation by setting the
        current frame.'''
        self.current_frame = 1
        while self.current_frame <= self.frame_count:
            yield self.current_frame
            if not self.paused:
                self.current_frame += 1
