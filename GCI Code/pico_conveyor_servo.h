#ifndef PICO_CONVEYOR_SERVO_H
#define PICO_CONVEYOR_SERVO_H

#include <stdint.h>
#include <stdbool.h>

// Initialize PWM on a GPIO pin for servo control
void conveyor_servo_init(uint servo_gpio);

// Set servo speed for continuous-rotation servo.
// speed ranges from -100 to +100.
//  0   = stop
//  +100 = full forward
//  -100 = full reverse
void conveyor_servo_set_speed(int speed);

// Convenience helpers
void conveyor_servo_stop(void);
void conveyor_servo_forward(int speed_percent);
void conveyor_servo_reverse(int speed_percent);

#endif
