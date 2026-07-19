
#include "mpu6050.h"
#include "math.h"

uint8_t MPU6050_Init(I2C_HandleTypeDef *I2Cx)
{
	uint8_t check, data;
	
	HAL_I2C_Mem_Read(I2Cx, MPU6050_ADDR, MPU6050_REG_WHO_AM_I, I2C_MEMADD_SIZE_8BIT, &check, sizeof(check), 1000);
	
	if(check == 0x70)
	{
		data = 0x00;
		HAL_I2C_Mem_Write(I2Cx, MPU6050_ADDR, MPU6050_REG_PWR_MGMT_1, I2C_MEMADD_SIZE_8BIT, &data, sizeof(data), 1000);
		HAL_Delay(10);
		
		data = 0x03;
		HAL_I2C_Mem_Write(I2Cx, MPU6050_ADDR, MPU6050_REG_DLPF, I2C_MEMADD_SIZE_8BIT, &data, sizeof(data), 1000);
		HAL_Delay(10);
		
		data = 0x00;
		HAL_I2C_Mem_Write(I2Cx, MPU6050_ADDR, MPU6050_REG_ACCEL_CONFIG, I2C_MEMADD_SIZE_8BIT, &data, sizeof(data), 1000);
		HAL_Delay(10);
		
		data = 0x00;
		HAL_I2C_Mem_Write(I2Cx, MPU6050_ADDR, MPU6050_REG_GYRO_CONFIG, I2C_MEMADD_SIZE_8BIT, &data, sizeof(data), 1000);
		HAL_Delay(10);
		
		return 1;
	}
	
	return 0;
}

void MPU6050_Read_Accel(I2C_HandleTypeDef *I2Cx, MPU6050_t *dataStruct)
{
	uint8_t Rec_data[6];
	
	HAL_I2C_Mem_Read(I2Cx, MPU6050_ADDR, MPU6050_REG_ACCEL_XOUT_H, I2C_MEMADD_SIZE_8BIT, Rec_data, (sizeof(Rec_data)/sizeof(Rec_data[0])), 1000);
	
	dataStruct->Accel_X_Raw = (int16_t)(Rec_data[0]<<8 | Rec_data[1]);
	dataStruct->Accel_Y_Raw = (int16_t)(Rec_data[2]<<8 | Rec_data[3]);
	dataStruct->Accel_Z_Raw = (int16_t)(Rec_data[4]<<8 | Rec_data[5]);
	
	dataStruct->Ax = dataStruct->Accel_X_Raw / 16384.0;
	dataStruct->Ay = dataStruct->Accel_Y_Raw / 16384.0;
	dataStruct->Az = dataStruct->Accel_Z_Raw / 16384.0;
}

void MPU6050_Read_Gyro(I2C_HandleTypeDef *I2Cx, MPU6050_t *dataStruct)
{
	uint8_t Rec_data[6];
	
	HAL_I2C_Mem_Read(I2Cx, MPU6050_ADDR, MPU6050_REG_GYRO_XOUT_H, I2C_MEMADD_SIZE_8BIT, Rec_data, (sizeof(Rec_data)/(sizeof(Rec_data[0]))), 1000);
	
	dataStruct->Gyro_X_Raw = (int16_t)(Rec_data[0]<<8 | Rec_data[1]);
	dataStruct->Gyro_Y_Raw = (int16_t)(Rec_data[2]<<8 | Rec_data[3]);
	dataStruct->Gyro_Z_Raw = (int16_t)(Rec_data[4]<<8 | Rec_data[5]);
	
	dataStruct->Gx = (dataStruct->Gyro_X_Raw / 131.0)-dataStruct->Gx_offset;
	dataStruct->Gy = dataStruct->Gyro_Y_Raw / 131.0;
	dataStruct->Gz = dataStruct->Gyro_Z_Raw / 131.0;
}

void MPU6050_Read_All(I2C_HandleTypeDef *I2Cx, MPU6050_t *dataStruct)
{
	MPU6050_Read_Accel(I2Cx, dataStruct);
	MPU6050_Read_Gyro(I2Cx, dataStruct);
}

void MPU6050_ComputePitch(I2C_HandleTypeDef *I2Cx, MPU6050_t *dataStruct, float dt)
{
	dataStruct->pitch_acc = atan2f(-dataStruct->Ay, sqrtf(dataStruct->Ax * dataStruct->Ax + dataStruct->Az * dataStruct->Az)) * 57.2958f;
	
	//Complementary Filter
	dataStruct->pitch = 0.90f * (dataStruct->pitch - dataStruct->Gx*dt) + 0.1f * dataStruct->pitch_acc;
}

void MPU6050_Calibrate_Gyro(I2C_HandleTypeDef *I2Cx, MPU6050_t *dataStruct)
{
	float Gx_Sum = 0;
	const int samples = 1000;
	
	for(int i=0;i<samples;i++)
	{
		MPU6050_Read_All(I2Cx, dataStruct);
		Gx_Sum += dataStruct->Gx;
		HAL_Delay(5);
	}
	dataStruct->Gx_offset = (Gx_Sum)/samples;
}