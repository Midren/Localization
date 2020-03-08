#include "ble_findme.h"
#include "cyhal.h"
#include "cy_retarget_io.h"
#include "cybsp.h"


/*******************************************************************************
* Macros
********************************************************************************/
#define BLESS_INTR_PRIORITY     (1u)


/*******************************************************************************
* Global Variables
********************************************************************************/
bool gpio_intr_flag = false;
cy_stc_ble_conn_handle_t app_conn_handle;


/*******************************************************************************
* Function Prototypes
********************************************************************************/
static void bless_interrupt_handler(void);
static void stack_event_handler(uint32 event, void* eventParam);


typedef struct {
	char* name;
	int name_len;
	uint8_t *serviceUUID;
	uint8_t servUUID_len;
} advInfo_t;

advInfo_t currentAdvInfo;

static void findAdvInfo(uint8_t *adv, uint8_t len) {
	memset(&currentAdvInfo, 0, sizeof(currentAdvInfo));

	for(uint8_t i=0; i<len;) {
		switch(adv[i+1]) {
		case 0x07:
			currentAdvInfo.serviceUUID = &adv[i+2];
			currentAdvInfo.servUUID_len = adv[i]-1;
			break;
		case 0x09:
			currentAdvInfo.name = (char*) &adv[i+2];
			currentAdvInfo.name_len = adv[i]-1;
			break;
		}
		i = i + adv[i]+1;
	}
}

void saveRSSI_value(int8_t rssi_value) {
	cy_stc_ble_gatt_handle_value_pair_t handleValuePair = {
		.value.val = (uint8_t*)&rssi_value,
		.value.len = sizeof(int8_t)/sizeof(uint8_t),
		.value.actualLen = sizeof(int8_t)/sizeof(uint8_t),
		.attrHandle = CY_BLE_RSSI_MEASURE_VALUE_CHAR_HANDLE
	};

	cy_en_ble_gatt_err_code_t err = Cy_BLE_GATTS_WriteAttributeValueLocal(&handleValuePair);
	if(err != CY_BLE_GATT_ERR_NONE) {
		printf("BLE GATTC write error %d\r\n", err);
	}
}

/*******************************************************************************
* Function Name: ble_findme_process
********************************************************************************
* Summary:
*  This function processes the BLE events and configures the device to enter
*  low power mode as required.
*
*******************************************************************************/
void ble_findme_process(void)
{
    /* Cy_BLE_ProcessEvents() allows the BLE stack to process pending events */
    Cy_BLE_ProcessEvents();
    
	/* Update CYBSP_USER_LED1 to indicate current BLE status */
	if(CY_BLE_ADV_STATE_ADVERTISING == Cy_BLE_GetAdvertisementState()) {
		cyhal_gpio_toggle((cyhal_gpio_t)CYBSP_USER_LED1);
	} else if(CY_BLE_CONN_STATE_CONNECTED == Cy_BLE_GetConnectionState(app_conn_handle)) {
		cyhal_gpio_write((cyhal_gpio_t)CYBSP_USER_LED1, CYBSP_LED_STATE_ON);
	} else {
		cyhal_gpio_write((cyhal_gpio_t)CYBSP_USER_LED1, CYBSP_LED_STATE_OFF);
	}
}


/*******************************************************************************
* Function Name: ble_init
********************************************************************************
* Summary:
*  This function initializes the BLE and registers IAS callback function.
*
*******************************************************************************/
void ble_init(void)
{
    static const cy_stc_sysint_t bless_isr_config =
    {
      /* The BLESS interrupt */
      .intrSrc = bless_interrupt_IRQn,

      /* The interrupt priority number */
      .intrPriority = BLESS_INTR_PRIORITY
    };

    /* Hook interrupt service routines for BLESS */
    (void) Cy_SysInt_Init(&bless_isr_config, bless_interrupt_handler);

    /* Store the pointer to blessIsrCfg in the BLE configuration structure */
    cy_ble_config.hw->blessIsrConfig = &bless_isr_config;

    /* Registers the generic callback functions  */
    Cy_BLE_RegisterEventCallback(stack_event_handler);

    /* Initializes the BLE host */
    Cy_BLE_Init(&cy_ble_config);

    /* Enables BLE */
    Cy_BLE_Enable();

    /* Enables BLE Low-power mode (LPM)*/
    Cy_BLE_EnableLowPowerMode();
}


