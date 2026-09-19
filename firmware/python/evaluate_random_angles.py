import csv
from pathlib import Path

import numpy as np
from stable_baselines3 import SAC

from balance_env import BalanceEnv


# Use the same model path as your previous evaluation.
MODEL_PATH = Path("models/sac_balance_100k.zip")

OUTPUT_PATH = Path("grid_states_results.csv")

N_TESTS = 25

# Random initial angle range, in degrees
ANGLE_MIN_DEG = -10.0
ANGLE_MAX_DEG = 10.0

# Random initial angular velocity range, in rad/s
OMEGA_MIN_RAD_S = -0.3
OMEGA_MAX_RAD_S = 0.3

SEED = 42


# Must match the environment sampling time.
DT = 0.01
MAX_STEPS = 500
LAST_WINDOW_STEPS = round(1.0 / DT)

# Evaluation criterion: all samples in the last second
# must remain within +/- 0.5 degrees.
ANGLE_TOLERANCE_DEG = 0.5

def main():
    if not MODEL_PATH.is_file():
        raise FileNotFoundError(
            f"Model not found: {MODEL_PATH.resolve()}\n"
            "Set MODEL_PATH to the model used in your previous test."
        )

    # rng = np.random.default_rng(SEED)

    # initial_angles = rng.uniform(
    # ANGLE_MIN_DEG,
    # ANGLE_MAX_DEG,
    # size=N_TESTS,
    # )

    # initial_omegas = rng.uniform(
    # OMEGA_MIN_RAD_S,
    # OMEGA_MAX_RAD_S,
    # size=N_TESTS,
    # )

    angle_grid = np.array(
    [-10.0, -5.0, 0.0, 5.0, 10.0],
    dtype=np.float64,
    )

    omega_grid = np.array(
        [-0.3, -0.15, 0.0, 0.15, 0.3],
        dtype=np.float64,
    )

    initial_angles = np.repeat(angle_grid, len(omega_grid))
    initial_omegas = np.tile(omega_grid, len(angle_grid))



    model = SAC.load(str(MODEL_PATH), device="cpu")
    env = BalanceEnv()

    results = []

    try:
        for test_id, (
            initial_angle_deg,
            initial_omega,
        ) in enumerate(
             zip(initial_angles, initial_omegas),
             start=1,
        ):
            observation, _ = env.reset(
              seed=SEED + test_id,
              options={
              "initial_angle_deg": float(initial_angle_deg),
              "initial_omega": float(initial_omega),
              },
            )

            angles_deg = []
            omegas = []
            actions = []

            total_reward = 0.0
            terminated = False
            truncated = False

            for _ in range(MAX_STEPS):
                action, _ = model.predict(
                    observation,
                    deterministic=True,
                )

                observation, reward, terminated, truncated, _ = (
                    env.step(action)
                )

                angles_deg.append(
                    float(np.rad2deg(observation[0]))
                )
                omegas.append(float(observation[1]))
                actions.append(
                    float(np.asarray(action).reshape(-1)[0])
                )

                total_reward += float(reward)

                if terminated or truncated:
                    break

            angles_deg = np.asarray(angles_deg)
            omegas = np.asarray(omegas)
            actions = np.asarray(actions)

            steps = len(angles_deg)
            tail = angles_deg[-LAST_WINDOW_STEPS:]

            # Completing the requested five-second horizon
            # without termination.
            completed_horizon = (
                steps == MAX_STEPS and not terminated
            )

            last_1s_available = steps >= LAST_WINDOW_STEPS

            within_tolerance = bool(
                last_1s_available
                and np.all(
                    np.abs(tail) <= ANGLE_TOLERANCE_DEG
                )
            )

            passed = bool(
                completed_horizon and within_tolerance
            )

            row = {
                "test_id": test_id,
                "initial_angle_deg": float(initial_angle_deg),
                "initial_omega_rad_s": float(initial_omega),
                "steps": steps,
                "duration_s": steps * DT,
                "final_angle_deg": float(angles_deg[-1]),
                "final_omega_rad_s": float(omegas[-1]),
                "max_abs_angle_deg": max(
                    abs(float(initial_angle_deg)),
                    float(np.max(np.abs(angles_deg))),
                ),
                "max_abs_omega_rad_s": float(
                    np.max(np.abs(omegas))
                ),
                "max_abs_action": float(
                    np.max(np.abs(actions))
                ),
                "final_action": float(actions[-1]),
                "mean_abs_angle_last_1s_deg": (
                    float(np.mean(np.abs(tail)))
                    if last_1s_available else float("nan")
                ),
                "max_abs_angle_last_1s_deg": (
                    float(np.max(np.abs(tail)))
                    if last_1s_available else float("nan")
                ),
                "total_reward": total_reward,
                "terminated": bool(terminated),
                "truncated": bool(truncated),
                "completed_horizon": bool(completed_horizon),
                "passed": passed,
            }

            results.append(row)

            print(
                f"Test={test_id:03d} | "
                f"initial angle={initial_angle_deg:+7.3f} deg | "
                f"initial omega={initial_omega:+8.4f} rad/s | "
                f"steps={steps:3d} | "
                f"final={row['final_angle_deg']:+8.4f} deg | "
                f"final omega={row['final_omega_rad_s']:+9.5f} | "
                f"max|u|={row['max_abs_action']:7.3f} | "
                f"terminated={terminated} | "
                f"passed={passed}"
            )


    finally:
        env.close()

    with OUTPUT_PATH.open(
        "w", newline="", encoding="utf-8"
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=list(results[0].keys()),
        )
        writer.writeheader()
        writer.writerows(results)

    completed_count = sum(
        row["completed_horizon"] for row in results
    )
    passed_count = sum(row["passed"] for row in results)
    terminated_count = sum(
        row["terminated"] for row in results
    )

    print("\n--- Evaluation summary ---")
    print(f"Tests: {N_TESTS}")
    print(
        f"Completed 5 seconds without termination: "
        f"{completed_count}/{N_TESTS}"
    )
    print(f"Terminated episodes: {terminated_count}")
    print(
        f"Passed (+/- {ANGLE_TOLERANCE_DEG} deg "
        f"throughout the last second): "
        f"{passed_count}/{N_TESTS}"
    )
    print(f"Pass rate: {100.0 * passed_count / N_TESTS:.1f}%")
    print(f"Results saved to: {OUTPUT_PATH.resolve()}")


if __name__ == "__main__":
    main()
