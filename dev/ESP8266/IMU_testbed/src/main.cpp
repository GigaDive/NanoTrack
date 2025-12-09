#include <Arduino.h>
#include <ESP8266WiFi.h> // Include the Wi-Fi library
#include <WiFiUdp.h>
#include "credentials.h"
#include <Wire.h>
#include "global_types.h"
#include "mpu6050_simple.h"
#include "mpu6050_dmp.h"

unsigned int UDP_PORT = 1330;
unsigned int UDP_REMOTE = 4210;
WiFiUDP UDP;
IMU6050_full IMU6050_Measurement;
IMU6050_DMP IMU6050_dmp;
unsigned long timer = millis();
int32_t loopCounter = 0;
char packet[255];
char reply[400];
// IPAddress remoteIP(192,168,0,121);
const char *remoteIP = "192.168.0.121";
void setup()
{
  Serial.begin(115200); // Start the Serial communication to send messages to the computer
  delay(10);
  Serial.println('\n');

  WiFi.begin(ssid, password); // Connect to the network
  Serial.print("Connecting to ");
  Serial.print(ssid);
  Serial.println(" ...");

  int i = 0;
  while (WiFi.status() != WL_CONNECTED)
  { // Wait for the Wi-Fi to connect
    delay(1000);
    Serial.print(++i);
    Serial.print(' ');
  }

  Serial.println('\n');
  Serial.println("Connection established!");
  Serial.print("IP address:\t");
  Serial.println(WiFi.localIP()); // Send the IP address of the ESP8266 to the computer

  UDP.begin(UDP_PORT);
  Serial.print("Listening on UDP port ");
  Serial.println(UDP_PORT);
  // init_mpu6050();
  mpu6050_dmp_setup();
  IMU6050_dmp.sequence_number = 0;
}

void loop()
{
  if (millis() > timer + 1000)
  {
    Serial.print("Loop/s:   ");
    Serial.println(loopCounter);
    loopCounter = 0;
    timer = millis();
  }
  // loop_mpu6050(&IMU6050_Measurement);
  mpu6050_dmp_loop(&IMU6050_dmp);
  IMU6050_dmp.wifi_rssi = WiFi.RSSI();
  // sprintf(reply, "%f,%f,%f,%f,%f,%f,%f",
  // IMU6050_Measurement.accel.acceleration.x,
  // IMU6050_Measurement.accel.acceleration.y,
  // IMU6050_Measurement.accel.acceleration.z,
  // IMU6050_Measurement.gyro.gyro.x,
  // IMU6050_Measurement.gyro.gyro.y,
  // IMU6050_Measurement.gyro.gyro.z,
  // IMU6050_Measurement.temp.temperature
  // );
  // sprintf(reply, "Quaternions: %f,%f,%f,%f\nYPR:%f,%f,%f\nACCEL_WORLD:%d,%d,%d\nACCEL_REAL:%d,%d,%d\nTEMP: %f RSSI: %d SQN:%ld\n",
  sprintf(reply, "%f,%f,%f,%f,%f,%f,%f,%d,%d,%d,%d,%d,%d,%f,%d,%ld\n",
          IMU6050_dmp.q.w,
          IMU6050_dmp.q.x,
          IMU6050_dmp.q.y,
          IMU6050_dmp.q.z,
          IMU6050_dmp.ypr[0],
          IMU6050_dmp.ypr[1],
          IMU6050_dmp.ypr[2],
          IMU6050_dmp.accel_with_gravity.x,
          IMU6050_dmp.accel_with_gravity.y,
          IMU6050_dmp.accel_with_gravity.z,
          IMU6050_dmp.accel_without_gravity.x,
          IMU6050_dmp.accel_without_gravity.y,
          IMU6050_dmp.accel_without_gravity.z,
          IMU6050_dmp.temp,
          IMU6050_dmp.wifi_rssi,
          IMU6050_dmp.sequence_number);
  UDP.beginPacket(remoteIP, UDP_REMOTE);
  UDP.write(reply, sizeof(reply));
  UDP.endPacket();
  IMU6050_dmp.sequence_number = IMU6050_dmp.sequence_number + 1;
  loopCounter++;

}