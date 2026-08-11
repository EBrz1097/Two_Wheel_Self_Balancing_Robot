# Two-Wheel Self-Balancing Robot

A two-wheel self-balancing robot based on the STM32F103C8T6 microcontroller, MPU6050 IMU, and L298N motor driver.

The project focuses on sensor acquisition, real-time angle estimation, motor control, and stabilization of an inverted-pendulum system. The controller development started with a PID controller and later progressed to a reduced LQR controller. The next planned phase is the design and implementation of an MPC controller.

---

## Project Overview

A self-balancing robot is an unstable inverted pendulum. Without active control, the robot naturally falls away from its upright position. The controller must continuously:

1. Measure the robot's orientation.
2. Estimate its angular velocity.
3. Calculate a corrective motor command.
4. Drive the motors in the appropriate direction.
5. Repeat this process at a fixed and sufficiently high frequency.

The current control loop operates with the following timing:
~~~text
Control-loop period: 0.01 s
Control-loop frequency: 100 Hz
~~~

The robot is currently tested while being held by hand on a smooth wooden surface.

---

## Main Features

- STM32F103C8T6-based control system
- MPU6050-based attitude sensing
- Gyroscope bias calibration
- Accelerometer and gyroscope sensor fusion
- Complementary filter for angle estimation
- Timer-based periodic sensor reading
- Timer-based control-loop execution
- PWM-based DC motor control
- Forward and reverse motor direction control
- Initial PID controller implementation
- LQR controller design in MATLAB
- Reduced LQR implementation without wheel encoders
- Planned MPC controller implementation

---

## Hardware

### Main Components

| Component | Description |
|---|---|
| Microcontroller | STM32F103C8T6 |
| IMU | MPU6050 |
| Motor driver | L298N |
| Motors | 6 V brushed DC motors |
| Encoders | Not available |
| Wheels | Approximately 50 mm diameter |
| Wheel spacing | Approximately 200 mm |
| Battery | Two 3.7 V Li-ion cells connected in series |
| Battery voltage | Approximately 7.4 V nominal |

The motors are simple brushed DC motors without position or velocity encoders. Therefore, the current system does not directly measure wheel position or wheel velocity.

---

## Hardware Connections

### MPU6050

The MPU6050 communicates with the STM32 through I2C.

| MPU6050 Signal | STM32 Pin |
|---|---|
| SCL | PB6 |
| SDA | PB7 |

### Motor Driver

The L298N is controlled using PWM and GPIO direction signals.

| Function | STM32 Pin |
|---|---|
| PWM outputs | PA6, PA7 |
| Motor direction signals | PA0 to PA3 |

The exact mapping between each direction pin and motor terminal is defined in the motor-control implementation.

---

## Timers

Two timers are used in the current implementation:

| Timer | Function |
|---|---|
| TIM4 | Periodic sensor sampling and controller execution |
| TIM3 | PWM generation for the motors |

TIM4 executes the sensor and controller loop every:

~~~text
dt = 0.01 s
~~~

This produces a control frequency of:

~~~text
f_control = 1 / dt = 100 Hz
~~~

A fixed control period is important because the controller calculations depend on a known sampling interval.

---

## Software Environment

The project is developed using:

- STM32CubeMX for peripheral configuration
- Keil MDK for compilation and programming
- STM32 HAL drivers
- Embedded C

The current application logic, including the controller, is implemented directly in:

~~~text
main.c
~~~

There is currently no separate `controller.c` module.

The project is based on the standard STM32CubeMX structure:

~~~text
two-wheel-self-balancing-robot/
├── Core/
│   ├── Inc/
│   └── Src/
│       └── main.c
├── Drivers/
├── .ioc
└── README.md
~~~

The exact directory structure may vary depending on the Keil and STM32CubeMX project configuration.

---

## Development Phases

### Phase 1: MPU6050 Communication

The first phase involved establishing communication between the STM32F103C8T6 and the MPU6050 using I2C.

The main tasks were:

- Initializing the I2C peripheral
- Configuring the MPU6050
- Reading accelerometer measurements
- Reading gyroscope measurements
- Checking communication with the sensor
- Converting raw sensor values into physical units

The I2C pins used in this project are:

~~~text
PB6: I2C clock
PB7: I2C data
~~~

---

### Phase 2: Gyroscope Calibration

