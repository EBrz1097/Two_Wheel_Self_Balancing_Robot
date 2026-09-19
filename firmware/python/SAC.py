import numpy as np
import matplotlib.pyplot as plt

# Discrete-time model
Ts = 0.01

Ad = np.array([
    [1.0164, 0.0101],
    [3.2879, 1.0164]
], dtype=np.float64)

Bd = np.array([
    [-0.0017],
    [-0.3351]
], dtype=np.float64)

K = np.array([[-28.4811, -3.6417]], dtype=np.float64)

# Hardware-equivalent input limits: PWM = 40 * u
u_max = 1000.0 / 40.0

# Illustrative test: initial tilt of 5 degrees, zero angular velocity
duration = 5.0
n_steps = int(round(duration / Ts))

states = np.zeros((n_steps + 1, 2))
actions = np.zeros(n_steps)

states[0] = [np.deg2rad(5.0), 0.0]

for k in range(n_steps):
    x = states[k]

    # LQR: u = -Kx
    u_raw = -(K @ x).item()
    u = np.clip(u_raw, -u_max, u_max)

    # No additional factor of 40 in the model
    states[k + 1] = Ad @ x + Bd[:, 0] * u
    actions[k] = u

time = np.arange(n_steps + 1) * Ts
pwm = 40.0 * actions

# Linear closed-loop stability check (without saturation)
eigenvalues = np.linalg.eigvals(Ad - Bd @ K)

print("Closed-loop eigenvalues:", eigenvalues)
print("Locally stable:", bool(np.all(np.abs(eigenvalues) < 1.0)))
print(f"Peak absolute PWM: {np.max(np.abs(pwm)):.3f}")
print(f"Final angle: {np.rad2deg(states[-1, 0]):.6f} deg")

fig, axes = plt.subplots(3, 1, figsize=(9, 8), sharex=True)

axes[0].plot(time, np.rad2deg(states[:, 0]))
axes[0].set_ylabel("Angle (deg)")

axes[1].plot(time, states[:, 1])
axes[1].set_ylabel("Angular velocity (rad/s)")

axes[2].step(time[:-1], pwm, where="post")
axes[2].set_ylabel("PWM")
axes[2].set_xlabel("Time (s)")

for ax in axes:
    ax.grid(True)

plt.tight_layout()
plt.show()
