#include "cy_pdl.h"
#include "cybsp_types.h"
#include "cy_retarget_io.h"
#include "cybsp.h"
#include "cyhal.h"
#include "cycfg_pins.h"
#include "cycfg_ble.h"
#include "ble_findme.h"

static const cy_stc_sysint_t butt_isr_config =
{
  /* The BLESS interrupt */
  .intrSrc = BUTT_IRQ,

  /* The interrupt priority number */
  .intrPriority = 1u
};

#define MCWDT_INTR_PRIORITY     (7u)

static void butt_interrupt_handler(void) {
	Cy_GPIO_ClearInterrupt(BUTT_PORT, BUTT_NUM);
    NVIC_ClearPendingIRQ(butt_isr_config.intrSrc);
	printf("Button has been pressed \r\n");
	found_mask |= BTN_PRESSED;
	mcwdt_timer_flag = 0;
	Cy_MCWDT_ResetCounters(CYBSP_MCWDT_HW, CY_MCWDT_CTR0 | CY_MCWDT_CTR1, 150);
}

static void mcwdt_interrupt_handler(void) {
    Cy_MCWDT_ClearInterrupt(CYBSP_MCWDT_HW, CY_MCWDT_CTR0 | CY_MCWDT_CTR1);
	mcwdt_timer_flag = 1;
}

int main(void)
{
    cy_rslt_t result;

    /* Configure switch SW2 as hibernate wake up source */
    Cy_SysPm_SetHibWakeupSource(CY_SYSPM_HIBPIN1_LOW);

    /* Unfreeze IO if device is waking up from hibernate */
    if(Cy_SysPm_GetIoFreezeStatus())
    {
        Cy_SysPm_IoUnfreeze();
    }

    /* Initialize the device and board peripherals */
    result = cybsp_init();
    
    /* Board init failed. Stop program execution */
    if (result != CY_RSLT_SUCCESS)
    {
        CY_ASSERT(0);
    }

    /* Initialize retarget-io to use the debug UART port */
    result = cy_retarget_io_init(CYBSP_DEBUG_UART_TX, CYBSP_DEBUG_UART_RX, \
                                 CY_RETARGET_IO_BAUDRATE);

    /* \x1b[2J\x1b[;H - ANSI ESC sequence for clear screen */
    printf("\x1b[2J\x1b[;H");
    printf("PSoC 6 MCU With RSSI Client \r\n");

    /* retarget-io init failed. Stop program execution */
    if (result != CY_RSLT_SUCCESS)
    {
        CY_ASSERT(0);
    }


    /* Initialize the User LEDs */
    result = cyhal_gpio_init((cyhal_gpio_t)CYBSP_USER_LED1, CYHAL_GPIO_DIR_OUTPUT,
                             CYHAL_GPIO_DRIVE_STRONG, CYBSP_LED_STATE_OFF);
    result |= cyhal_gpio_init((cyhal_gpio_t)CYBSP_USER_LED2, CYHAL_GPIO_DIR_OUTPUT,
                              CYHAL_GPIO_DRIVE_STRONG, CYBSP_LED_STATE_OFF);
    
    /* Configure USER_BTN */
    (void) Cy_SysInt_Init(&butt_isr_config, butt_interrupt_handler);
    NVIC_ClearPendingIRQ(butt_isr_config.intrSrc);
    NVIC_EnableIRQ(butt_isr_config.intrSrc);
    
    /* gpio init failed. Stop program execution */
    if (result != CY_RSLT_SUCCESS)
    {
        CY_ASSERT(0);
    }

    init_cycfg_pins();

    /* Configure BLE */
    ble_init();

     /* Step 1 - Unlock WDT */
    Cy_MCWDT_Unlock(CYBSP_MCWDT_HW);

    /* Step 2 - Initial configuration of MCWDT */
	Cy_MCWDT_Init(CYBSP_MCWDT_HW, &CYBSP_MCWDT_config);

    /* Step 3 - Clear match event interrupt, if any */
    Cy_MCWDT_ClearInterrupt(CYBSP_MCWDT_HW, CY_MCWDT_CTR0 | CY_MCWDT_CTR1);

    /* Step 4 - Enable ILO */
    Cy_SysClk_IloEnable();

    const cy_stc_sysint_t mcwdt_isr_config =
    {
      .intrSrc = (IRQn_Type)CYBSP_MCWDT_IRQ,
      .intrPriority = MCWDT_INTR_PRIORITY
    };

    /* Step 5 - Enable interrupt if periodic interrupt mode selected */
    Cy_SysInt_Init(&mcwdt_isr_config, mcwdt_interrupt_handler);

    NVIC_EnableIRQ(mcwdt_isr_config.intrSrc);

	Cy_MCWDT_SetInterruptMask(CYBSP_MCWDT_HW, CY_MCWDT_CTR0 | CY_MCWDT_CTR1);
    /* Step 6- Enable WDT */
	Cy_MCWDT_Enable(CYBSP_MCWDT_HW, CY_MCWDT_CTR0 | CY_MCWDT_CTR1, 93u);

    /* Step 7- Lock WDT configuration */
    Cy_MCWDT_Lock(CYBSP_MCWDT_HW);

    /* Enable global interrupts */
    __enable_irq();

    found_mask = 0;
    uint8_t count = SAMPLE_NUM;
    for(int i = 0; i < 3; i++) {
    	rssi_values[i] = 0;
    }

    for(;;)
    {
        ble_findme_process();
        if((found_mask & FOUND_BEACONS_123) == FOUND_BEACONS_123 && mcwdt_timer_flag == 1) {
        	if(count == SAMPLE_NUM) {
        		printf("[INFO] RSSI sampling started\r\n");
        	}
			cyhal_gpio_write((cyhal_gpio_t)CYBSP_USER_LED2, CYBSP_LED_STATE_ON);
        	printf("[INFO] RSSI values: %d %d %d \r\n", rssi_values[0], rssi_values[1], rssi_values[2]);
        	found_mask = 8;
        	count--;
        	if(!count) {
        		count = SAMPLE_NUM;
        		found_mask = 0;
				cyhal_gpio_write((cyhal_gpio_t)CYBSP_USER_LED2, CYBSP_LED_STATE_OFF);
        		printf("[INFO] RSSI sampling ended\r\n");
        	}
        	CyDelay(50);
        }
    }
}


/* END OF FILE */

