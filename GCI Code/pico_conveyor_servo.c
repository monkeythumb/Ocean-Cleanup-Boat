#include "pico_conveyor_servo.h"
#include "pico/stdlib.h"
#include "hardware/pwm.h"
#include "hardware/clocks.h"

// --- Servo timing constants ---
// Most servos expect 50 Hz (20 ms period).
#define SERVO_FREQ_HZ     50.0f
#define SERVO_PERIOD_US   20000.0f  // 20 ms

// Pulse widths for continuous rotation servos.
// You MAY need to tune these slightly for your specific servo.
// Typical:
// 1500 us = stop
// 1000 us = full reverse
// 2000 us = full forward
#define SERVO_STOP_US     1500.0f
#define SERVO_MIN_US      1000.0f
#define SERVO_MAX_US      2000.0f

static uint g_servo_gpio = 0;
static uint g_pwm_slice = 0;
static uint g_pwm_chan = 0;
static uint32_t g_wrap = 0;

// Convert microseconds pulse width to PWM level
static uint32_t us_to_level(float pulse_us) {
    // PWM clock for this slice
    uint32_t sys_clk = clock_get_hz(clk_sys);

    // We set a divider so PWM runs at a convenient frequency.
    // PWM frequency = sys_clk / divider / (wrap + 1).
    // wrap chosen to make 50 Hz period.
    float divider = 64.0f; // stable default for Pico
    float pwm_clk = (float)sys_clk / divider;

    // One PWM tick duration in us:
    float tick_us = 1e6f / pwm_clk;

    return (uint32_t)(pulse_us / tick_us);
}

void conveyor_servo_init(uint servo_gpio) {
    g_servo_gpio = servo_gpio;

    gpio_set_function(g_servo_gpio, GPIO_FUNC_PWM);
    g_pwm_slice = pwm_gpio_to_slice_num(g_servo_gpio);
    g_pwm_chan  = pwm_gpio_to_channel(g_servo_gpio);

    uint32_t sys_clk = clock_get_hz(clk_sys);

    // Choose divider and wrap to get 50 Hz
    float divider = 64.0f;
    float pwm_clk = (float)sys_clk / divider;
    g_wrap = (uint32_t)(pwm_clk / SERVO_FREQ_HZ) - 1;

    pwm_config cfg = pwm_get_default_config();
    pwm_config_set_clkdiv(&cfg, divider);
    pwm_config_set_wrap(&cfg, g_wrap);

    pwm_init(g_pwm_slice, &cfg, true);

    conveyor_servo_stop();
}

void conveyor_servo_set_speed(int speed) {
    if (speed > 100) speed = 100;
    if (speed < -100) speed = -100;

    float pulse_us = SERVO_STOP_US;

    if (speed > 0) {
        // map 0..100 -> STOP..MAX
        pulse_us = SERVO_STOP_US +
                   (SERVO_MAX_US - SERVO_STOP_US) * ((float)speed / 100.0f);
    } else if (speed < 0) {
        // map -100..0 -> MIN..STOP
        pulse_us = SERVO_STOP_US +
                   (SERVO_STOP_US - SERVO_MIN_US) * ((float)speed / 100.0f);
    }

    uint32_t level = us_to_level(pulse_us);
    pwm_set_chan_level(g_pwm_slice, g_pwm_chan, level);
}

void conveyor_servo_stop(void) {
    conveyor_servo_set_speed(0);
}

void conveyor_servo_forward(int speed_percent) {
    if (speed_percent < 0) speed_percent = -speed_percent;
    conveyor_servo_set_speed(speed_percent);
}

void conveyor_servo_reverse(int speed_percent) {
    if (speed_percent < 0) speed_percent = -speed_percent;
    conveyor_servo_set_speed(-speed_percent);
}

// ------------------- Example main -------------------
// Put this in main.c if you want a quick test:
//
// int main() {
//     stdio_init_all();
//     conveyor_servo_init(15); // GPIO15
//     while (true) {
//         conveyor_servo_forward(60);  // run belt
//         sleep_ms(5000);
//         conveyor_servo_stop();
//         sleep_ms(2000);
//     }
// }
