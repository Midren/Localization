#include "cy_pdl.h"
#include "cybsp_types.h"
#include "cy_retarget_io.h"
#include "cybsp.h"
#include "cyhal.h"
#include "ble_findme.h"


int main(void)
{
    cy_rslt_t result;

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

    /* retarget-io init failed. Stop program execution */
    if (result != CY_RSLT_SUCCESS)
    {
        CY_ASSERT(0);
    }


    /* \x1b[2J\x1b[;H - ANSI ESC sequence for clear screen */
    printf("\x1b[2J\x1b[;H");
    printf("PSoC 6 MCU With BLE Connectivity Find Me\r\n\n");

    ble_findme_init();

    for(;;)
    {
        ble_findme_process();
    }
}


/* END OF FILE */

