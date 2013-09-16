#-*- coding:utf-8 -*-

import numpy as np

__all__ = ['angle']


def angle(v0, v1):
    u_v0 = v0 / np.linalg.norm(v0)
    u_v1 = v1 / np.linalg.norm(v1)
    angle = np.arccos(np.dot(u_v0, u_v1))
    if np.isnan(angle):
        if (u_v0 == u_v1).all():
            return 0.0
        else:
            return np.pi
    return angle
