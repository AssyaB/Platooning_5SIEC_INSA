#include "steering.h"
#include "stdlib.h"

#define SPEED1Min 37
#define SPEED1Max 63
#define SPEED2Min 42
#define SPEED2Max 58


//#define gauche_volant 0x98E // valeur initiale = 2395
//#define droite_volant 0x730 // valeur initiale = 1825
#define centre_volant (gauche_volant + droite_volant)/2 // valeur initiale = 2110

// CHOOSE YOUR CAR
// black 1 car

#define MAX_CMD_STEERING1 SPEED1Max // Left steering command
#define MIN_CMD_STEERING1 SPEED1Min // Right steering command
#define MAX_CMD_STEERING2 SPEED2Max // Left steering command
#define MIN_CMD_STEERING2 SPEED2Min // Right steering command
#define MEDIUM_CMD_STEERING (MAX_CMD_STEERING1 + MIN_CMD_STEERING1)/2

// pink car
/*
#define MAX_CMD_STEERING1 SPEED1Min // Left steering command
#define MIN_CMD_STEERING1 SPEED1Max // Right steering command
#define MAX_CMD_STEERING2 SPEED2Min // Left steering command
#define MIN_CMD_STEERING2 SPEED2Max // Right steering command
#define MEDIUM_CMD_STEERING (MAX_CMD_STEERING1 + MIN_CMD_STEERING1)/2
*/


extern uint32_t ADCBUF[5];

int gauche_volant, droite_volant, coeff_correction;
int applied_cmd;

void init_steering(void){
	steering_set_speed(GPIO_PIN_SET, MAX_CMD_STEERING1);
	HAL_Delay(3000);
	droite_volant = get_steering_angle();
	steering_set_speed(GPIO_PIN_SET, MIN_CMD_STEERING1);
	HAL_Delay(3000);
	gauche_volant = get_steering_angle();
	coeff_correction = (gauche_volant - droite_volant) / 100;
	for(int i = 0; i < 50000; i ++)
		position_cmd(GPIO_PIN_SET, 50);
	steering_set_speed(GPIO_PIN_SET, MEDIUM_CMD_STEERING);
}

void steering_set_speed(GPIO_PinState en_steering, int speed){

		/* Threshold */
		/* The speed */
		if (speed < SPEED1Min){
			speed = SPEED1Min;
		} else if (speed > SPEED1Max){
			speed  = SPEED1Max;
		}
		applied_cmd = speed;
		speed = 3200 * ( speed/ 100.0 );

		TIM1->CCR3 = speed;

		/*        Enable moteurs        */
		/* GPIO_PIN_SET : activation    */
		/* GPIO_PIN_RESET : pont ouvert */

		HAL_GPIO_WritePin( GPIOC, GPIO_PIN_12, en_steering);  //PC12  AV
}

int get_steering_angle(void){
	return ADCBUF[1];
}

void position_cmd (GPIO_PinState en_steering, int msg_CAN){

	int cpt_pos = get_steering_angle();
	int cpt_centre, msg_corr, angle_diff;

	cpt_centre = cpt_pos - centre_volant; // valeur entre 0 et 606 (avec de la chance...)
	msg_corr = coeff_correction*(msg_CAN - 50); // valeur entre 0 et 600

	/*// Limit the steering
	if (cpt_centre > 0xFF){cpt_centre = 0xFF;}
	else if (cpt_centre < -0xFF){cpt_centre = -0xFF;}
	*/ // plus besoin de ce truc !!
	
	
	angle_diff = msg_corr - cpt_centre;

	// Discrete command turning/steady
	if (abs(angle_diff)<100){
		if(abs(angle_diff)<25){steering_set_speed(GPIO_PIN_RESET, MEDIUM_CMD_STEERING);}// Don't move
		else if (angle_diff > 0){steering_set_speed(en_steering, MIN_CMD_STEERING2);}// Go Left ??
		else {steering_set_speed(en_steering, MAX_CMD_STEERING2);} // Go Right ??
	}
	else if (angle_diff > 0){steering_set_speed(en_steering, MIN_CMD_STEERING1);}// Go Left ??
	else {steering_set_speed(en_steering, MAX_CMD_STEERING1);} // Go Right ??
}

void STEE_setCanMess(uint8_t* data){
			int pos;
			data[0] = (gauche_volant >> 8) & 0xFF; // PosGauche //pour vérif
			data[1] = gauche_volant & 0xFF;
			
			data[2] = (droite_volant >> 8) & 0xFF; // PosDroite //pour vérif
			data[3] = droite_volant & 0xFF;
			
			pos = ((get_steering_angle() - droite_volant) * 100) / (gauche_volant - droite_volant);
	
			data[4] = (pos >> 8) & 0xFF; // Actual position of the steering wheel
			data[5] = pos & 0xFF;
			
			data[6] = (applied_cmd >> 8) & 0xFF; // VMD_mes
			data[7] = applied_cmd & 0xFF;
}
