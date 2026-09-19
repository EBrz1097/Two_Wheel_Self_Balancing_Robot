import numpy as np
from dynamics import next_state

# Initial angle: 5 degrees
# Initial angular velocity: 0 rad/s
x = np.array([
    np.deg2rad(5.0),
    0.0
], dtype=np.float64)
               
u = 1.0   # equivalent to 40 PWM

# Advance the model by one sampling interval
x_next = next_state(x, u)

print("Current state [rad, rad/s]:")
print(x)

print("\nInput u:")
print(u)

print("\nNext state [rad, rad/s]:")
print(x_next)

print("\nCurrent angle in degrees:")
print(np.rad2deg(x[0]))

print("\nNext angle in degrees:")
print(np.rad2deg(x_next[0]))

print("\nEquivalent PWM:")
print(40.0 * u)
