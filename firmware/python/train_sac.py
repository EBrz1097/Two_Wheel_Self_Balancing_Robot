from pathlib import Path

from stable_baselines3 import SAC
from stable_baselines3.common.monitor import Monitor

from balance_env import BalanceEnv


def main():
    # Output folders beside this script
    project_dir = Path(__file__).resolve().parent

    log_dir = project_dir / "logs"
    model_dir = project_dir / "models"

    log_dir.mkdir(parents=True, exist_ok=True)
    model_dir.mkdir(parents=True, exist_ok=True)

    # Monitor records episode rewards and lengths
    env = Monitor(
        BalanceEnv(),
        filename=str(log_dir / "sac_balance"),
    )

    try:
        model = SAC(
            policy="MlpPolicy",
            env=env,

            # Optimization
            learning_rate=3e-4,
            batch_size=256,

            # Experience replay
            buffer_size=100_000,
            learning_starts=1_000,

            # Update schedule
            train_freq=1,
            gradient_steps=1,

            # Discount and target-network update
            gamma=0.99,
            tau=0.005,

            # Automatic entropy coefficient
            ent_coef="auto",

            # Two hidden layers for this initial experiment
            policy_kwargs=dict(net_arch=[64, 64]),

            seed=42,
            verbose=1,
            device="cpu",
        )

        print("Starting SAC training...")

        model.learn(
            total_timesteps=100_000,
            log_interval=20,
        )

        model_path = model_dir / "sac_balance_100k"

        model.save(str(model_path))

        print("Training completed.")
        print(f"Model saved to: {model_path}.zip")

    finally:
        env.close()


if __name__ == "__main__":
    main()
