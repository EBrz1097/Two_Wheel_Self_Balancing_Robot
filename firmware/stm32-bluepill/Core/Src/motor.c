
#include "motor.h"
#include "main.h"

extern TIM_HandleTypeDef htim3;
static int16_t left_pwm_prev;
static int16_t right_pwm_prev;

static int16_t Motor_Clamp(int16_t min, int16_t max, int16_t val)
{
	if(val<min) return min;
	if(val>max) return max;
	return val;
}

static int16_t Apply_Ramp(int16_t current, int16_t step, int16_t val)
{
	if(val>current+step) return current+step;
	if(val<current-step) return current-step;
	return val;
}

static int16_t Map_PWM_with_DeadZone(int16_t pwm, int16_t dead_fwd, int16_t dead_bwd)
{
	if(pwm == 0) return 0;
	
	else if(pwm > 0)
	{
		int32_t PWM;
		PWM = dead_fwd + ((int32_t)(pwm-1)*(MOTOR_PWM_MAX_AMP-dead_fwd)/(MOTOR_PWM_MAX_AMP-1));
		return (int16_t)PWM;
	}else
	{
		int16_t  tmp = -pwm;
		int32_t PWM;
		PWM = dead_bwd + ((int32_t)(tmp-1)*(MOTOR_PWM_MAX_AMP-dead_bwd)/(MOTOR_PWM_MAX_AMP-1));
		return (int16_t)(-PWM);
	}
}

void Motor_Init(void)
{
	HAL_TIM_PWM_Start(&htim3, TIM_CHANNEL_1);
	HAL_TIM_PWM_Start(&htim3, TIM_CHANNEL_2);
	
	left_pwm_prev = 0;
	right_pwm_prev = 0;
	
	Motor_StopAll();
}

void Motor_SetLeft(int16_t pwm)
{
	Motor_Clamp(-MOTOR_PWM_MAX_AMP, MOTOR_PWM_MAX_AMP, pwm);
	
	Apply_Ramp(left_pwm_prev, MOTOR_RAMP_STEP, pwm);
	
	pwm = Map_PWM_with_DeadZone(pwm, LEFT_FORWARD_DEAD, LEFT_BACKWARD_DEAD);
	
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
	left_pwm_prev = pwm;
}

void Motor_SetRight(int16_t pwm)
{
	Motor_Clamp(-MOTOR_PWM_MAX_AMP, MOTOR_PWM_MAX_AMP, pwm);
	
	Apply_Ramp(right_pwm_prev, MOTOR_RAMP_STEP, pwm);
	
	pwm = Map_PWM_with_DeadZone(pwm, RIGHT_FORWARD_DEAD, RIGHT_BACKWARD_DEAD);
	
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
	right_pwm_prev = pwm;
}

void Motor_StopAll(void)
{
	Motor_SetLeft(0);
	Motor_SetRight(0);
}