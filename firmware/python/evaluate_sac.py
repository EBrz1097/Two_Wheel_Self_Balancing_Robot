import numpy as np
from stable_baselines3 import SAC

from balance_env import BalanceEnv


def main():
    model_path = "models/sac_balance_100k.zip"

    env = BalanceEnv()
    model = SAC.load(model_path)

    n_episodes = 5

    episode_rewards = []
    episode_lengths = []
    maximum_angles = []

    try:
        for episode in range(1, n_episodes + 1):
            observation, info = env.reset()

            terminated = False
            truncated = False
            episode_reward = 0.0
            step_count = 0
            max_abs_angle_deg = 0.0

            while not (terminated or truncated):
                # Deterministic evaluation: no exploration noise
                action, _states = model.predict(
                    observation,
                    deterministic=True,
                )

                observation, reward, terminated, truncated, info = env.step(action)

                episode_reward += reward
                step_count += 1

                angle_deg = np.rad2deg(observation[0])
                max_abs_angle_deg = max(
                    max_abs_angle_deg,
                    abs(float(angle_deg)),
                )

            episode_rewards.append(episode_reward)
            episode_lengths.append(step_count)
            maximum_angles.append(max_abs_angle_deg)

            print(
                f"Episode {episode}: "
                f"reward={episode_reward:.3f}, "
                f"steps={step_count}, "
                f"time={step_count * env.Ts:.2f} s, "
                f"max|angle|={max_abs_angle_deg:.3f} deg, "
                f"terminated={terminated}, "
                f"truncated={truncated}"
            )

        print("\nEvaluation summary")
        print("------------------")
        print(f"Mean reward: {np.mean(episode_rewards):.3f}")
        print(f"Mean episode length: {np.mean(episode_lengths):.2f} steps")
        print(f"Mean episode time: {np.mean(episode_lengths) * env.Ts:.3f} s")
        print(f"Mean max absolute angle: {np.mean(maximum_angles):.3f} deg")

    finally:
        env.close()


if __name__ == "__main__":
    main()
