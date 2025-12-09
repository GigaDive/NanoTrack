#pragma once
#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>
#include "helper_3dmath.h"

struct IMU6050_full
{
    sensors_event_t accel, gyro, temp;
};
struct IMU6050_DMP
{
    Quaternion q;
    float ypr[3];
    float temp;
    VectorInt16 accel_without_gravity; // [x, y, z]            gravity-free accel sensor measurements
    VectorInt16 accel_with_gravity;    // [x, y, z]              world-frame accel sensor measurements
    int32_t wifi_rssi;
    long sequence_number;
};
