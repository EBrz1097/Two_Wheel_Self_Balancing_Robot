import numpy as np
from stable_baselines3 import SAC

from balance_env import BalanceEnv


def main():
    model = SAC.load("models/sac_balance_initial.zip")
    env = BalanceEnv()

    try:
        observation, info = env.reset()

        terminated = False
        truncated = False
        step = 0

        actions = []

        print(" step | angle(deg) | omega      | action(u) | PWM")
        print("------+------------+------------+-----------+---------")

        while not (terminated or truncated):
            action, _ = model.predict(
                observation,
                deterministic=True,
            )

            action_value = float(np.asarray(action).reshape(-1)[0])
            actions.append(action_value)

            observation, reward, terminated, truncated, info = env.step(action)

            angle_deg = np.rad2deg(float(observation[0]))
            omega = float(observation[1])
            pwm = 40.0 * action_value

            if step < 20 or step % 5 == 0 or terminated or truncated:
                print(
                    f"{step + 1:5d} | "
                    f"{angle_deg:10.3f} | "
                    f"{omega:10.3f} | "
                    f"{action_value:9.3f} | "
                    f"{pwm:7.3f}"
                )

            step += 1

        actions = np.asarray(actions)

        print("\nSummary")
        print("-------")
        print(f"Steps: {step}")
        print(f"Minimum action: {actions.min():.3f}")
        print(f"Maximum action: {actions.max():.3f}")
        print(f"Mean action: {actions.mean():.3f}")
        print(f"Mean absolute action: {np.mean(np.abs(actions)):.3f}")

    finally:
        env.close()


if __name__ == "__main__":
    main()
