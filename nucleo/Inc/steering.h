#ifndef _STERRING_H_
#define _STERRING_H_

#include "stm32f1xx_hal.h"
#include "stm32f1xx_hal_gpio.h"
#include "stdint.h"

void STEE_setCanMess(uint8_t* data);
/**
* Set the speed of the steering motor. Speed value has to be between 0 and 100
**/
void steering_set_speed(GPIO_PinState en_steering, int speed);

/**
* Return the steering angle.
**/
int get_steering_angle(void);

/**
* Command the front wheel position
**/
void position_cmd (GPIO_PinState en_steering, int msg_CAN);
/**
* Init the steering wheel to know the changing value
**/
void init_steering(void);

#endif
