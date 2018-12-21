
/**
  ******************************************************************************
  * @file           : main.c
  * @brief          : Main program body
  ******************************************************************************
  ** This notice applies to any and all portions of this file
  * that are not between comment pairs USER CODE BEGIN and
  * USER CODE END. Other portions of this file, whether 
  * inserted by the user or by software development tools
  * are owned by their respective copyright owners.
  *
  * COPYRIGHT(c) 2018 STMicroelectronics
  *
  * Redistribution and use in source and binary forms, with or without modification,
  * are permitted provided that the following conditions are met:
  *   1. Redistributions of source code must retain the above copyright notice,
  *      this list of conditions and the following disclaimer.
  *   2. Redistributions in binary form must reproduce the above copyright notice,
  *      this list of conditions and the following disclaimer in the documentation
  *      and/or other materials provided with the distribution.
  *   3. Neither the name of STMicroelectronics nor the names of its contributors
  *      may be used to endorse or promote products derived from this software
  *      without specific prior written permission.
  *
  * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
  * AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
  * IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
  * DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
  * FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
  * DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
  * SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
  * CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
  * OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
  * OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
  *
  ******************************************************************************
  */
/* Includes ------------------------------------------------------------------*/
#include "main.h"
#include "stm32f1xx_hal.h"
#include "adc.h"
#include "can.h"
#include "dma.h"
#include "tim.h"
#include "usart.h"
#include "gpio.h"



/* USER CODE BEGIN Includes */

/* USER CODE END Includes */

/* Private variables ---------------------------------------------------------*/

/* USER CODE BEGIN PV */
/* Private variables ---------------------------------------------------------*/
int UPDATE_CMD_FLAG = 0;
int SEND_CAN = 0;
int UPDATE_STE_INFO = 0;

/* Tous ADC sur 12 bits pleine echelle 3.3V
	ADCBUF[0] mesure batterie 
	ADCBUF[1] angle volant
	ADCBUF[2] I moteur arriere gauche
	ADCBUF[3] I moteur arriere droit
	ADCBUF[4] I moteur avant
*/
uint32_t ADCBUF[5];

int cmdLRM = 50, cmdRRM = 50, cmdSFM = 50; // 0 à 100 Moteur gauche, droit, avant

uint32_t VMG_mes = 0, VMD_mes = 0, per_vitesseG = 0, per_vitesseD = 0;
//int	volatile i=0;
/* Enable Moteurs */
GPIO_PinState en_MARG = GPIO_PIN_RESET;
GPIO_PinState en_MARD = GPIO_PIN_RESET;
GPIO_PinState en_MAV  = GPIO_PIN_RESET;
/*********************************Informations rotation volant********************************/
/* mesure angulaire potentiometre amplitudes volant +/- 17 % environ autour du centre        */
/* PWM = 0.5 (50) % arret, PWM = 0.4 tourne gauche, PWM = 0.6 tourne droite                  */
/*butees potar  volant :                                                                         */
//#define gauche_volant 2446 /*2395*/  
//#define centre_volant (gauche_volant+droite_volant)/2/*2056*/  
//#define droite_volant 1840/*1825*/  

CanTxMsgTypeDef TxMessage;
CanRxMsgTypeDef RxMessage;
uint8_t data[8] = {0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77, 0x88};


extern CAN_HandleTypeDef hcan;


/* USER CODE END PV */

/* Private function prototypes -----------------------------------------------*/
void SystemClock_Config(void);

/* USER CODE BEGIN PFP */
/* Private function prototypes -----------------------------------------------*/

/* USER CODE END PFP */

/* USER CODE BEGIN 0 */
void HAL_TIM_PeriodElapsedCallback(TIM_HandleTypeDef *htim){
	if (htim->Instance==TIM2)
	{
		VMG_mes = 0;
	} else if (htim->Instance==TIM4){
		VMD_mes = 0;
	}
}


