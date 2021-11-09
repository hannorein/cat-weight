
#include <Servo.h>
#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <WiFiClient.h>
#include "HX711.h"

Servo servo;
HX711 scale;

float weight = 0.; // averaged
float weight_current = 0;
float weight_while_open = 0.;
float decay = 0.3;

float weight_min = 4;
float weight_max = 6;

int food = 0; // 0 closed
              // 1 opening
              // 2 open
              // 3 closing

const int  angle_closed = 6;
const int angle_open = 126;  
const int motor_speed = 1;          
int angle = 0;
long counter = 0;
long counter_while_open = 0;
long error_counter = 0;
float zero = 0;
float kg = 21000; // calibration

#include "wifisecrets.h"

void setup() {
  WiFi.begin(ssid, password);
 
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.print("Connecting..");
  }

  pinMode(15, INPUT); // manual overwrite input pin
  
  food = 1;
  
  // put your setup code here, to run once:
  Serial.begin(9600);
  Serial.println("\n\nHello World\n\n");
  scale.begin(0, 2); // clock = 2 = D4
  zero = scale.get_value(20);
  //scale.set_scale();  
  //scale.tare();  
  servo.attach(4);
  servo.write(angle_closed);
}


void send_data(char* url){
  if(WiFi.status()== WL_CONNECTED){
    WiFiClient client;
    HTTPClient http;
    
    http.setTimeout(500); // milli seconds
    // Your Domain name with URL path or IP address with path
    http.begin(client, url);
    
    // Send HTTP GET request
    int httpResponseCode = http.GET();
    
    if (httpResponseCode>0) {
      Serial.print("HTTP Response code: ");
      Serial.println(httpResponseCode);
      String payload = http.getString();
      Serial.println(payload);
    } else {
      Serial.print("Error code: ");
      Serial.println(httpResponseCode);
      error_counter++;
    }
    // Free resources
    http.end();
  }else{
    error_counter ++;
  }
}


void loop() {
  counter ++;

  int overwrite = digitalRead(15); // manual overwrite input pin
  if (overwrite==1 && food==0){
    food = 1;
  }

  if (error_counter >10){
    ESP.restart();
  }
  
  if (food == 0 || food == 2){
    if (scale.wait_ready_timeout(10)) {
      weight_current = (scale.get_value(2)-zero)/kg;
      weight = weight_current*decay + (1.-decay)*weight;
    }
    if (counter%8==0){
      Serial.print("HX711:");
      Serial.println(weight);
    }
  }

  if (food == 0 && counter>10000){
    counter = 0;
    if (weight<0.1*weight_min && overwrite==0){
      zero = scale.get_value(10);
      Serial.print("Tare");
      char url[512];
      sprintf(url,"http://74.208.244.193:8076/push?weight=%.5f&zero=%.5f",weight,zero);
      send_data(url);
    }
  }

  if (food==0 && weight>weight_min && weight<weight_max){
    food = 1;
  }

  if (food == 1){
    counter = 0;
    angle += motor_speed;
    servo.write(angle);
    if (angle>=angle_open){
      food = 2;
      counter_while_open = 0;
      weight_while_open = 0;
    }
  }

  if (food==2){
    counter_while_open++;
    if (counter_while_open>50){
      weight_while_open += weight_current;
      if (counter_while_open==150 && overwrite==0){
        char url[512];
        sprintf(url,"http://74.208.244.193:8076/push?weight=%.5f&zero=%.5f",weight_while_open/100,zero);
        send_data(url);
      }
    }
  }

  if (food==2 && (weight<0.9*weight_min || weight>weight_max) && overwrite==0 ){
    food = 3;
  }

  if (food == 3){
    counter = 0;
    angle -= motor_speed;
    servo.write(angle);
    if (angle<=angle_closed){
      food = 0;
    }
  }

    
  

  delay(  5);
}
