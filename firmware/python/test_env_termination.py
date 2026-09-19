import numpy as np
from balance_env import BalanceEnv

env = BalanceEnv()
observation, info = env.reset()

# Apply zero input and let the unstable model move away from balance.
action = np.array([0.0], dtype=np.float32)

for step in range(1, 501):
    observation, reward, terminated, truncated, info = env.step(action)

    if terminated or truncated:
        print("Episode ended.")
        print("Steps:", step)
        print(f"Elapsed time: {step * env.Ts:.2f} s")
        print(f"Final angle: {np.rad2deg(observation[0]):.3f} deg")
        print("Terminated:", terminated)
        print("Truncated:", truncated)
        break

env.close()