void HAL_TIM_IC_CaptureCallback(TIM_HandleTypeDef *htim)
{
	/***               Mesures des vitesses moteurs                      ***
	* Féquences entrées micro, sorties capteurs, entre environ 2hz à 80 hz *
	* Timer 2,4 sur 16 bits (65535)cp ->compte période 9999 pour 1s (1Hz)  * 
	*                               ->compte période 1000 pour 0.1s (10Hz) *
	* Rapport réduction 2279/64 ~ 36 impulsions/tour de roue               *
	* unite de 0.01*tr/mn = 168495/ cp                                     *  
	*/
	if (htim->Instance==TIM2)
	{
		per_vitesseG =	HAL_TIM_ReadCapturedValue (&htim2,TIM_CHANNEL_3);//PB10
		VMG_mes = 1684949/per_vitesseG ;// X 0.01 tr/mn	

		__HAL_TIM_SET_COUNTER(&htim2,0);// mise a zero compteur apres capture
	}
	if (htim->Instance==TIM4)
	{
		per_vitesseD =	HAL_TIM_ReadCapturedValue (&htim4,TIM_CHANNEL_3);//PB8
		VMD_mes = 1684949/per_vitesseD ;// X 0.01 tr/mn	
			
		__HAL_TIM_SET_COUNTER(&htim4,0);// mise a zero compteur apres capture
	}
}



/* USER CODE END 0 */

/**
  * @brief  The application entry point.
  *
  * @retval None
  */
int main(void)
{
  /* USER CODE BEGIN 1 */
	hcan.pTxMsg = &TxMessage;
	hcan.pRxMsg = &RxMessage;
  /* USER CODE END 1 */

  /* MCU Configuration----------------------------------------------------------*/

  /* Reset of all peripherals, Initializes the Flash interface and the Systick. */
  HAL_Init();

  /* USER CODE BEGIN Init */

  /* USER CODE END Init */

  /* Configure the system clock */
  SystemClock_Config();

  /* USER CODE BEGIN SysInit */

  /* USER CODE END SysInit */

  /* Initialize all configured peripherals */
  MX_GPIO_Init();
  MX_DMA_Init();
  MX_USART2_UART_Init();
  MX_TIM1_Init();
  MX_TIM2_Init();
  MX_TIM4_Init();
  MX_ADC1_Init();
  MX_CAN_Init();
  /* USER CODE BEGIN 2 */

  /* Initialisations */
	
	/*gestion systic 1Khz*/
	
	//uint32_t usTicks = HAL_RCC_GetSysClockFreq() / 1000;   
	// HAL_SYSTICK_Config(usTicks);

  /* PWM MOTEURS */
	HAL_TIM_PWM_Start(&htim1, TIM_CHANNEL_1);
	HAL_TIM_PWM_Start(&htim1, TIM_CHANNEL_2);
	HAL_TIM_PWM_Start(&htim1, TIM_CHANNEL_3);

	//Sorties complementaires
	HAL_TIMEx_OCN_Start(&htim1,TIM_CHANNEL_1);
	HAL_TIMEx_OCN_Start(&htim1,TIM_CHANNEL_2);
	HAL_TIMEx_OCN_Start(&htim1,TIM_CHANNEL_3);
	/*Vitesse*/
	__HAL_TIM_ENABLE_IT(&htim2, TIM_IT_UPDATE);
	__HAL_TIM_ENABLE_IT(&htim4, TIM_IT_UPDATE);
  HAL_TIM_IC_Start_IT (&htim2,TIM_CHANNEL_3);//autorisation IT capture CH3
  HAL_TIM_IC_Start_IT (&htim4,TIM_CHANNEL_3);//autorisation IT capture CH3

  /* ADC1 */
  HAL_ADC_Start_DMA (&hadc1,ADCBUF,5);
	
	/* CAN */
	CAN_FilterConfig();
	__HAL_CAN_ENABLE_IT(&hcan, CAN_IT_FMP0);

	init_steering();
	/* USER CODE END 2 */

  /* Infinite loop */
  /* USER CODE BEGIN WHILE */
	
  while (1)
  {
  /* USER CODE END WHILE */

  /* USER CODE BEGIN 3 */
		
		/* Update motors command*/
		if (UPDATE_CMD_FLAG){
			UPDATE_CMD_FLAG = 0;
			
			wheels_set_speed(en_MARD, en_MARG, cmdRRM, cmdLRM);
			position_cmd(en_MAV, cmdSFM);
		}
		
		/* CAN */
		// Envoi des mesures
		if (SEND_CAN){
			SEND_CAN = 0;
			data[0] = (ADCBUF[1] >> 8) & 0xFF; // Vol_mes
			data[1] = ADCBUF[1] & 0xFF;
			
			data[2] = (ADCBUF[0] >> 8) & 0xFF; // Bat_mes
			data[3] = ADCBUF[0] & 0xFF;
			
			data[4] = (VMG_mes >> 8) & 0xFF; // VMG_mes
			data[5] = VMG_mes & 0xFF;
			
			data[6] = (VMD_mes >> 8) & 0xFF; // VMD_mes
			data[7] = VMD_mes & 0xFF;
			
			CAN_Send(data, CAN_ID_MS);
		}
		
		if(UPDATE_STE_INFO){
			UPDATE_STE_INFO = 0;
			STEE_setCanMess(data);
			CAN_Send(data, 0x300);
		}
  }
  /* USER CODE END 3 */

}

