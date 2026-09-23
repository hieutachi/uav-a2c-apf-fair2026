import math

import numpy as np

from scripts.a2c_new import Drone3D, aabb_signed_clearance, swept_aabb_collision, apf_action


def test_constants():
    d = Drone3D()
    assert d.mass == 0.5 and d.kd == 0.12 and abs(d.g - 9.81) < 1e-9 and d.max_f == 12.0
    assert (d.alt_min, d.alt_max) == (5.0, 6.0)


def test_force_clip_and_scale_per_axis():
    d = Drone3D()
    d.state = np.array([0, 0, 5.5, 0, 0, 0], float)
    # action beyond [-1,1] must clip per axis then scale by 12 N; wind zero.
    a = np.array([5.0, -5.0, 0.0])
    s = d.update(a, wind=np.zeros(3), dt=0.1)
    # ax = (12)/0.5 = 24 ; vx = 24*0.1 = 2.4
    assert abs(s[3] - 2.4) < 1e-9
    assert abs(s[4] + 2.4) < 1e-9


def test_semi_implicit_euler_uses_updated_velocity():
    d = Drone3D()
    d.state = np.array([0, 0, 5.5, 0, 0, 0], float)
    s = d.update(np.array([1.0, 0, 0]), wind=np.zeros(3), dt=0.1)
    vx = (12.0) / 0.5 * 0.1  # 2.4
    assert abs(s[3] - vx) < 1e-9
    assert abs(s[0] - vx * 0.1) < 1e-9  # x advanced with UPDATED velocity


def test_drag_uses_relative_air_velocity():
    d = Drone3D()
    d.state = np.array([0, 0, 5.5, 1.0, 0, 0], float)
    # zero action; wind equals velocity -> drag term zero -> only gravity on z
    s = d.update(np.zeros(3), wind=np.array([1.0, 0, 0]), dt=0.1)
    assert abs(s[3] - 1.0) < 1e-9  # vx unchanged since v-wind=0


def test_altitude_clamp_and_velocity_reset():
    d = Drone3D()
    d.state = np.array([0, 0, 5.98, 0, 0, 0], float)
    s = d.update(np.array([0, 0, 1.0]), wind=np.zeros(3), dt=0.1)
    assert 5.0 <= s[2] <= 6.0
    if s[2] in (5.0, 6.0):
        assert s[5] == 0.0  # vz reset on clamp


def test_swept_collision_detects_crossing_and_priority_semantics():
    obs = {"x": (10.0, 20.0), "y": (10.0, 20.0), "z": (0.0, 10.0)}
    assert swept_aabb_collision([0, 15, 5], [30, 15, 5], obs) is True   # passes through
    assert swept_aabb_collision([0, 0, 5], [0, 5, 5], obs) is False     # misses


def test_signed_clearance_surface_vs_inside():
    obs = {"x": (0.0, 10.0), "y": (0.0, 10.0), "z": (0.0, 10.0)}
    # outside on +x by 5 m
    assert abs(aabb_signed_clearance([15, 5, 5], obs) - 5.0) < 1e-9
    # inside -> negative nearest face depth
    assert aabb_signed_clearance([5, 5, 5], obs) < 0


def test_apf_repulsion_uses_center_distance():
    # single obstacle; place drone so nearest-surface != center distance is obvious.
    obs = [{"x": (0.0, 20.0), "y": (0.0, 2.0), "z": (0.0, 2.0)}]
    pos = np.array([10.0, 5.0, 1.0])  # center=(10,1,1); center dist=4 < d0=6
    f = apf_action(pos, target=np.array([10.0, 100.0, 1.0]), obstacles=obs)
    # repulsion should push +y (away from center at y=1); net y-component positive
    assert f[1] > 0
    assert np.all(f <= 1.0) and np.all(f >= -1.0)
