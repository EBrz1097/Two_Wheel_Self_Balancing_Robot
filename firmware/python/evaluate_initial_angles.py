import numpy as np
from stable_baselines3 import SAC

from balance_env import BalanceEnv


def main():
    # بارگذاری مدل آموزش‌دیده
    model = SAC.load(
        "models/sac_balance_100k.zip",
        device="cpu",
    )

    # زوایای اولیه برای تست پایداری ربات/سیستم
    initial_angles = [-10.0, -5.0, -2.0, 0.0, 2.0, 5.0, 10.0]
    max_steps = 500

    for initial_angle_deg in initial_angles:
        env = BalanceEnv()

        try:
            observation, info = env.reset(
                options={
                    "initial_angle_deg": initial_angle_deg,
                    "initial_omega": 0.0,
                }
            )

            terminated = False
            truncated = False
            total_reward = 0.0
            max_abs_angle_deg = abs(initial_angle_deg)
            final_angle_deg = initial_angle_deg
            final_omega = 0.0
            step = 0

            for step in range(max_steps):
                action, _ = model.predict(
                    observation,
                    deterministic=True,
                )

                observation, reward, terminated, truncated, info = env.step(action)

                total_reward += float(reward)

                final_angle_deg = float(np.rad2deg(observation[0]))
                final_omega = float(observation[1])
                max_abs_angle_deg = max(
                    max_abs_angle_deg,
                    abs(final_angle_deg),
                )

                if terminated or truncated:
                    break

            print(
                f"Initial angle={initial_angle_deg:6.1f} deg | "
                f"steps={step + 1:3d} | "
                f"final angle={final_angle_deg:8.3f} deg | "
                f"final omega={final_omega:9.5f} rad/s | "
                f"max angle={max_abs_angle_deg:8.3f} deg | "
                f"reward={total_reward:9.3f} | "
                f"terminated={terminated} | "
                f"truncated={truncated}"
            )

        finally:
            env.close()


if __name__ == "__main__":
    main()
