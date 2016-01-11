# imu_quad
Software to interface the Beaglebone Black (BBB) with the MPU-6050 3 axis accelerometer and gyro IMU. Data is collected from the IMU over I2C bus in raw quaternion format, converted to Euler angles and then sent over the network to a remote machine. Software is based on InvenSense Motion Driver Firmware examples found on I2CDevLib.

Connection MPU 6050
P9_40 - INT
P9_1 - GND
P9_3 - VCC
P9_19 - SCL
P9_20 - SDA
