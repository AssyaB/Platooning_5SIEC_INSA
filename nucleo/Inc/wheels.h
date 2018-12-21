#ifndef _WHEELS_H_
#define _WHEELS_H_

#include "stm32f1xx_hal.h"
#include "stm32f1xx_hal_gpio.h"

/**
* Set the speed of the left and right rear motors. Speed values have to be between 0 and 100
**/
void wheels_set_speed(GPIO_PinState en_right, GPIO_PinState en_left, int speed_right, int speed_left);

#endif
