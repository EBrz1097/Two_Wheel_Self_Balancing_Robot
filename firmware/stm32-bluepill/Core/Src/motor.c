
#include "motor.h"
#include "main.h"

extern TIM_HandleTypeDef htim3;

static int16_t Motor_Clamp(int16_t min, int16_t max, int16_t val)
{
	if(val<min) return min;
	if(val>max) return max;
	return val;
}

void Motor_Init(void)
{
	HAL_TIM_PWM_Start(&htim3, TIM_CHANNEL_1);
	HAL_TIM_PWM_Start(&htim3, TIM_CHANNEL_2);
	
	Motor_StopAll();
}

void Motor_SetLeft(int16_t pwm)
{
	Motor_Clamp(-MOTOR_PWM_MAX_AMP, MOTOR_PWM_MAX_AMP, pwm);
	
	if(pwm > 0)
	{
		HAL_GPIO_WritePin(IN1_GPIO_Port, IN1_Pin ,GPIO_PIN_SET);
		HAL_GPIO_WritePin(IN2_GPIO_Port, IN2_Pin, GPIO_PIN_RESET);
		__HAL_TIM_SET_COMPARE(&htim3, TIM_CHANNEL_1, pwm);
		
	}else if(pwm < 0)
	{
		HAL_GPIO_WritePin(IN1_GPIO_Port, IN1_Pin ,GPIO_PIN_RESET);
		HAL_GPIO_WritePin(IN2_GPIO_Port, IN2_Pin, GPIO_PIN_SET);
		__HAL_TIM_SET_COMPARE(&htim3, TIM_CHANNEL_1, -pwm);
		
	}else
	{
		HAL_GPIO_WritePin(IN1_GPIO_Port, IN1_Pin ,GPIO_PIN_RESET);
		HAL_GPIO_WritePin(IN2_GPIO_Port, IN2_Pin, GPIO_PIN_RESET);
		__HAL_TIM_SET_COMPARE(&htim3, TIM_CHANNEL_1, 0);
		
	}
	
}

void Motor_SetRight(int16_t pwm)
{
	Motor_Clamp(-MOTOR_PWM_MAX_AMP, MOTOR_PWM_MAX_AMP, pwm);
	
	if(pwm > 0)
	{
		HAL_GPIO_WritePin(IN1_GPIO_Port, IN3_Pin ,GPIO_PIN_RESET);
		HAL_GPIO_WritePin(IN2_GPIO_Port, IN4_Pin, GPIO_PIN_SET);
		__HAL_TIM_SET_COMPARE(&htim3, TIM_CHANNEL_2, pwm);
		
	}else if(pwm < 0)
	{
		HAL_GPIO_WritePin(IN1_GPIO_Port, IN3_Pin ,GPIO_PIN_SET);
		HAL_GPIO_WritePin(IN2_GPIO_Port, IN4_Pin, GPIO_PIN_RESET);
		__HAL_TIM_SET_COMPARE(&htim3, TIM_CHANNEL_2, -pwm);
		
	}else
	{
		HAL_GPIO_WritePin(IN1_GPIO_Port, IN1_Pin ,GPIO_PIN_RESET);
		HAL_GPIO_WritePin(IN2_GPIO_Port, IN2_Pin, GPIO_PIN_RESET);
		__HAL_TIM_SET_COMPARE(&htim3, TIM_CHANNEL_2, 0);
		
	}
}

void Motor_StopAll(void)
{
	Motor_SetLeft(0);
	Motor_SetRight(0);
}