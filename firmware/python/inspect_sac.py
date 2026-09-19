from pathlib import Path
import math

import matplotlib.pyplot as plt
import numpy as np
from stable_baselines3 import SAC

from balance_env import BalanceEnv


EVALUATION_TIME_S = 5.0
TAIL_WINDOW_S = 1.0
PWM_GAIN = 40.0
TIME_TOLERANCE = 1e-9


def main():
    project_dir = Path(__file__).resolve().parent
    model_path = project_dir / "models" / "sac_balance_100k.zip"
    output_dir = project_dir / "results"
    output_dir.mkdir(parents=True, exist_ok=True)

    model = SAC.load(str(model_path), device="cpu")
    env = BalanceEnv()

    try:
        observation, info = env.reset()

        ts = float(env.Ts)
        if not np.isfinite(ts) or ts <= 0:
            raise ValueError(f"env.Ts must be positive and finite, got {ts!r}")

        initial_observation = np.asarray(
            observation,
            dtype=float,
        ).reshape(-1)

        if initial_observation.size < 2:
            raise ValueError(
                "The observation must contain at least angle and angular velocity."
            )

        states = [initial_observation.copy()]
        actions = []
        rewards = []

        terminated = False
        truncated = False

        # Maximum number of simulation steps for the requested duration.
        max_steps = int(
            math.floor(EVALUATION_TIME_S / ts + TIME_TOLERANCE)
        )

        if max_steps <= 0:
            raise ValueError(
                f"Invalid maximum step count: {max_steps}. Ts={ts}"
            )

        for _ in range(max_steps):
            action, _ = model.predict(
                observation,
                deterministic=True,
            )

            action_array = np.asarray(action, dtype=float).reshape(-1)

            if action_array.size != 1:
                raise ValueError(
                    f"Expected one continuous action, got "
                    f"{action_array.size} values."
                )

            low = float(
                np.asarray(env.action_space.low, dtype=float)
                .reshape(-1)[0]
            )
            high = float(
                np.asarray(env.action_space.high, dtype=float)
                .reshape(-1)[0]
            )

            u = float(np.clip(action_array[0], low, high))

            if not np.isfinite(u):
                raise ValueError(f"Policy returned a non-finite action: {u}")

            # Keep the action shape compatible with a one-dimensional Box space.
            applied_action = np.asarray([u], dtype=np.float32)

            step_result = env.step(applied_action)

            if len(step_result) != 5:
                raise ValueError(
                    "BalanceEnv.step() must return:"
                    " observation, reward, terminated, truncated, info"
                )

            observation, reward, terminated, truncated, info = step_result

            next_state = np.asarray(
                observation,
                dtype=float,
            ).reshape(-1)

            if next_state.size < 2:
                raise ValueError(
                    "The observation returned by env.step() must contain "
                    "at least angle and angular velocity."
                )

            states.append(next_state.copy())
            actions.append(u)
            rewards.append(float(reward))

            if terminated or truncated:
                break

        states = np.asarray(states, dtype=float)
        actions = np.asarray(actions, dtype=float)
        rewards = np.asarray(rewards, dtype=float)

        if actions.size == 0:
            print("Rollout ended without taking any action.")
            return

        state_times = np.arange(len(states), dtype=float) * ts
        action_times = np.arange(len(actions), dtype=float) * ts

        angle_deg = np.rad2deg(states[:, 0])
        omega = states[:, 1]

        # Select states recorded during the final one-second window.
        final_time = state_times[-1]
        tail_mask = state_times >= (
            final_time - TAIL_WINDOW_S - TIME_TOLERANCE
        )
        tail_angles = angle_deg[tail_mask]

        if tail_angles.size == 0:
            tail_angles = angle_deg[-1:]

        action_low = float(
            np.asarray(env.action_space.low, dtype=float)
            .reshape(-1)[0]
        )
        action_high = float(
            np.asarray(env.action_space.high, dtype=float)
            .reshape(-1)[0]
        )

        saturated = (
            np.isclose(actions, action_low, atol=1e-3, rtol=0)
            | np.isclose(actions, action_high, atol=1e-3, rtol=0)
        )

        print(f"Duration: {len(actions) * ts:.2f} s")
        print(f"Total reward: {np.sum(rewards):.3f}")
        print(f"Final angle: {angle_deg[-1]:.4f} deg")
        print(f"Final angular velocity: {omega[-1]:.5f} rad/s")
        print(
            f"Maximum absolute angle: "
            f"{np.max(np.abs(angle_deg)):.4f} deg"
        )
        print(
            f"Last-window mean angle: "
            f"{np.mean(tail_angles):.4f} deg"
        )
        print(
            f"Last-window RMS angle: "
            f"{np.sqrt(np.mean(tail_angles ** 2)):.4f} deg"
        )
        print(
            f"Maximum absolute action: "
            f"{np.max(np.abs(actions)):.4f}"
        )
        print(
            f"Action saturation: "
            f"{100.0 * np.mean(saturated):.2f}%"
        )
        print(f"terminated={terminated}, truncated={truncated}")

        fig, axes = plt.subplots(
            3,
            1,
            figsize=(10, 8),
            sharex=False,
        )

        axes[0].plot(state_times, angle_deg)
        axes[0].axhline(
            0,
            color="black",
            linewidth=0.8,
            linestyle="--",
        )
        axes[0].set_ylabel("Angle (deg)")
        axes[0].set_title("SAC Balance Response")

        axes[1].plot(state_times, omega)
        axes[1].set_ylabel("Angular velocity (rad/s)")

        # Action u[k] applies over [k*Ts, (k+1)*Ts).
        action_edges = np.arange(len(actions) + 1, dtype=float) * ts
        axes[2].stairs(actions, action_edges)
        axes[2].set_ylabel("Control u")
        axes[2].set_xlabel("Time (s)")

        for axis in axes:
            axis.grid(True, alpha=0.3)

        fig.tight_layout()

        plot_path = output_dir / "sac_100k_response.png"
        fig.savefig(plot_path, dpi=180, bbox_inches="tight")

        # Each CSV row contains the state before applying the action,
        # the action, and the state after applying it.
        csv_path = output_dir / "sac_100k_trace.csv"

        trace = np.column_stack(
            [
                action_times,
                states[:-1, 0],
                states[:-1, 1],
                actions,
                PWM_GAIN * actions,
                states[1:, 0],
                states[1:, 1],
                rewards,
            ]
        )

        np.savetxt(
            csv_path,
            trace,
            delimiter=",",
            header=(
                "time_s,theta_rad,omega_rad_s,u,pwm_command,"
                "next_theta_rad,next_omega_rad_s,reward"
            ),
            comments="",
        )

        print(f"Plot saved to: {plot_path}")
        print(f"Trace saved to: {csv_path}")

        plt.show()

    finally:
        env.close()


if __name__ == "__main__":
    main()