/******************************************************************************
* Function Name: bless_interrupt_handler
*******************************************************************************
* Summary:
*  Wrapper function for handling interrupts from BLESS.
*
******************************************************************************/
static void bless_interrupt_handler(void)
{
    Cy_BLE_BlessIsrHandler();
}


/*******************************************************************************
* Function Name: stack_event_handler
********************************************************************************
*
* Summary:
*   This is an event callback function to receive events from the BLE Component.
*
* Parameters:
*  uint32 event:      event from the BLE component
*  void* eventParam:  parameters related to the event
*
*******************************************************************************/
static void stack_event_handler(uint32_t event, void* eventParam)
{
    switch(event)
    {
        /**********************************************************************
         * General events
         *********************************************************************/

        /* This event is received when the BLE stack is started */
        case CY_BLE_EVT_STACK_ON:
        {
            printf("[INFO] : BLE stack started \r\n");
            Cy_BLE_GAPC_StartScan(CY_BLE_SCANNING_FAST, 0);
            break;
        }

        /* This event is received when there is a timeout */
        case CY_BLE_EVT_TIMEOUT:
        {
            /* Reason for Timeout */
            cy_en_ble_to_reason_code_t reason_code =
                ((cy_stc_ble_timeout_param_t*)eventParam)->reasonCode;

            switch(reason_code)
            {
                case CY_BLE_GAP_ADV_TO:
                {
                    printf("[INFO] : Advertisement timeout event \r\n");
                    break;
                }
                case CY_BLE_GATT_RSP_TO:
                {
                    printf("[INFO] : GATT response timeout\r\n");
                    break;
                }
                default:
                {
                    printf("[INFO] : BLE timeout event\r\n");
                    break;
                }
            }

            break;
        }

        /**********************************************************************
         * GAP events
         *********************************************************************/

        /* This event is generated at the GAP Peripheral end after connection
         * is completed with peer Central device
         */
        case CY_BLE_EVT_GAPC_SCAN_PROGRESS_RESULT: {
        	cy_stc_ble_gapc_adv_report_param_t *scanProgressParam = (cy_stc_ble_gapc_adv_report_param_t *) eventParam;
        	findAdvInfo(scanProgressParam->data, scanProgressParam->dataLen);

        	if(currentAdvInfo.name_len > 0) {
				currentAdvInfo.name[currentAdvInfo.name_len] = '\0';
				if(!strcmp(currentAdvInfo.name, "RSSI-Server-1")) {
					rssi_values[0] = found_mask & 1 ? rssi_values[0] : scanProgressParam->rssi;
					found_mask |= 1;
				} else if(!strcmp(currentAdvInfo.name, "RSSI-Server-2")) {
					rssi_values[1] = found_mask & 2 ? rssi_values[1] : scanProgressParam->rssi;
					found_mask |= 2;
				} else if(!strcmp(currentAdvInfo.name, "RSSI-Server-3")) {
					rssi_values[2] = found_mask & 4 ? rssi_values[2] : scanProgressParam->rssi;
					found_mask |= 4;
				}
        	}
        	break;
        }
        /**********************************************************************
         * GATT events
         *********************************************************************/

        /* This event is generated at the GAP Peripheral end after connection
         * is completed with peer Central device
         */
        case CY_BLE_EVT_GATT_CONNECT_IND:
        {
            app_conn_handle = *(cy_stc_ble_conn_handle_t *)eventParam;
            printf("[INFO] : GATT device connected\r\n");
            break;
        }

        default:
        {
            printf("[INFO] : BLE Event 0x%lX\r\n", (unsigned long) event);
        }
    }
}

/* [] END OF FILE */
