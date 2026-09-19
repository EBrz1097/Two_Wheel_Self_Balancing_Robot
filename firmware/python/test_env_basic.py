import numpy as np
from balance_env import BalanceEnv


env = BalanceEnv()

observation, info = env.reset(seed=42)

print("Initial observation:")
print(observation)

print("\nInitial info:")
print(info)

action = np.array([1.0], dtype=np.float32)

next_observation, reward, terminated, truncated, info = env.step(action)

print("\nAction:")
print(action)

print("\nNext observation:")
print(next_observation)

print("\nReward:")
print(reward)

print("\nTerminated:")
print(terminated)

print("\nTruncated:")
print(truncated)

print("\nInfo:")
print(info)

env.close()
