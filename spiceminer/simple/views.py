#!/usr/bin/env python
#-*- coding:utf-8 -*-

import math

import numpy
import matplotlib.pyplot as plt
import matplotlib.widgets as widgets
from mpl_toolkits.mplot3d import Axes3D

from .. import _helpers


# Astronomical unit in km
AU = 1.4960e8


def clamp(x, divider):
    limit = x - x % divider
    return numpy.linspace(-limit, limit, 2 * (x // divider) + 1)

def prepare_axes(ax, spine_name, color, ticks):
    labels = {'red': 'x', 'green': 'y', 'blue': 'z'}
    spine = ax.spines[spine_name]
    if spine_name in ('left', 'right'):
        axis = ax.yaxis
        if spine_name == 'left':
            pos = (0.51, 0.94)
        else:
            pos = (0.47, 0.94)
    else:
        axis = ax.xaxis
        if spine_name == 'bottom':
            pos = (0.97, 0.52)
        else:
            pos = (0.97, 0.47)
    ax.text(pos[0], pos[1], labels[color] + ' [AU]', color=color, transform=ax.transAxes)
    # axis position
    spine.set_position(('data',0))
    axis.set_ticks_position(spine_name)
    # ticks
    axis.offsetText.set_visible(False)
    axis.set_ticks(ticks * AU)
    axis.set_ticklabels(ticks)
    axis.get_ticklabels()[len(ticks) // 2].set_visible(False)
    # color
    spine.set_color(color)
    for line in axis.get_ticklines():
        line.set_color(color)

def update_line(frame, line, data):
    line.set_data(data[:2, :frame])
    try:
        line.set_3d_properties(data[2:, :frame])
    except AttributeError:
        pass
    return line

def update_points(frame, patch, data):
    patch.set_offsets(data[:2, frame - 1])
    try:
        patch.set_3d_properties(data[2:, frame - 1], 'z')
    except AttributeError:
        pass
    return patch


class QuadView(object):
    def __init__(self, title, limit, figsize=(12,9.0625), dpi=100):
        self.items = []
        self.figure = plt.figure(num=1, figsize=figsize, dpi=dpi)
        self.figure.subplots_adjust(0, 0, 1, 1, 0, 0)
        self.axes = {
            '3d': plt.subplot2grid((32,2), (0,0), rowspan=20, projection='3d'),
            'z': plt.subplot2grid((32,2), (0,1), rowspan=20),
            'x': plt.subplot2grid((32,2), (20,0), rowspan=10),
            'y': plt.subplot2grid((32,2), (20,1), rowspan=10)
        }
        self.controls = {
            'play': plt.subplot2grid((32,10), (30,0), rowspan=2),
            'slider': plt.subplot2grid((32,10), (30,1), rowspan=2, colspan=9)
        }
        self.widgets = {
            'play': widgets.Button(self.controls['play'], 'Pause'),
            'slider': widgets.Slider(self.controls['slider'], '', 0, 1, 0)
        }
        self._set_limits(limit)
        ticks = clamp(limit / AU, 0.25 * int(limit / AU))
        self._prepare_3d(title, ticks)
        self._prepare_2d(limit, ticks)

    def add(self, startpoint, args):
        lines = [
            self.axes['3d'].plot(*startpoint, **args)[0],
            self.axes['z'].plot(*startpoint[:2], **args)[0],
            self.axes['x'].plot(*startpoint[1:], **args)[0],
            self.axes['y'].plot(*startpoint[0::2], **args)[0]
        ]
        points = [
            self.axes['3d'].scatter(*startpoint, **args),
            self.axes['z'].scatter(*startpoint[:2], **args),
            self.axes['x'].scatter(*startpoint[1:], **args),
            self.axes['y'].scatter(*startpoint[0::2], **args)
        ]
        for point in points:
            point.set_color(lines[0].get_color())
        self.items.append((lines, points))

    def update(self, time_, line_data):
        for lp, data in zip(self.items, line_data):
            lines, points = lp
            frame = data.shape[1]
            update_line(frame, lines[0], data)
            update_line(frame, lines[1], data[:2])
            update_line(frame, lines[2], data[1:])
            update_line(frame, lines[3], data[0::2])
            update_points(frame, points[0], data)
            update_points(frame, points[1], data[:2])
            update_points(frame, points[2], data[1:])
            update_points(frame, points[3], data[0::2])
            points[0].set_color(lines[0].get_color())


    def _set_limits(self, limit):
        for ax in self.axes.values():
            ax.grid(True)
            ax.set_xlim((-limit , limit))
            ax.set_ylim((-limit, limit))
        self.axes['3d'].set_zlim((-limit, limit))

    def _prepare_3d(self, title, ticks):
        ax = self.axes['3d']
        #title
        ax.set_title(title, position=(0.5, 0.95))
        # change ticks
        for axis in (ax.w_xaxis, ax.w_yaxis, ax.w_zaxis):
            axis.set_ticks(ticks[1::2] * AU)
            axis.set_ticklabels(ticks[1::2])
        # plot spines
        l0 = numpy.identity(3) * ticks[-1] * AU
        l1 = l0 * -1
        for i, color in enumerate(['red', 'green', 'blue']):
            ax.plot(*zip(l0[i], l1[i]), c=color, alpha=0.4)

    def _prepare_2d(self, limit, ticks):
        half_limit = limit / 2
        half_ticks = math.ceil((len(ticks) - 1) / 4.0)
        half_ticks = ticks[half_ticks:-half_ticks]
        ax = self.axes['z']
        # title
        ax.set_title('XY-plane')
        ax.title.set_position((0.1, 0.935))
        # y-axis
        prepare_axes(ax, 'right', 'green', ticks)
        # x-axis
        prepare_axes(ax, 'top', 'red', ticks)

        ax = self.axes['y']
        # title
        ax.set_title('XZ-plane')
        ax.title.set_position((0.1, 0.88))
        # y-axis
        ax.set_ylim((-half_limit, half_limit))
        prepare_axes(ax, 'right', 'blue', half_ticks)
        # x-axis
        prepare_axes(ax, 'bottom', 'red', ticks)

        ax = self.axes['x']
        # title
        ax.set_title('YZ-plane')
        ax.title.set_position((0.1, 0.88))
        # y-axis
        ax.set_ylim(-half_limit, half_limit)
        prepare_axes(ax, 'left', 'blue', half_ticks)
        # x-axis
        prepare_axes(ax, 'bottom', 'green', ticks)
