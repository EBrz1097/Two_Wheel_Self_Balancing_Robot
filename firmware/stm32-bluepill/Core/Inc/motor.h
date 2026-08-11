
#ifndef MOTOR_H
#define MOTOR_H

#include "stm32f1xx_hal.h"
#include "stdint.h"

#define MOTOR_PWM_MAX_AMP					999
#define LEFT_FORWARD_DEAD					385
#define LEFT_BACKWARD_DEAD			  380
#define RIGHT_FORWARD_DEAD				375
#define RIGHT_BACKWARD_DEAD			 	375

#define MOTOR_RAMP_STEP						20

void Motor_Init(void);
static int16_t Motor_Clamp(int16_t min, int16_t max, int16_t val);
void Motor_SetLeft(int16_t pwm);
void Motor_SetRight(int16_t pwm);
void Motor_StopAll(void);
static int16_t Apply_Ramp(int16_t current, int16_t step, int16_t val);
static int16_t Map_PWM_with_DeadZone(int16_t pwm, int16_t dead_fwd, int16_t dead_bwd);

#endif