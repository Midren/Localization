/******************************************************************************
* File Name: ble_findme.h
*
* Description: This file is public interface of ble_findme.c
*
* Related Document: Readme.md
*
*******************************************************************************
* Copyright (2019), Cypress Semiconductor Corporation. All rights reserved.
*******************************************************************************
* This software, including source code, documentation and related materials
* ("Software"), is owned by Cypress Semiconductor Corporation or one of its
* subsidiaries ("Cypress") and is protected by and subject to worldwide patent
* protection (United States and foreign), United States copyright laws and
* international treaty provisions. Therefore, you may use this Software only
* as provided in the license agreement accompanying the software package from
* which you obtained this Software ("EULA").
*
* If no EULA applies, Cypress hereby grants you a personal, non-exclusive,
* non-transferable license to copy, modify, and compile the Software source
* code solely for use in connection with Cypress's integrated circuit products.
* Any reproduction, modification, translation, compilation, or representation
* of this Software except as specified above is prohibited without the express
* written permission of Cypress.
*
* Disclaimer: THIS SOFTWARE IS PROVIDED AS-IS, WITH NO WARRANTY OF ANY KIND,
* EXPRESS OR IMPLIED, INCLUDING, BUT NOT LIMITED TO, NONINFRINGEMENT, IMPLIED
* WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE. Cypress
* reserves the right to make changes to the Software without notice. Cypress
* does not assume any liability arising out of the application or use of the
* Software or any product or circuit described in the Software. Cypress does
* not authorize its products for use in any products where a malfunction or
* failure of the Cypress product may reasonably be expected to result in
* significant property damage, injury or death ("High Risk Product"). By
* including Cypress's product in a High Risk Product, the manufacturer of such
* system or application assumes all risk of such use and in doing so agrees to
* indemnify Cypress against all liability.
******************************************************************************/


/******************************************************************************
 * Include guard
 *****************************************************************************/
#ifndef BLE_FIND_ME_H
#define BLE_FIND_ME_H

#include "cycfg_ble.h"

/******************************************************************************
 * Function prototypes
 *****************************************************************************/
void ble_init(void);
void ble_findme_process(void);

cy_stc_ble_rssi_info_t rssi_value;
int8_t rssi_values[3];
uint8_t found_mask;
bool mcwdt_timer_flag;

#define BTN_PRESSED (8u)
#define FOUND_BEACONS_1 ((1u) | BTN_PRESSED)
#define FOUND_BEACONS_2 ((2u) | BTN_PRESSED)
#define FOUND_BEACONS_3 ((4u) | BTN_PRESSED)
#define FOUND_BEACONS_12 (FOUND_BEACONS_1 | FOUND_BEACONS_2)
#define FOUND_BEACONS_123 (FOUND_BEACONS_12 | FOUND_BEACONS_3)

#define SAMPLE_NUM (200u)

#endif  /* BLE_FIND_ME_H */


/* END OF FILE [] */
