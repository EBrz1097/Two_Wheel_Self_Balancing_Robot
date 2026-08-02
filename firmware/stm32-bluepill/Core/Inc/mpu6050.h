
#ifndef MPU6050_H
#define MPU6050_H


#include "stm32f1xx_hal.h"
#include "stdint.h"


#define MPU6050_ADDR 		(0x68 << 1)

#define MPU6050_REG_WHO_AM_I				0x75
#define MPU6050_REG_PWR_MGMT_1			0x6B
#define MPU6050_REG_ACCEL_XOUT_H		0x3B
#define MPU6050_REG_GYRO_XOUT_H			0x43
#define MPU6050_REG_DLPF						0x1A
#define MPU6050_REG_ACCEL_CONFIG		0x1C
#define MPU6050_REG_GYRO_CONFIG			0x1B

typedef struct
{
	int16_t Accel_X_Raw;
	int16_t Accel_Y_Raw;
	int16_t Accel_Z_Raw;
	
	int16_t Gyro_X_Raw;
	int16_t Gyro_Y_Raw;
	int16_t Gyro_Z_Raw;
	
	float Ax;
	float Ay;
	float Az;
	
	float Gx;
	float Gy;
	float Gz;
	
	float pitch_acc;
	float pitch;
	
	float Gx_offset;
	float pitch_offset;
}MPU6050_t;


uint8_t MPU6050_Init(I2C_HandleTypeDef *I2Cx);
void MPU6050_Read_Accel(I2C_HandleTypeDef *I2Cx, MPU6050_t *dataStruct);
void MPU6050_Read_Gyro(I2C_HandleTypeDef *I2Cx, MPU6050_t *dataStruct);
void MPU6050_Read_All(I2C_HandleTypeDef *I2Cx, MPU6050_t *dataStruct);
void MPU6050_ComputePitch(I2C_HandleTypeDef *I2Cx, MPU6050_t *dataStruct, float dt);
void MPU6050_Calibrate_Gyro(I2C_HandleTypeDef *I2Cx, MPU6050_t *dataStruct);
void MPU6050_Calculate_PitchOffset(I2C_HandleTypeDef *I2Cx, MPU6050_t *dataStruct);

#endif