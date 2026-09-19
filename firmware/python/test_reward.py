import numpy as np
from balance_env import BalanceEnv

env = BalanceEnv()

observation, info = env.reset()

print("Initial observation:", observation)

# Test one step with zero action
action = np.array([0.0], dtype=np.float32)

observation, reward, terminated, truncated, info = env.step(action)

print("Next observation:", observation)
print("Reward:", reward)
print("Terminated:", terminated)
print("Truncated:", truncated)

env.close()
