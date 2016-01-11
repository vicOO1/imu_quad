# imu_quad
Software to interface the Beaglebone Black (BBB) with the MPU-6050 3 axis accelerometer and gyro IMU. Data is collected from the IMU over I2C bus in raw quaternion format, converted to Euler angles and then sent over the network to a remote machine. Software is based on InvenSense Motion Driver Firmware examples found on I2CDevLib
