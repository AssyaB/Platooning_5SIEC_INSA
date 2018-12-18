#include "wheels.h"

#define MAX_SPEED_WHEEL 75
#define MIN_SPEED_WHEEL 25


void wheels_set_speed(GPIO_PinState en_right, GPIO_PinState en_left, int speed_right, int speed_left){
		// Moteur avant
		/* > 50 % droite, < 50 % gauche et 50 % arret        */	
		/*limitations  de preference 0.4 a 0.6 %             */	

		if (speed_left < MIN_SPEED_WHEEL){
			speed_left = MIN_SPEED_WHEEL;
		} else if (speed_left > MAX_SPEED_WHEEL){
			speed_left = MAX_SPEED_WHEEL;
		}
		if (speed_right < MIN_SPEED_WHEEL){
			speed_right = MIN_SPEED_WHEEL;
		} else if (speed_right > MAX_SPEED_WHEEL){
			speed_right = MAX_SPEED_WHEEL;
		}	
		
		speed_left = 3200 * ( speed_left/ 100.0 );
		speed_right = 3200 * ( speed_right/ 100.0 );
		
		TIM1->CCR1=speed_left;
		TIM1->CCR2=speed_right;
		
		/*        Enable moteurs        */
		/* GPIO_PIN_SET : activation    */
		/* GPIO_PIN_RESET : pont ouvert */
			
		HAL_GPIO_WritePin( GPIOC, GPIO_PIN_10, en_left); //PC10  AR_G
		HAL_GPIO_WritePin( GPIOC, GPIO_PIN_11, en_right); //PC11  AR_D
}
