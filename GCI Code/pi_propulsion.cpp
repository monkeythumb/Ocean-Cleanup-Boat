#include "pi_propulsion.h"
#include <pigpio.h>
#include <cstdio>
#include <algorithm>

// Servo/ESC pulse widths
static const int STOP_US = 1500;
static const int MIN_US  = 1000;
static const int MAX_US  = 2000;

static int g_left_gpio = 18;
static int g_right_gpio = 19;

static int clamp100(int v) {
    return std::max(-100, std::min(100, v));
}

static int percent_to_us(int percent) {
    percent = clamp100(percent);
    if (percent == 0) return STOP_US;

    if (percent > 0) {
        return STOP_US + (int)((MAX_US - STOP_US) * (percent / 100.0));
    } else {
        return STOP_US + (int)((STOP_US - MIN_US) * (percent / 100.0));
    }
}

bool propulsion_init(int left_gpio, int right_gpio) {
    g_left_gpio = left_gpio;
    g_right_gpio = right_gpio;

    if (gpioInitialise() < 0) {
        std::printf("pigpio init failed\n");
        return false;
    }

    gpioSetMode(g_left_gpio, PI_OUTPUT);
    gpioSetMode(g_right_gpio, PI_OUTPUT);

    propulsion_stop();
    return true;
}

void propulsion_set(int left_percent, int right_percent) {
    left_percent  = clamp100(left_percent);
    right_percent = clamp100(right_percent);

    int left_us  = percent_to_us(left_percent);
    int right_us = percent_to_us(right_percent);

    gpioServo(g_left_gpio, left_us);
    gpioServo(g_right_gpio, right_us);
}

void propulsion_stop() {
    gpioServo(g_left_gpio, STOP_US);
    gpioServo(g_right_gpio, STOP_US);
}

void propulsion_forward(int percent) {
    percent = clamp100(percent);
    propulsion_set(percent, percent);
}

void propulsion_turn_left(int percent) {
    // left slower, right faster
    percent = clamp100(percent);
    propulsion_set(percent / 2, percent);
}

void propulsion_turn_right(int percent) {
    percent = clamp100(percent);
    propulsion_set(percent, percent / 2);
}

// ---------------- Example main ----------------
// Compile this file into an executable and run.
// WASD keyboard control for quick pool testing.
#ifdef BUILD_PROPULSION_MAIN
#include <termios.h>
#include <unistd.h>

static char getch_nonblock() {
    char buf = 0;
    termios old = {};
    if (tcgetattr(STDIN_FILENO, &old) < 0) return 0;
    termios nw = old;
    nw.c_lflag &= ~ICANON;
    nw.c_lflag &= ~ECHO;
    nw.c_cc[VMIN] = 0;
    nw.c_cc[VTIME] = 0;
    tcsetattr(STDIN_FILENO, TCSANOW, &nw);
    read(STDIN_FILENO, &buf, 1);
    tcsetattr(STDIN_FILENO, TCSANOW, &old);
    return buf;
}

int main() {
    if (!propulsion_init(18, 19)) return 1;
    std::printf("Propulsion ready. Use W/A/S/D, space=stop, Q=quit\n");

    int base = 0;

    while (true) {
        char c = getch_nonblock();
        if (c == 0) { usleep(20000); continue; }

        if (c == 'q' || c == 'Q') break;
        if (c == ' ') { base = 0; propulsion_stop(); continue; }

        if (c == 'w' || c == 'W') base = clamp100(base + 10);
        if (c == 's' || c == 'S') base = clamp100(base - 10);

        if (c == 'a' || c == 'A') propulsion_turn_left(base);
        else if (c == 'd' || c == 'D') propulsion_turn_right(base);
        else propulsion_forward(base);

        std::printf("Thrust: %d%%\n", base);
    }

    propulsion_stop();
    gpioTerminate();
    return 0;
}
#endif
