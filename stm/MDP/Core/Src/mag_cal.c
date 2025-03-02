#include "mag_cal.h"
#include "motor.h"

static I2C_HandleTypeDef *hi2c;
static MagCalParams *params;

static void magcal_preload(MagCalParams *params_ptr) {
	//Previous Callibration for Hard
	params_ptr->offset_HI[0] = 12.3750;
	params_ptr->offset_HI[1] = -56.4750;

	//Our Callibration for Hard
	//params_ptr->offset_HI[0] = 9.4500;
	//params_ptr->offset_HI[1] = -2.7750;

	//Previous callibration for soft
	params_ptr->matrix_SI[0][0] = 0.8898;
	params_ptr->matrix_SI[0][1] = -0.5961;
	params_ptr->matrix_SI[1][0] = 0.8007;
	params_ptr->matrix_SI[1][1] = 1.1952;

	//Our callibration for soft
	//params_ptr->matrix_SI[0][0] = 1.6606;
	//params_ptr->matrix_SI[0][1] = 1.3085;
	//params_ptr->matrix_SI[0][1] = 0.0413;
	//params_ptr->matrix_SI[1][0] = -5.1538;
	//params_ptr->matrix_SI[1][0] = -0.1134;
	//params_ptr->matrix_SI[1][1] = 4.5604;
}

void magcal_init(I2C_HandleTypeDef *hi2c_ptr, MagCalParams *params_ptr) {
	//Initialise our magnometer
	hi2c = hi2c_ptr;
	params = params_ptr;

	magcal_preload(params_ptr);
}

