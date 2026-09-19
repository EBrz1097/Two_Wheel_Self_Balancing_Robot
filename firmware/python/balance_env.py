import gymnasium as gym
from gymnasium import spaces
import numpy as np

from dynamics import Ad, Bd, Ts


class BalanceEnv(gym.Env):
    """Simple two-state self-balancing robot environment.

    State:
        x[0] = angle in rad
        x[1] = angular velocity in rad/s

    Action:
        u = normalized PWM input used directly in the model
        Hardware PWM = 40 * u
    """

    metadata = {"render_modes": []}

    def __init__(self):
        super().__init__()

        # Sampling time
        self.Ts = Ts

        # System matrices
        self.Ad = np.asarray(Ad, dtype=np.float64)
        self.Bd = np.asarray(Bd, dtype=np.float64).reshape(-1)

        # Input limit:
        # Hardware PWM is limited to [-1000, 1000]
        # PWM = 40 * u  =>  u in [-25, 25]
        self.u_max = 25.0

        # Episode termination angle, in radians
        self.theta_limit = np.deg2rad(30.0)

        # Observation space: [angle, angular velocity]
        # Keep angle unbounded here because the terminal observation
        # may exceed the termination threshold.
        self.observation_space = spaces.Box(
            low=np.array([-np.inf, -np.inf], dtype=np.float32),
            high=np.array([np.inf, np.inf], dtype=np.float32),
            dtype=np.float32,
        )

        # Continuous action space: [u]
        self.action_space = spaces.Box(
            low=np.array([-self.u_max], dtype=np.float32),
            high=np.array([self.u_max], dtype=np.float32),
            dtype=np.float32,
        )

        self.state = None
        self.step_count = 0

        # 500 steps at Ts = 0.01 s correspond to 5 seconds
        self.max_steps = 500

    def reset(self, *, seed=None, options=None):
        super().reset(seed=seed)

        options = options or {}

        initial_angle_deg = float(
            options.get("initial_angle_deg", 5.0)
        )
        initial_omega = float(
            options.get("initial_omega", 0.0)
        )

        self.state = np.array(
            [
                np.deg2rad(initial_angle_deg),
                initial_omega,
            ],
            dtype=np.float64,
        )

        self.step_count = 0

        observation = self.state.astype(np.float32)
        info = {
            "initial_angle_deg": initial_angle_deg,
            "initial_omega": initial_omega,
        }

        return observation, info


    def step(self, action):
        # Convert action to scalar
        u = float(np.asarray(action).reshape(-1)[0])

        # Protect the physical input limit
        u = float(np.clip(u, -self.u_max, self.u_max))

        # State transition: x_next = Ad @ x + Bd * u
        self.state = self.Ad @ self.state + self.Bd * u

        self.step_count += 1

        # Updated state used for reward and termination
        theta = float(self.state[0])
        omega = float(self.state[1])

        # End the episode if the updated angle reaches either limit
        terminated = bool(abs(theta) >= self.theta_limit)

        # Time-limit condition
        truncated = bool(self.step_count >= self.max_steps)

        # Reward: penalize angle, angular velocity, and control effort
        reward = -(
            10.0 * theta**2
            + 0.5 * omega**2
            + 0.001 * u**2
        )

        # Additional penalty for crossing the angle limit
        if terminated:
            reward -= 100.0

        observation = self.state.astype(np.float32)

        info = {
            "u": u,
            "pwm": 40.0 * u,
        }

        return observation, float(reward), terminated, truncated, info
