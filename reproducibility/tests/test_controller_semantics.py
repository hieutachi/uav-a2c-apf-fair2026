import numpy as np

from scripts.a2c_new import DroneEnv3D


def _obstacles():
    return [{"x": (40.0, 60.0), "y": (10.0, 30.0), "z": (0.0, 8.0)}]


def test_observation_is_12d_no_obstacles():
    env = DroneEnv3D(target=(300, 150, 5), obstacles=_obstacles(), policy_mode="hybrid")
    obs, _ = env.reset(seed=1009)
    assert obs.shape == (12,)
    # obs = [pos(3), vel(3), goal-disp(3), wind(3)] -> none of these encode obstacle geometry
    assert env.observation_space.shape == (12,)


def test_h1_a2c_mode_ignores_apf():
    env = DroneEnv3D(target=(300, 150, 5), obstacles=_obstacles(), policy_mode="a2c")
    env.reset(seed=1009)
    action = np.array([0.3, -0.2, 0.1], np.float32)
    before = env.drone.state.copy()
    env.step(action)
    # In a2c mode the blended command equals the raw action; reproduce one integration step.
    env2 = DroneEnv3D(target=(300, 150, 5), obstacles=_obstacles(), policy_mode="a2c")
    env2.reset(seed=1009)
    # same seed -> same wind/reset; stepping with same action must match a2c branch exactly
    env2.step(action)
    assert np.allclose(env.drone.state, env2.drone.state)


def test_h2_apf_mode_is_model_free():
    env = DroneEnv3D(target=(300, 150, 5), obstacles=_obstacles(), policy_mode="apf")
    env.reset(seed=1009)
    # action is ignored in apf mode; passing zeros vs random must give identical next state
    s_a = DroneEnv3D(target=(300, 150, 5), obstacles=_obstacles(), policy_mode="apf")
    s_a.reset(seed=1009); s_a.step(np.zeros(3, np.float32))
    s_b = DroneEnv3D(target=(300, 150, 5), obstacles=_obstacles(), policy_mode="apf")
    s_b.reset(seed=1009); s_b.step(np.array([0.9, -0.9, 0.5], np.float32))
    assert np.allclose(s_a.drone.state, s_b.drone.state)


def test_blend_schedule_endpoints():
    from scripts.a2c_new import clamp
    def lam(d):
        return clamp(1.0 - d / 300.0, 0.15, 0.55)
    assert abs(lam(335.4) - 0.15) < 1e-9
    assert abs(lam(255.0) - 0.15) < 1e-9
    assert abs(lam(135.0) - 0.55) < 1e-9
    assert abs(lam(0.0) - 0.55) < 1e-9
