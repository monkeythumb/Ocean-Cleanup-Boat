Ocean Cleanup Boat — GCI 200 Project

Isha Ali, Marc Arnault, Matt Barnes, Farida Khalifa, Emily Stringfellow

This project develops a small-scale, solar-powered trash-collecting boat designed for closed water sources (lakes, dams, reservoirs). The vessel is intended to detect floating debris, move toward it, lift it using a front conveyor belt, and store it in a rear net. This semester’s deliverables include finalized control code and a working simulation; physical building and pool testing will begin in GCI 250 once delayed materials arrive.

System Overview:
- Conveyor (Pico W): A continuous-rotation servo drives a belt that carries trash from the bow intake into rear storage.
- Propulsion (Raspberry Pi): Differential thrust using two servo-fan thrusters for forward motion and steering.
- Power: 12 V solar panels charging a buffer battery, with regulated rails for compute and actuation.
- Sensors (planned/optional): Distance sensors for basic debris/obstacle detection.

Repository Layout:
  ocean-cleanup-boat/
  ├── pico_conveyor/ # Conveyor servo PWM code (Pico W)
  ├── pi_propulsion/ # Propulsion/thrust code (Raspberry Pi)
  ├── simulation/ # Ocean cleanup simulation (Python/pygame)
  ├── docs/ # Metadata, wiring diagrams, timeline
  └── media/ # Renders and test media

Hardware Assumptions:
- Conveyor controller: Raspberry Pi Pico W
- Servo signal on GP15 (configurable in code).
- Propulsion controller: Raspberry Pi (Linux)
- Left thrust signal GPIO18, right thrust signal GPIO19.

Actuators: Continuous-rotation servos / servo-fan thrusters.
Power: Servos are powered from a dedicated rail (not from Pi/Pico pins). Grounds are shared across all subsystems.

Running the Code:
  Conveyor (Pico W):
    - Build with the Raspberry Pi Pico SDK.
    - Flash the compiled UF2 to the Pico W.

  In main.c, call:
    conveyor_servo_init(15);
    conveyor_servo_forward(60);

Propulsion (Raspberry Pi)
Install dependency:
  sudo apt-get update
  sudo apt-get install pigpio
  sudo systemctl enable pigpiod
  sudo systemctl start pigpiod

Compile:
  g++ -DBUILD_PROPULSION_MAIN pi_propulsion.cpp -o propulsion_test -lpigpio -lrt -lpthread

Run:
  sudo ./propulsion_test

Controls while running:
  W/S = increase/decrease thrust (forward/reverse)
  A/D = turn left/right
  Space = stop
  Q = quit
Equal thrust on both sides drives straight; unequal thrust produces turning.

Hardware and Code Status:
  Our hardware plan uses a single Raspberry Pi Pico W microcontroller with a supporting circuit/driver board. All control code in this repository is written for the Pico W and is complete and ready to use once our delayed components arrive. Because the physical prototype was not assembled this semester, the code has not yet been tested on water; next term will focus on printing, assembly, and calibration (servo neutral values, belt speed, and thrust balance).

---------------------------------------------------------------------------------------------------------------

Ocean Cleanup Simulation:

This simulation models a simplified trash-collection scenario to support the physical boat design. It uses a 2D pygame environment to represent a trash field and an autonomous collection vessel powered by solar energy. The simulation estimates collection rate, distance traveled, energy generated, energy consumed, and battery state over repeated “days.”

What the Simulation Does:
- Spawns a fixed number of floating trash objects in a bounded water area.
- Moves the boat toward the closest trash until storage capacity is full.
- Tracks daily distance traveled (pixels → meters → km).
- Models battery drain based on distance traveled.
- Models solar charging with a day/night cycle where solar output varies over time.
- Ends each day with a performance summary screen.
- Key Parameters (editable in script)
- DAY_DURATION_SECONDS — length of one simulated day.
- BATTERY_CAPACITY_KWH — maximum battery energy.
- ENERGY_PER_KM_KWH — energy used per kilometer traveled.
- SOLAR_MAX_POWER_KW — peak solar charging power.
- max_trash_capacity — boat storage limit per day.
- boat_speed_pixels_per_sec — boat movement speed.

How to Run:
  Install pygame:
    pip install pygame
  Run the simulation:
    python ocean_cleanup_sim.py

Outputs Shown On-Screen:
- Trash collected per day
- Distance traveled (km)
- Solar energy generated (kWh)
- Energy consumed (kWh)
- Battery remaining (%)
- Time to full trash capacity (if reached)
- These outputs support expectations for real-world performance, especially how solar charging and travel energy use affect collection efficiency.

