from pathlib import Path

import numpy as np
import torch
from stable_baselines3 import SAC


MODEL_PATH = Path("models/sac_balance_100k.zip")
OUTPUT_DIR = Path("exported_actor")


def to_numpy(tensor):
    return tensor.detach().cpu().numpy().astype(np.float32)


def main():
    model = SAC.load(str(MODEL_PATH), device="cpu")
    actor = model.policy.actor
    actor.eval()

    # Verify the architecture before extracting its parameters.
    assert model.observation_space.shape == (2,)
    assert model.action_space.shape == (1,)
    assert not actor.use_sde

    assert len(actor.latent_pi) == 4
    assert isinstance(actor.latent_pi[0], torch.nn.Linear)
    assert isinstance(actor.latent_pi[1], torch.nn.ReLU)
    assert isinstance(actor.latent_pi[2], torch.nn.Linear)
    assert isinstance(actor.latent_pi[3], torch.nn.ReLU)

    W1 = to_numpy(actor.latent_pi[0].weight)
    b1 = to_numpy(actor.latent_pi[0].bias)

    W2 = to_numpy(actor.latent_pi[2].weight)
    b2 = to_numpy(actor.latent_pi[2].bias)

    W3 = to_numpy(actor.mu.weight)
    b3 = to_numpy(actor.mu.bias)

    assert W1.shape == (64, 2)
    assert b1.shape == (64,)
    assert W2.shape == (64, 64)
    assert b2.shape == (64,)
    assert W3.shape == (1, 64)
    assert b3.shape == (1,)

    action_low = np.asarray(
        model.action_space.low, dtype=np.float32
    )
    action_high = np.asarray(
        model.action_space.high, dtype=np.float32
    )

    assert np.all(action_low == -25.0)
    assert np.all(action_high == 25.0)

    def predict_numpy(observations):
        x = np.asarray(observations, dtype=np.float32)

        h1 = np.maximum(x @ W1.T + b1, np.float32(0.0))
        h2 = np.maximum(h1 @ W2.T + b2, np.float32(0.0))

        mean = h2 @ W3.T + b3
        normalized_action = np.tanh(mean)

        # Match Stable-Baselines3 action scaling.
        return action_low + (
            np.float32(0.5)
            * (normalized_action + np.float32(1.0))
            * (action_high - action_low)
        )

    # Numerical test inputs, not a robot stability test.
    rng = np.random.default_rng(42)

    random_observations = rng.uniform(
        low=[-0.2, -0.3],
        high=[0.2, 0.3],
        size=(1000, 2),
    ).astype(np.float32)

    observations = np.vstack([
        np.zeros((1, 2), dtype=np.float32),
        random_observations,
    ])

    sb3_actions, _ = model.predict(
        observations,
        deterministic=True,
    )

    numpy_actions = predict_numpy(observations)

    errors = np.abs(sb3_actions - numpy_actions)
    max_error = float(np.max(errors))

    print("\n--- Extracted parameter shapes ---")
    for name, array in [
        ("W1", W1), ("b1", b1),
        ("W2", W2), ("b2", b2),
        ("W3", W3), ("b3", b3),
    ]:
        print(f"{name}: {array.shape}")

    print("\n--- Zero observation ---")
    print("SB3 action  :", sb3_actions[0])
    print("NumPy action:", numpy_actions[0])

    print("\n--- Numerical comparison ---")
    print("Number of observations:", len(observations))
    print(f"Maximum absolute error: {max_error:.9g}")

    passed = bool(
        np.all(np.isfinite(numpy_actions))
        and np.all(np.isfinite(sb3_actions))
        and max_error <= 1e-4
    )

    print("Verification:", "PASS" if passed else "FAIL")

    if not passed:
        raise RuntimeError(
            "Verification failed. Do not proceed to C export."
        )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    weights_path = OUTPUT_DIR / "actor_weights.npz"
    np.savez(
        weights_path,
        W1=W1, b1=b1,
        W2=W2, b2=b2,
        W3=W3, b3=b3,
        action_low=action_low,
        action_high=action_high,
    )

    reference_path = OUTPUT_DIR / "actor_reference.csv"
    reference_data = np.column_stack([
        observations,
        sb3_actions.reshape(-1),
        numpy_actions.reshape(-1),
    ])

    np.savetxt(
        reference_path,
        reference_data,
        delimiter=",",
        header="obs0,obs1,action_sb3,action_numpy",
        comments="",
        fmt="%.9g",
    )

    print("\n--- Saved files ---")
    print(weights_path.resolve())
    print(reference_path.resolve())


if __name__ == "__main__":
    main()