The gyroscope has a static bias even when the robot is not rotating. This bias must be estimated and removed before using angular velocity in the controller.

At startup, the robot remains stationary while approximately 1000 gyroscope samples are collected.

The bias is calculated as:

~~~text
gyro_bias = average of stationary gyro measurements
~~~

The corrected measurement is then:

~~~text
gyro_corrected = gyro_raw - gyro_bias
~~~

The robot must remain still during the calibration process.

---

### Phase 3: Angle Estimation

The MPU6050 provides two useful sources of orientation information:

- The accelerometer estimates the angle relative to gravity.
- The gyroscope measures angular velocity and provides fast short-term motion information.

The project uses the gyroscope X-axis for the relevant angular-velocity measurement:

~~~text
Gx -> angular velocity used by the controller
~~~

The gyroscope measurement is initially available in degrees per second. It is converted to radians per second before being used in the mathematical controller:

c
omega_rad_s = gyro_deg_s * 0.017f;

The more accurate conversion constant is:

c
0.0174533f

The difference between `0.017f` and `0.0174533f` is small, but the more accurate constant is recommended for future versions.

---

### Phase 4: Complementary Filter

The gyroscope responds quickly to motion but suffers from integration drift. The accelerometer provides a long-term reference based on gravity but is sensitive to vibration and dynamic acceleration.

A complementary filter combines both measurements:

~~~text
angle_estimated =
alpha * angle_gyro
+ (1 - alpha) * angle_accelerometer
~~~

The current filter coefficient is:

~~~text
alpha = 0.9
~~~

The gyroscope-based angle is updated using:

~~~text
angle_gyro = angle_previous + gyro_rate * dt
~~~

The current filter can be represented as:

c
angle = 0.9f * (angle_previous + gyro_rad_s * dt)
+ 0.1f * accel_angle;

The complementary filter gives more weight to the gyroscope during short-term motion and uses the accelerometer to correct long-term drift.

---

### Phase 5: Timer-Based Real-Time Execution

The sensor reading and controller execution are triggered periodically using TIM4.

Every 0.01 seconds, the system performs the following sequence:

1. Read MPU6050 data.
2. Remove the gyroscope bias.
3. Convert sensor values into physical units.
4. Estimate the robot angle.
5. Calculate the angular velocity.
6. Execute the controller.
7. Generate the motor command.
8. Update the motor PWM and direction.

The same sensor sample is used by the controller during each control cycle.

The resulting control frequency is approximately:

~~~text
100 Hz
~~~

A periodic timer interrupt is used to maintain a consistent sampling period.

---

### Phase 6: Motor Driver

The motors are controlled through an L298N dual H-bridge driver.

The motor-control implementation includes:

- PWM speed control
- Forward direction control
- Reverse direction control
- Motor stop control
- Signed motor commands

The controller output is interpreted as a signed command:

~~~text
positive command: one motor direction
negative command: opposite motor direction
~~~

The signed command is converted into:

- A PWM duty cycle
- Direction GPIO states

The PWM signals are generated using TIM3.

Because the motors are not identical, their deadzones may differ. During testing, one motor was observed to have a smaller deadzone than the other.

---

## PID Controller

Before implementing LQR, the project used a PID-based controller for initial balancing experiments.

The PID gains were:

~~~text
Kp = 30
Ki = 5
Kd = 3
~~~

The general PID control law was:

\[ u(t) = K_p e(t) + K_i \int e(t)\,dt + K_d \frac{de(t)}{dt} \]

where:

- \(e(t)\) is the angle error
- \(K_p\) is the proportional gain
- \(K_i\) is the integral gain
- \(K_d\) is the derivative gain

The PID controller provided an initial practical baseline for testing:

- Sensor direction and sign conventions
- Motor direction
- Angle estimation
- PWM response
- Basic closed-loop behavior

The PID controller was later replaced by an LQR-based controller to use a state-space model and provide a more systematic control-design approach.

The PID phase remains useful as a reference point for evaluating the behavior of future controllers such as LQR and MPC.

Potential PID-specific considerations for future experiments include:

- Integral windup protection
- Derivative noise sensitivity
- Integral reset when the robot falls
- Output saturation
- Motor deadzone compensation
- Derivative filtering

---

## Mathematical Model

The robot can be approximated as an inverted pendulum mounted on a moving wheel base.

The approximate physical parameters used during modeling were:

~~~text
Total mass: approximately 1 kg
Distance from wheel axis to center of mass: approximately 0.1 m
Wheel diameter: approximately 0.05 m
~~~

The linearized continuous-time system was represented as:

matlab
A = [0 1 0 0;
0 0 -22.89 0;
0 0 0 1;
0 0 327.0 0];

B = [0;
3.333;
0;
-33.33];

The state vector is:

~~~text
x = [position, velocity, angle, angular_velocity]^T

Mathematically:

\[ x = \begin{bmatrix} x \\ \dot{x} \\ \theta \\ \dot{\theta} \end{bmatrix} \]

The continuous-time system model is:

\[ \dot{x} = Ax + Bu \]

where:

- \(x\) is the system state
- \(u\) is the control input
- \(A\) is the system matrix
- \(B\) is the input matrix
~~~
---

## LQR Controller Design

The LQR controller was designed in MATLAB using:

matlab
Q = diag([1 1 100 10]);
R = 1;

K = lqr(A, B, Q, R);

The resulting gain vector was:

~~~text
K = [-1.0000  -2.1923  -28.4811  -3.6417]

The standard LQR control law is:

\[ u = -Kx \]

Therefore:

\[ u = 1.0000x + 2.1923\dot{x} + 28.4811\theta + 3.6417\dot{\theta} \]

The full LQR controller requires four state variables:

- Wheel-base position
- Wheel-base velocity
- Robot angle
- Robot angular velocity

However, the current robot does not have wheel encoders. Consequently, position and velocity are not directly available.

The current implementation uses the angle-related terms:

\[ u_{\text{reduced}} = 28.4811\theta + 3.6417\dot{\theta} \]
~~~

The practical motor command is scaled using an experimental gain:

~~~text
Ku = 70
~~~

The current control structure is approximately:

~~~text
motor_command =
Ku * (28.4811 * theta_rad
+ 3.6417 * omega_rad_s)
~~~

The angle and angular velocity must be expressed in:

~~~text
theta_rad: radians
omega_rad_s: radians per second
~~~

---

## Current Experimental Behavior

The current controller demonstrates the expected basic balancing behavior:

- The robot reacts when it begins to fall.
- The motors move in the corrective direction.
- The robot can partially recover from small disturbances.
- The system can operate near the upright position during manual testing.

The robot is currently tested while being held by hand on a smooth wooden surface.

### Oscillation Around the Upright Position

The robot oscillates around the upright angle and does not settle accurately at the equilibrium point.

The observed oscillation amplitude is approximately:

~~~text
±3 degrees
~~~
Possible causes include:

- Insufficient damping from the angular-velocity term
- Sensor and computation delay
- Motor deadzone
- Unequal motor response
- Mechanical backlash
- Incorrect angle offset
- Quantization or noise in the measured angle
- Imperfect model parameters
- Discrete-time effects

The equilibrium angle is not exactly zero in the current mechanical setup. This may be caused by:

- MPU6050 mounting orientation
- Mechanical imbalance
- Chassis geometry
- Sensor calibration
- The selected reference position

A future implementation should use an equilibrium-angle offset:

~~~text
theta_error = theta_measured - theta_equilibrium
~~~

rather than assuming that the upright position is exactly zero degrees.

---

### Slow Reaction to Falling

The robot reacts to falling, but the response feels slower than desired.

The angular velocity is currently converted to radians per second without an additional low-pass filter. This decision was made because filtering the gyroscope signal noticeably reduced the response speed of the controller.

A low-pass filter on angular velocity can introduce phase lag. In a balancing robot, this is important because angular velocity provides early information about the direction and speed of falling.

The following sequence can occur when excessive filtering or delay is present:

1. The robot begins to rotate away from the upright position.
2. The raw gyroscope detects the motion immediately.
3. The filtered measurement changes more slowly.
4. The controller receives delayed angular-velocity information.
5. The corrective motor command is delayed.
6. The robot overshoots or feels weak during recovery.

The conversion from degrees per second to radians per second does not introduce delay. Multiplying by `0.017f` instead of `0.0174533f` produces only a small scaling error.

The more likely sources of delay are:

- Sensor filtering
- Complementary-filter behavior
- I2C reading time
- Interrupt scheduling
- Motor-driver response
- Mechanical inertia
- PWM update timing

---