/**
  * @brief System Clock Configuration
  * @retval None
  */
void SystemClock_Config(void)
{

  RCC_OscInitTypeDef RCC_OscInitStruct;
  RCC_ClkInitTypeDef RCC_ClkInitStruct;
  RCC_PeriphCLKInitTypeDef PeriphClkInit;

    /**Initializes the CPU, AHB and APB busses clocks 
    */
  RCC_OscInitStruct.OscillatorType = RCC_OSCILLATORTYPE_HSI;
  RCC_OscInitStruct.HSIState = RCC_HSI_ON;
  RCC_OscInitStruct.HSICalibrationValue = 16;
  RCC_OscInitStruct.PLL.PLLState = RCC_PLL_ON;
  RCC_OscInitStruct.PLL.PLLSource = RCC_PLLSOURCE_HSI_DIV2;
  RCC_OscInitStruct.PLL.PLLMUL = RCC_PLL_MUL16;
  if (HAL_RCC_OscConfig(&RCC_OscInitStruct) != HAL_OK)
  {
    _Error_Handler(__FILE__, __LINE__);
  }

    /**Initializes the CPU, AHB and APB busses clocks 
    */
  RCC_ClkInitStruct.ClockType = RCC_CLOCKTYPE_HCLK|RCC_CLOCKTYPE_SYSCLK
                              |RCC_CLOCKTYPE_PCLK1|RCC_CLOCKTYPE_PCLK2;
  RCC_ClkInitStruct.SYSCLKSource = RCC_SYSCLKSOURCE_PLLCLK;
  RCC_ClkInitStruct.AHBCLKDivider = RCC_SYSCLK_DIV1;
  RCC_ClkInitStruct.APB1CLKDivider = RCC_HCLK_DIV2;
  RCC_ClkInitStruct.APB2CLKDivider = RCC_HCLK_DIV1;

  if (HAL_RCC_ClockConfig(&RCC_ClkInitStruct, FLASH_LATENCY_2) != HAL_OK)
  {
    _Error_Handler(__FILE__, __LINE__);
  }

  PeriphClkInit.PeriphClockSelection = RCC_PERIPHCLK_ADC;
  PeriphClkInit.AdcClockSelection = RCC_ADCPCLK2_DIV8;
  if (HAL_RCCEx_PeriphCLKConfig(&PeriphClkInit) != HAL_OK)
  {
    _Error_Handler(__FILE__, __LINE__);
  }

    /**Configure the Systick interrupt time 
    */
  HAL_SYSTICK_Config(HAL_RCC_GetHCLKFreq()/1000);

    /**Configure the Systick 
    */
  HAL_SYSTICK_CLKSourceConfig(SYSTICK_CLKSOURCE_HCLK);

  /* SysTick_IRQn interrupt configuration */
  HAL_NVIC_SetPriority(SysTick_IRQn, 0, 0);
}

/* USER CODE BEGIN 4 */

/* USER CODE END 4 */

/**
  * @brief  This function is executed in case of error occurrence.
  * @param  file: The file name as string.
  * @param  line: The line in file as a number.
  * @retval None
  */
void _Error_Handler(char *file, int line)
{
  /* USER CODE BEGIN Error_Handler_Debug */
  /* User can add his own implementation to report the HAL error return state */
  /*while(1)
  {
  }*/
  /* USER CODE END Error_Handler_Debug */
}

#ifdef  USE_FULL_ASSERT
/**
  * @brief  Reports the name of the source file and the source line number
  *         where the assert_param error has occurred.
  * @param  file: pointer to the source file name
  * @param  line: assert_param error line source number
  * @retval None
  */
void assert_failed(uint8_t* file, uint32_t line)
{ 
  /* USER CODE BEGIN 6 */
  /* User can add his own implementation to report the file name and line number,
    ex: printf("Wrong parameters value: file %s on line %d\r\n", file, line) */
  /* USER CODE END 6 */
}
#endif /* USE_FULL_ASSERT */

/**
  * @}
  */

/**
  * @}
  */

/************************ (C) COPYRIGHT STMicroelectronics *****END OF FILE****/
