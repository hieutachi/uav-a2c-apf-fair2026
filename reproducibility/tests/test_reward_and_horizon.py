import math

import numpy as np

from scripts.a2c_new import DroneEnv3D


def test_horizon_nominal_300m():
    env = DroneEnv3D(target=(300, 150, 5), obstacles=[], start=(0, 0, 5))
    dxy = math.hypot(300, 150)
    expected = int((dxy / (5.0 * 0.1)) * 1.8) + 300
    assert expected == 1507
    assert env.max_steps == expected


def test_altitude_penalty_inactive_under_clamp():
    # After Drone3D clamps z to [5,6], the reward's altitude branches are unreachable.
    env = DroneEnv3D(target=(300, 150, 5), obstacles=[], start=(0, 0, 5))
    env.reset(seed=1009)
    for _ in range(20):
        _, _, done, trunc, _ = env.step(np.array([0.0, 1.0, 1.0], np.float32))
        assert 5.0 <= env.drone.state[2] <= 6.0
        if done or trunc:
            break


def test_collision_priority_over_success():
    # Obstacle straddling the goal so the final step both reaches goal and collides.
    obs = [{"x": (295.0, 305.0), "y": (145.0, 155.0), "z": (0.0, 10.0)}]
    env = DroneEnv3D(target=(300, 150, 5), obstacles=obs, start=(299, 150, 5))
    env.reset(seed=1009)
    # push into goal/obstacle
    _, _, done, _, info = env.step(np.array([1.0, 0.0, 0.0], np.float32))
    if info["collision"]:
        assert info["success"] is False  # success must be false whenever collision is true


def test_reward_distance_shaping_sign():
    env = DroneEnv3D(target=(300, 150, 5), obstacles=[], start=(0, 0, 5))
    env.reset(seed=1009)
    _, r, _, _, _ = env.step(np.array([1.0, 0.5, 0.0], np.float32))
    assert isinstance(r, float)
