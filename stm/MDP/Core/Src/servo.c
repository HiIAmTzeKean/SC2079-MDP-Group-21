#include "servo.h"

static TIM_HandleTypeDef *pwm_tim;

#define SERVO_LOOKUP_SIZE 38
static float anglePWMTable[38][2] = {
	{-36, 3400},
	{-32, 3410},
	{-29, 3420},
	{-26, 3500},
	{-24, 3600},
	{-22, 3750},
	{-20, 3800},
	{-18, 3900},
	{-14, 4000},
	{-13, 4100},
	{-10, 4200},
	{-7, 4300},
	{-6, 4400},
	{-4, 4500},
	{-2, 4600},
	{-1, 4700},
	{0, 4800},
	{1, 4900},
	{1.5, 5000},
	{3, 5100},
	{4.5, 5200},
	{7, 5300},
	{8.5, 5400},
	{10, 5500},
	{12, 5600},
	{13, 5700},
	{14, 5800},
	{15, 5900},
	{16, 6000},
	{17, 6100},
	{20, 6200},
	{21, 6300},
	{22, 6400},
	{23, 6500},
	{24, 6600},
	{25, 6700},
	//{25, 7000}, //Tryna see if same angle
	{25.5, 6700},
	//{25.5, 7050},
	//original{26, 6800}
	{36, 7350}
	//{26, 7100}
};

void servo_init(TIM_HandleTypeDef *pwm) {
	pwm_tim = pwm;
	HAL_TIM_PWM_Start(pwm, SERVO_PWM_CHANNEL);
}

void servo_setVal(uint32_t val) {
	pwm_tim->Instance->CCR1 = val;
}

void servo_setAngle(float angle) {
	//clamp angle to within width.
	if (angle < -SERVO_WIDTH) angle = -SERVO_WIDTH;
	else if (angle > SERVO_WIDTH) angle = SERVO_WIDTH;

	uint32_t val = 0;
	if (angle <= anglePWMTable[0][0]) val = anglePWMTable[0][0];
	else if (angle >= anglePWMTable[SERVO_LOOKUP_SIZE - 1][0]) val = anglePWMTable[SERVO_LOOKUP_SIZE - 1][0];
	else {
		uint8_t i;
		float min_val, max_val;
		float min_angle, max_angle;
		for (i = 0; i < SERVO_LOOKUP_SIZE - 1; i++) {
			min_angle = anglePWMTable[i][0];
			max_angle = anglePWMTable[i+1][0];
			min_val = anglePWMTable[i][1];
			max_val = anglePWMTable[i+1][1];

			if (angle >= min_angle && angle <= max_angle) {
				val = min_val + (max_val - min_val) * (angle - min_angle) / (max_angle - min_angle);
				break;
			}
		}
	}

	if (val == 0) val = anglePWMTable[SERVO_LOOKUP_SIZE - 1][1];
	servo_setVal(val);
}
