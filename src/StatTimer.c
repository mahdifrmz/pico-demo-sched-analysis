/* Scheduler includes. */
#include "FreeRTOS.h"
#include "task.h"
#include "StatTimer.h"

/* Demo includes. */
#include "IntQueueTimer.h"
#include "IntQueue.h"

/* SDK APIs.*/
#include "pico/time.h"
#include "hardware/irq.h"

#define tmrMAX_PRIORITY ( 1UL )
#define tmrNUM ( 2 )
#define tmrIRQ TIMER_IRQ_2
#define tmrPERSIOD_US (100)

volatile uint32_t ulTimer;

void prvAlarm2Callback( uint timer )
{
    configASSERT(timer == tmrNUM);
    hardware_alarm_set_target(tmrNUM, make_timeout_time_us( tmrPERSIOD_US) );
    ulTimer++;
}

void vInitialiseStatTimer( void )
{
    ulTimer = 0;
    hardware_alarm_claim(tmrNUM);
    taskDISABLE_INTERRUPTS();
    irq_set_priority(TIMER_IRQ_2, tmrMAX_PRIORITY);
    hardware_alarm_set_callback(tmrNUM, prvAlarm2Callback);
    hardware_alarm_set_target(tmrNUM, make_timeout_time_us( tmrPERSIOD_US) );
}

uint32_t ulGetStatTimer( void )
{
    return ulTimer;
}

void vConfigureStatTimer( void )
{
    ulTimer = 0;
}