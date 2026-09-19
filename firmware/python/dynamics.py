import numpy as np

# Sampling time in seconds
Ts = 0.01

# Discrete-time model
Ad = np.array([
    [1.0164, 0.0101],
    [3.2879, 1.0164]
], dtype=np.float64)

Bd = np.array([
    [-0.0017],
    [-0.3351]
], dtype=np.float64)

def next_state(x, u):
    """
    Compute the state after one sampling interval.

    x: state vector with shape (2,)
       x[0]: angle in radians
       x[1]: angular velocity in rad/s

    u: scalar model input
       Hardware conversion: PWM = 40 * u
    """
    x = np.asarray(x, dtype=np.float64).reshape(2,)
    u = float(u)

    x_next = Ad @ x + Bd[:, 0] * u

    return x_next
