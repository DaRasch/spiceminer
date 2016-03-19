#-*- coding:utf-8 -*-

import numpy as np

import spiceminer as sm


def _stamp_angles_falloff(angles, falloff, resolution):
    falloff = np.vectorize(falloff, otypes=[float])
    m, n = resolution
    d_phi = 2 * np.pi / float(m)
    d_theta = np.pi / float(n)
    stamp_shape = [
        int(angles[1] / d_theta) * 2 + 1,
        int(angles[0] / d_phi) * 2 + 1]
    q, p = stamp_shape
    q2, p2 = q // 2, p // 2
    x_grid, y_grid = np.mgrid[-q2:q2 + 1, -p2:p2 + 1]
    x_grid, y_grid = x_grid * d_phi, y_grid * d_theta
    stamp = falloff(x_grid, y_grid)
    return stamp, x_grid, y_grid

def _stamp_resample(stamp, angles, resolution):
    import scipy.ndimage as ndimage
    m, n = resolution
    q, p = stamp.shape
    d_phi = 2 * np.pi / float(m)
    d_theta = np.pi / float(n)
    d_phi_old = 2 * angles[0] / float(p)
    d_theta_old = 2 * angles[1] / float(q)
    zoom_phi = d_phi / d_phi_old
    zoom_theta = d_theta / d_theta_old
    return ndimage.zoom(stamp, zoom=(zoom_theta, zoom_phi), order=3)

def _apply_stamp(skymap, stamp, phi, theta):
    umax = np.vectorize(max)
    n, m = skymap.shape
    q, p = stamp.shape
    q2, p2 = q // 2, p // 2
    x = int(np.interp(phi, [-np.pi, np.pi], [0, m]))
    y = int(np.interp(theta, [-np.pi, np.pi], [0, n]))
    uneven = p & 1, q & 1
    bounds = np.array([
        x - p2,
        y - q2,
        x + p2 + uneven[0],
        y + q2 + uneven[1]
    ], dtype=int)
    ldx, ldy = ldiffs = -bounds[:2].clip(max=0)
    udx, udy = udiffs = -(np.array([m, n]) - bounds[2:]).clip(max=0)
    lbx, lby = bounds[:2] + ldiffs
    ubx, uby = bounds[2:] - udiffs
    skymap[lby:uby, lbx:ubx] = umax(skymap[lby:uby, lbx:ubx], stamp[ldy: q - udy, ldx: p - udx])
    if ldx:
        skymap[lby:uby, -ldx:] = umax(skymap[lby:uby, -ldx:], stamp[ldy: q - udy, :ldx])
    if udx:
        skymap[lby:uby, :udx] = umax(skymap[lby:uby, :udx], stamp[ldy: q - udy, -udx:])
    if ldy:
        skymap[-ldy:, lbx:ubx] = umax(skymap[-ldy:, lbx:ubx], stamp[:ldy, ldx: p - udx])
    if udy:
        skymap[:udy, lbx:ubx] = umax(skymap[:udy, lbx:ubx], stamp[-udy:, ldx: p - udx])


class SkyMapper(object):
    def __init__(self, parent, stamp, resolution):
        '''
        parent: Body
        stamp: ndarray
        resolution: 2-tuple of int
            x, y
        '''
        self.parent = sm.Body(parent)
        self.stamp = stamp
        self.resolution = resolution

    @classmethod
    def ellipse(cls, parent, angles, falloff=None, resolution=(360, 180)):
        if falloff is None:
            falloff = lambda phi, theta: 1.0
        stamp, x_dist, y_dist = _stamp_angles_falloff(angles, falloff, resolution)
        mask = x_dist**2 / angles[0]**2.0 + y_dist**2.0 / angles[1]**2 > 1
        stamp[mask] = 0
        return cls(parent, stamp, resolution)

    @classmethod
    def rectangle(cls, parent, angles, falloff=None, resolution=(360, 180)):
        if falloff is None:
            falloff = lambda phi, theta: 1.0
        stamp = _stamp_angles_falloff(angles, falloff, resolution)[0]
        return cls(parent, stamp, resolution)

    @classmethod
    def customstamp(cls, parent, angles, stamp, resolution=(360, 180)):
        stamp = _stamp_resample(stamp, angles, resolution)
        return cls(parent, stamp, resolution, **kwargs)

    def _make_skymap(self, vectors):
        skymap = np.zeros(shape=self.resolution[::-1])
        coords = sm.cartesian2sphere(vectors)
        for phi, theta in coords[1:].T:
            _apply_stamp(skymap, self.stamp, phi, theta - np.pi / 2)
        return skymap

    def fixed(self, times, offset=None, frame='ECLIPJ2000'):
        _, matrices = self.parent.rotation(times, target=frame)
        vectors = np.array([mat.dot(np.array([1,0,0])) for mat in matrices]).T
        return self._make_skymap(vectors)

    def tracking(self, times, target='SUN', frame='ECLIPJ2000'):
        vectors = target.position(times, observer=self.parent, frame=frame)[1:]
        return self._make_skymap(vectors)


class InstrumentSkyMapper(object):
    def __init__(self, instrument, falloff=None, resolution=(360, 180)):
        '''
        parent: Body
        resolution: 2-tuple of int
            x, y
        '''
        self.parent = sm.Body(instrument)
        if falloff is None:
            falloff = lambda phi, theta: 1.0
        shape, frame, boresight, bounds = self.parent.fov()
        self.boresight = boresight
        if shape in ('CIRCLE', 'POLYGON'):
            angles = [sm.angle(boresight, bounds[:, 0])] * 2
        elif shape == 'RECTANGLE':
            va = bounds[:, 0] + (bounds[:, 1] - bounds[:, 0]) / 2
            vb = bounds[:, 1] + (bounds[:, 2] - bounds[:, 1]) / 2
            angles = [sm.angle(boresight, va), sm.angle(boresight, vb)]
        else:
            va, vb = bounds[:, 0], bounds[:, 1]
            angles = [sm.angle(boresight, va). sm.angle(boresight, vb)]
        self.stamp, x_grid, y_grid = _stamp_angles_falloff(angles, falloff, resolution)
        if shape in ('CIRCLE', 'ELLIPSE'):
            mask = (x_grid**2 / angles[0]**2.0 + y_grid**2.0 / angles[1]**2) > 1
            self.stamp[mask] = 0
        self.resolution = resolution

    def _make_skymap(self, vectors):
        skymap = np.zeros(shape=self.resolution[::-1])
        coords = sm.cartesian2sphere(vectors)
        for phi, theta in coords[1:].T:
            _apply_stamp(skymap, self.stamp, phi, theta - np.pi / 2)
        return skymap

    def fixed(self, times, frame='ECLIPJ2000'):
        _, matrices = self.parent.rotation(times, target=frame)
        vectors = np.array([mat.dot(self.boresight) for mat in matrices]).T
        return self._make_skymap(vectors)
