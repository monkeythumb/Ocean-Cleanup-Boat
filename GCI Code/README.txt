Install library:
sudo apt-get update
sudo apt-get install pigpio
sudo systemctl enable pigpiod
sudo systemctl start pigpiod


compile:
g++ -DBUILD_PROPULSION_MAIN pi_propulsion.cpp -o propulsion_test -lpigpio -lrt -lpthread

Run:
sudo ./propulsion_test

Controls while running
Press keys:
W = faster forward
S = slower / reverse
A = turn left
D = turn right
Space = stop
Q = quit