//calibration sequence based on: https://www.atlantis-press.com/article/25847616.pdf
//This is to calculate our sequence to see if there was a misconfiguration for bias
void magcal_calc_params() {
	float magRange[2][2]; //minimum, maximum for each axis
	float mag[2];
	char buf[20];

	//load initial values.
	HAL_Delay(500);
	ICM20948_readMagnetometer_XY(hi2c, mag);
	magRange[0][0] = mag[0];
	magRange[0][1] = mag[0];
	magRange[1][0] = mag[1];
	magRange[1][1] = mag[1];

	//find minimum and maximum of X and Y axis.
	OLED_ShowString(0, 0, "Min/Max XY");
	uint16_t i = 0;
	while (1) {
		ICM20948_readMagnetometer_XY(hi2c, mag);
		snprintf(buf, 20, "%.3f|%.3f", mag[0], mag[1]);
		OLED_ShowString(0, 10, buf);

		for (i = 0; i < 2; i++) {
			if (mag[i] < magRange[i][0]) magRange[i][0] = mag[i];
			if (mag[i] > magRange[i][1]) magRange[i][1] = mag[i];

			snprintf(buf, 20, "%.3f|%.3f", magRange[i][0], magRange[i][1]);
			OLED_ShowString(0, 10 * (i + 2), buf);
		}

		OLED_Refresh_Gram();
		if (user_is_pressed())
		{
//			for (int x = 0; x < 5; x ++){
//				if(x == 0){
//					servo_setVal(6700);
//					HAL_GPIO_WritePin(MOTORA_IN1_GPIO_Port, MOTORA_IN1_Pin, GPIO_PIN_SET);
//					HAL_GPIO_WritePin(MOTORA_IN2_GPIO_Port, MOTORA_IN2_Pin, GPIO_PIN_RESET);
//					HAL_GPIO_WritePin(MOTORB_IN1_GPIO_Port, MOTORB_IN1_Pin, GPIO_PIN_SET);
//					HAL_GPIO_WritePin(MOTORB_IN2_GPIO_Port, MOTORB_IN2_Pin, GPIO_PIN_RESET);
//					setManualPwmLR(5000);
//					HAL_Delay(5000);
//					servo_setVal(4800);
//					setManualPwmLR(0);
//				}
//				else if (x == 1)
//				{
//					servo_setVal(6700);
//					HAL_GPIO_WritePin(MOTORA_IN1_GPIO_Port, MOTORA_IN1_Pin, GPIO_PIN_RESET);
//					HAL_GPIO_WritePin(MOTORA_IN2_GPIO_Port, MOTORA_IN2_Pin, GPIO_PIN_SET);
//					HAL_GPIO_WritePin(MOTORB_IN1_GPIO_Port, MOTORB_IN1_Pin, GPIO_PIN_RESET);
//					HAL_GPIO_WritePin(MOTORB_IN2_GPIO_Port, MOTORB_IN2_Pin, GPIO_PIN_SET);
//					setManualPwmLR(5000);
//					HAL_Delay(5000);
//					servo_setVal(4800);
//					setManualPwmLR(0);
//				}
//				else if (x == 2)
//				{
//
//					servo_setVal(3550);
//					HAL_GPIO_WritePin(MOTORA_IN1_GPIO_Port, MOTORA_IN1_Pin, GPIO_PIN_SET);
//					HAL_GPIO_WritePin(MOTORA_IN2_GPIO_Port, MOTORA_IN2_Pin, GPIO_PIN_RESET);
//					HAL_GPIO_WritePin(MOTORB_IN1_GPIO_Port, MOTORB_IN1_Pin, GPIO_PIN_SET);
//					HAL_GPIO_WritePin(MOTORB_IN2_GPIO_Port, MOTORB_IN2_Pin, GPIO_PIN_RESET);
//					setManualPwmLR(5000);
//					HAL_Delay(5000);
//					servo_setVal(4800);
//					setManualPwmLR(0);
//				}
//				else if (x == 3)
//				{
//					servo_setVal(3550);
//					HAL_GPIO_WritePin(MOTORA_IN1_GPIO_Port, MOTORA_IN1_Pin, GPIO_PIN_RESET);
//					HAL_GPIO_WritePin(MOTORA_IN2_GPIO_Port, MOTORA_IN2_Pin, GPIO_PIN_SET);
//					HAL_GPIO_WritePin(MOTORB_IN1_GPIO_Port, MOTORB_IN1_Pin, GPIO_PIN_RESET);
//					HAL_GPIO_WritePin(MOTORB_IN2_GPIO_Port, MOTORB_IN2_Pin, GPIO_PIN_SET);
//					setManualPwmLR(5000);
//					HAL_Delay(5000);
//					servo_setVal(4800);
//					setManualPwmLR(0);
//				}
//			}

			break;
		}
	}

	//hard iron offset (center of ellipse).
	params->offset_HI[0] = (magRange[0][1] + magRange[0][0]) / 2;
	params->offset_HI[1] = (magRange[1][1] + magRange[1][0]) / 2;

	//calculate step size (to get an even number of readings).
	float xStep = (magRange[0][1] - magRange[0][0]) / MAGCAL_POINTS;
	float yStep = (magRange[1][1] - magRange[1][0]) / MAGCAL_POINTS;

	//read ellipse points.
	i = 0;
	float magVals[2][MAGCAL_POINTS];

	OLED_Clear();
	OLED_ShowString(0, 0, "Tracing ellipse");
	snprintf(buf, 20, "%.3f|%.3f", xStep, yStep);
	OLED_ShowString(0, 20, buf);
	OLED_Refresh_Gram();

	//trace ellipse (and also get b).
	float b = -1, dist;
	while (i < MAGCAL_POINTS) {
		ICM20948_readMagnetometer_XY(hi2c, mag);
		if (i == 0 ||
				(abs_float(mag[0] - magVals[0][i-1]) > xStep
				&& abs_float(mag[1] - magVals[1][i-1]) > yStep)) {
			magVals[0][i] = mag[0];
			magVals[1][i] = mag[1];

			snprintf(buf, 40, "On %i of %i", i+1, MAGCAL_POINTS);
			OLED_ShowString(0, 10, buf);
			OLED_Refresh_Gram();
			i++;
		}

		dist = dist_squared(params->offset_HI[0], mag[0], params->offset_HI[1], mag[1]);
		if (b < 0 || dist < b) {
			b = dist;
		}
	}

	b = (float) sqrt((double) b);
	//find major axis points on ellipse.
	uint16_t j = 0;
	uint16_t a1, a2;
	float a = 0;
	for (i = 0; i < MAGCAL_POINTS - 1; i++) {
		for (j = i + 1; j < MAGCAL_POINTS; j++) {
			dist = dist_squared(magVals[0][i], magVals[0][j], magVals[1][j], magVals[1][j]);
			if (dist > a) {
				a = dist;
				a1 = i; a2 = j;
			}
		}
	}

	//calculate required parameters.
	a = (float) sqrt((double) a) / 2;

	//re-using mag as [k1, k2].
	mag[0] = abs_float(magVals[1][a1] - params->offset_HI[1]) / a;
	mag[1] = abs_float(magVals[0][a1] - params->offset_HI[0]) / a;

	//check if rotation should be clockwise or counter-clockwise (re-use i = clockwise).
	i = (magVals[0][a1] > params->offset_HI[0] && magVals[1][a1] > params->offset_HI[1])
			|| (magVals[0][a2] > params->offset_HI[0] && magVals[1][a2] > params->offset_HI[1]);

	//soft iron matrix.
	params->matrix_SI[0][0] = mag[1];
	params->matrix_SI[0][1] = mag[0];
	params->matrix_SI[1][0] = -(mag[0]) * a / b;
	params->matrix_SI[1][1] = mag[1] * a / b;
	if (!i) {
		//flip if counter-clockwise.
		params->matrix_SI[0][1] = -(params->matrix_SI[0][1]);
		params->matrix_SI[1][0] = -(params->matrix_SI[1][0]);
	}

	//User indication.
	OLED_Clear();
	OLED_ShowString(0, 0, "MagCal done");
	snprintf(buf, 20, "%.4f %.4f", params->offset_HI[0], params->offset_HI[1]);
	OLED_ShowString(0, 10, buf);
	snprintf(buf, 20, "%.4f %.4f", params->matrix_SI[0][0], params->matrix_SI[0][1]);
	OLED_ShowString(0, 20, buf);
	snprintf(buf, 20, "%.4f %.4f", params->matrix_SI[1][0], params->matrix_SI[1][1]);
	OLED_ShowString(0, 30, buf);
	OLED_Refresh_Gram();

	while(!user_is_pressed());

	OLED_Clear();
	OLED_Refresh_Gram();
}

void magcal_adjust(float magXY[2]) {
	//Adjust our magcal for bias
	float x = magXY[0] - params->offset_HI[0], y = magXY[1] - params->offset_HI[1];
	magXY[0] = params->matrix_SI[0][0] * x + params->matrix_SI[0][1] * y;
	magXY[1] = params->matrix_SI[1][0] * x + params->matrix_SI[1][1] * y;
}
