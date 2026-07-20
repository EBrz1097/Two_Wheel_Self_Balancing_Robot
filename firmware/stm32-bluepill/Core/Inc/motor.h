
#ifndef MOTOR_H
#define MOTOR_H

#include "stm32f1xx_hal.h"
#include "stdint.h"

#define MOTOR_PWM_MAX_AMP		999



void Motor_Init(void);
static int16_t Motor_Clamp(int16_t min, int16_t max, int16_t val);
void Motor_SetLeft(int16_t pwm);
void Motor_SetRight(int16_t pwm);
void Motor_StopAll(void);


#endif