### Weak Corrective Torque

The robot feels relatively soft or weak when trying to recover.

Possible causes include:

- Insufficient value of `Ku`
- Motor deadzone
- Unequal motor characteristics
- L298N voltage drop
- Battery voltage sag
- Insufficient motor torque
- Ineffective low-duty PWM
- Incorrect motor direction mapping
- Incorrect scaling between the mathematical control input and PWM
- Model parameters that do not match the real robot

The L298N has a relatively high voltage drop compared with modern MOSFET-based motor drivers. This can reduce the effective voltage and torque available to the motors.

The value `Ku = 70` maps the model-based controller output to the motor command. This scaling factor is experimental and is not directly determined by the LQR calculation.

---

### Motor Asymmetry

One motor has a smaller deadzone than the other.

The same PWM command may therefore produce different wheel responses. This can cause:

- Turning during a forward or backward correction
- Different behavior in the two falling directions
- Unequal balancing torque
- Additional oscillation
- A nonzero steady-state angle

Future versions may use separate motor calibration parameters:

~~~text
left_motor_command  = scale_left  * command + offset_left
right_motor_command = scale_right * command + offset_right
~~~

A minimum effective PWM value may also be required to overcome each motor's deadzone.

---

## Important Limitation: No Wheel Encoders

The theoretical LQR model contains four states:

~~~text
position
velocity
angle
angular velocity
~~~

The current hardware only measures orientation-related quantities:

~~~text
angle
angular velocity
~~~

Without wheel encoders:

- Wheel position is not measured.
- Wheel velocity is not measured directly.
- Full-state LQR cannot be implemented as originally designed.
- The current controller is a reduced angle-based controller.
- Long-term position drift cannot be actively regulated.

The robot may balance temporarily while slowly moving forward or backward. This behavior is expected when the position and velocity states are unavailable.

Adding wheel encoders would make it possible to estimate wheel velocity and position and implement the complete four-state controller.

---

## Current System Parameters

| Parameter | Value |
|---|---:|
| Control period | 0.01 s |
| Control frequency | 100 Hz |
| Complementary filter coefficient | 0.9 |
| Gyroscope calibration samples | 1000 |
| Motor voltage | 6 V |
| Battery configuration | 2 x 3.7 V Li-ion in series |
| Wheel diameter | approximately 50 mm |
| Wheel spacing | approximately 200 mm |
| Total modeled mass | approximately 1 kg |
| Center-of-mass distance | approximately 0.1 m |
| PID proportional gain | 30 |
| PID integral gain | 5 |
| PID derivative gain | 3 |
| LQR scaling gain | 70 |
| Wheel encoders | Not installed |
| Controller implementation | `main.c` |

---

## Safety Considerations

The robot is an unstable mechanical system and can accelerate unexpectedly.

Recommended safety mechanisms include:

- Stop the motors when the angle exceeds a defined limit.
- Stop the motors if MPU6050 communication fails.
- Stop the motors if the control loop stops executing.
- Start the motors with zero command.
- Keep the robot physically constrained during initial tests.
- Test with a current-limited power supply when possible.
- Avoid placing fingers near the wheels.
- Verify motor direction before enabling closed-loop control.
- Check that the battery and motor driver are suitable for the motor current.

A fall-detection condition should disable the motors when the robot leaves the controllable angle range.

---

## Planned Phase: Model Predictive Control

The next control phase will investigate Model Predictive Control (MPC).

MPC repeatedly performs the following process:

1. Measure or estimate the current system state.
2. Predict future system behavior using a mathematical model.
3. Optimize a sequence of future control inputs.
4. Apply only the first control input.
5. Repeat the process at the next sampling instant.

MPC can explicitly handle:

- Motor command limits
- Angle constraints
- Rate-of-change limits
- PWM saturation
- Trade-offs between fast recovery and low oscillation
- Discrete-time system behavior

A future MPC implementation should begin with a discrete-time model:

\[ x_{k+1} = A_d x_k + B_d u_k \]

where \(A_d\) and \(B_d\) are obtained from the continuous-time model using:

~~~text
dt = 0.01 s
~~~

The first MPC version may use the same reduced state vector as the current controller:

~~~text
x = [theta, omega]^T
~~~

A more complete MPC implementation should use wheel encoders and the full state vector:

~~~text
x = [position, velocity, theta, omega]^T
~~~

