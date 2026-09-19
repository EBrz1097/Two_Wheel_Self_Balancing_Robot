from stable_baselines3.common.env_checker import check_env

from balance_env import BalanceEnv


env = BalanceEnv()

try:
    check_env(env, warn=True)
    print("Environment check completed successfully.")
finally:
    env.close()
