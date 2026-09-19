from pathlib import Path

import numpy as np
from stable_baselines3 import SAC


MODEL_PATH = Path("models/sac_balance_100k.zip")


def main():
    if not MODEL_PATH.is_file():
        raise FileNotFoundError(
            f"Model file not found: {MODEL_PATH.resolve()}"
        )

    # Load the trained model on the computer CPU.
    model = SAC.load(str(MODEL_PATH), device="cpu")
    actor = model.policy.actor
    actor.eval()

    print("\n--- Observation space ---")
    print(model.observation_space)

    print("\n--- Action space ---")
    print(model.action_space)
    print("Action low :", model.action_space.low)
    print("Action high:", model.action_space.high)

    print("\n--- Actor structure ---")
    print(actor)

    print("\n--- Actor configuration ---")
    print("use_sde:", actor.use_sde)

    print("\n--- Actor parameters ---")
    total_parameters = 0

    for name, parameter in actor.named_parameters():
        count = parameter.numel()
        total_parameters += count

        print(
            f"{name}: "
            f"shape={tuple(parameter.shape)}, "
            f"parameters={count}"
        )

    print("\n--- Parameter storage estimate ---")
    print("Total actor parameters:", total_parameters)
    print(
        "All actor parameters as float32: "
        f"{total_parameters * 4 / 1024:.2f} KiB"
    )

    # This checks inference only; it does not simulate the robot.
    # Zero has the same numerical value in degrees and radians.
    observation = np.zeros(
        model.observation_space.shape,
        dtype=np.float32,
    )

    action, _ = model.predict(
        observation,
        deterministic=True,
    )

    print("\n--- Deterministic prediction at zero observation ---")
    print("Observation:", observation)
    print("Predicted action:", action)


if __name__ == "__main__":
    main()
