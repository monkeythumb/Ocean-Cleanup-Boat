#ifndef PI_PROPULSION_H
#define PI_PROPULSION_H

#include <cstdint>

// Initialize pigpio and thruster pins
bool propulsion_init(int left_gpio = 18, int right_gpio = 19);

// Set thrust for each side: -100..100
void propulsion_set(int left_percent, int right_percent);

// Stop both thrusters
void propulsion_stop();

// Simple mixer helpers
void propulsion_forward(int percent);
void propulsion_turn_left(int percent);
void propulsion_turn_right(int percent);

#endif