The lack of encoders is therefore an important limitation for the first MPC version as well.

---

## Recommended MPC Development Steps

### Step 1: Validate the Current Model

Before implementing MPC, compare the model response with measured robot behavior.

The following parameters should be reviewed:

- Total robot mass
- Center-of-mass height
- Wheel radius
- Motor torque constant
- Motor resistance
- Gear ratio
- Motor driver voltage drop
- Battery voltage under load
- Effective motor deadzone
- Sampling period
- Sensor delay

---

### Step 2: Create a Discrete-Time Model

Using MATLAB:

matlab
Ts = 0.01;

sys_c = ss(A, B, eye(size(A)), zeros(size(B)));
sys_d = c2d(sys_c, Ts);

Ad = sys_d.A;
Bd = sys_d.B;

The resulting discrete-time model will be used for prediction.

---

### Step 3: Define the MPC Cost Function

A typical quadratic MPC cost function is:

\[ J = \sum_{i=1}^{N} \left( x_i^T Q x_i + u_i^T R u_i \right) \]

where:

- \(N\) is the prediction horizon
- \(Q\) penalizes state errors
- \(R\) penalizes control effort

The upright angle should receive a relatively high weight because maintaining balance is the primary objective.

---

### Step 4: Add Constraints

Possible constraints include:

~~~text
-u_max <= u <= u_max
-theta_min <= theta <= theta_max
-delta_u_min <= delta_u <= delta_u_max
~~~

These constraints are important because the motors and driver cannot generate unlimited torque.

---

### Step 5: Select an Embedded Implementation Strategy

The STM32F103C8T6 has limited computational resources compared with a desktop computer. Candidate implementation strategies include:

- Explicit MPC
- Small-horizon quadratic programming
- Precomputed control lookup tables
- Reduced-order MPC
- Offline optimization with an embedded control law
- Simplified constrained predictive control

The first MPC experiments can be performed in MATLAB or Simulink before porting the algorithm to the STM32.

---

## Future Improvements

Potential improvements include:

- Install wheel encoders.
- Implement full-state feedback.
- Add a state observer or Kalman filter.
- Calibrate the equilibrium angle.
- Calibrate individual motor deadzones.
- Compensate for unequal motor gains.
- Replace the L298N with a lower-loss motor driver.
- Improve battery-voltage monitoring.
- Measure actual motor current.
- Log angle, angular velocity, PWM command, and loop timing.
- Evaluate sensor and control delay.
- Use the accurate `deg/s` to `rad/s` conversion constant.
- Validate the model experimentally.
- Implement discrete-time LQR.
- Implement constrained MPC.
- Separate the controller into a dedicated software module.

---

## Project Status

### Completed

- STM32F103C8T6 project setup
- MPU6050 I2C communication
- Accelerometer and gyroscope data acquisition
- Gyroscope bias calibration using approximately 1000 samples
- Complementary filter implementation
- Timer-based execution at 100 Hz
- PWM motor control using TIM3
- Motor direction control
- Initial PID controller implementation
- Initial inverted-pendulum modeling
- LQR gain calculation in MATLAB
- Initial reduced LQR-based balancing experiment

### Current Status

The robot can react to falling and shows basic balancing behavior. However:

- It oscillates around the upright angle.
- It reacts more slowly than desired.
- The corrective torque feels weak.
- The two motors have different deadzones.
- The equilibrium angle has an offset.
- Wheel position and velocity are not measured.

### Next Milestone

Design and implement an MPC controller, beginning with a validated discrete-time model and a reduced angle-based state representation.

---

## LQR MATLAB Script

The following MATLAB script was used to calculate the LQR gain:

matlab
A = [0 1 0 0;
0 0 -22.89 0;
0 0 0 1;
0 0 327.0 0];

B = [0;
3.333;
0;
-33.33];

Q = diag([1 1 100 10]);
R = 1;

K = lqr(A, B, Q, R);

Acl = A - B*K;
closed_loop_poles = eig(Acl);

disp('LQR gain K:')
disp(K)

disp('Closed-loop poles:')
disp(closed_loop_poles)

The calculated gain was:

~~~text
K = [-1.0000  -2.1923  -28.4811  -3.6417]
~~~

---

## License

This project is intended for educational and experimental use.

A license can be added later depending on whether the project will be published, shared, or developed as an open-source project.
