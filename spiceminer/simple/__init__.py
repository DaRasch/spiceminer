#!/usr/bin/env python
#-*- coding:utf-8 -*-

import numpy
import matplotlib.pyplot as plt

from . import views
from . import animation
from .. import kernel
from ..time_ import Time
from ..bodies import Body

import pdb


class BodyData(object):
    def __init__(self, body, args, times):
        self.body = Body(body)
        self.plotargs = args
        self.data = self.body.position(times)


class SpiceAnimation(animation.PlaybackController):
    def __init__(self, path='.', bodies=None, times=None, title=None, **animargs):
        kernel.load(path, force_reload=True)
        if times is None:
            times =numpy.arange(Time.now() - 56 * Time.WEEK, Time.now(), Time.DAY, dtype=float)
        if title is None:
            title = 'From {}\nto {}'.format(str(Time.fromposix(times[0])), str(Time.fromposix(times[-1])))
        self.bodydata = [BodyData(body, args, times) for body, args in bodies.items()]
        limit = max(item.data[1:3].max() for item in self.bodydata) * 1.1
        frame_count = max(len(item.data[0]) for item in self.bodydata)

        self._view = views.QuadView(title, limit)
        self._view.widgets['play'].on_clicked(self._play_cb)
        self._view.widgets['slider'].on_changed(self._slider_cb)
        for item in self.bodydata:
            self._view.add(item.data[1:,:1], item.plotargs)
        super(self.__class__, self).__init__(self._view.figure, frame_count, **animargs)

    def _play_cb(self, event):
        super(self.__class__, self)._pause()

    def _slider_cb(self, pos):
        self.current_frame = int(pos * self.frame_count)

    def _draw_frame(self, frame):
        self._view.update(Time.fromposix(
            self.bodydata[0].data[0, frame - 1]),
            [item.data[1:, :frame] for item in self.bodydata]
        )
        slider = self._view.widgets['slider']
        slider.eventson = False
        slider.set_val(frame / float(self.frame_count))
        slider.eventson = True

    def show(self):
        try:
            plt.show(self._view.figure)
        finally:
            plt.close(self._view.figure)

    def close(self):
        try:
            plt.close(self._view.figure)
        except Exception:
            pass
