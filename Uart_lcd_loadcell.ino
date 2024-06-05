//Arduino Digital Weight Scale HX711 Load Cell Module
#include <HX711_ADC.h> // https://github.com/olkal/HX711_ADC
#include <Wire.h>
#include <LiquidCrystal_I2C.h> // LiquidCrystal_I2C library
HX711_ADC LoadCell(4, 5); // dt pin, sck pin
LiquidCrystal_I2C lcd(0x27, 16, 2); // LCD HEX address 0x27
int taree = 6;
int a = 0;
float b = 0;
int bytesSent = 0;

///*Test ổn định đọc
const int numReadings = 10;  // Số lần đọc để tính trung bình
const float stabilityThreshold = 0.05;  // Ngưỡng ổn định giữa các giá trị đọc

float readings[numReadings];     // Mảng lưu trữ giá trị đọc
int currentIndex = 0;          // Chỉ số hiện tại trong mảng readings

///

int readWeight() {
  // Đọc giá trị từ load cell
  float weightTemp = LoadCell.getData(); 
  
  // Chèn giá trị đọc mới vào mảng readings
  readings[currentIndex] = weightTemp;
  
  // Tăng chỉ số hiện tại, quay trở lại 0 nếu vượt quá kích thước mảng
  currentIndex++;
  if (currentIndex >= numReadings) {
    currentIndex = 0;
  }
  
  // Tính trung bình của các giá trị đọc
  float average = 0;
  for (int i = 0; i < numReadings; i++) {
    average += readings[i];
  }
  average /= numReadings;
//  Serial.println("Gia tri trung binh la: ");
//  Serial.println(average); ///*/
  return average;
}

bool isStable(float weight) {
  // Kiểm tra xem giá trị đọc đã ổn định hay chưa
  for (int i = 0; i < numReadings; i++) {
    if (abs(weight - readings[i]) > stabilityThreshold) {
//      Serial.println("false"); ///*/
      return false;
    }
  }
//  Serial.println("true"); ///*
  return true;
}


///*

///

void sendData(float weight) {
  while (bytesSent == 0) {
    String strWeight = String(weight);
//    Serial.println("Can nang la: ");
    bytesSent = Serial.println(strWeight);
//    Serial.println(bytesSent);
  }
}


void setup() {
  ////
  // Mở cổng Serial thông qua USB
  Serial.begin(9600);
  ////
  pinMode (taree, INPUT_PULLUP);
  LoadCell.begin(); // start connection to HX711
  LoadCell.start(1000); // load cells gets 1000ms of time to stabilize

  /////////////////////////////////////
  LoadCell.setCalFactor(125000); // Calibarate your LOAD CELL with 100g weight, and change the value according to readings
  /////////////////////////////////////

  lcd.init(); // begins connection to the LCD module
  lcd.backlight(); // turns on the backlight
  lcd.setCursor(1, 0); // set cursor to first row
  lcd.print("Digital Scale "); // print out to LCD
  lcd.setCursor(0, 1); // set cursor to first row
  lcd.print(" 5KG MAX LOAD "); // print out to LCD
  delay(3000);
  lcd.clear();
}
void loop() {
  lcd.setCursor(1, 0); // set cursor to first row
  lcd.print("Digital Scale "); // print out to LCD
  LoadCell.update(); // retrieves data from the load cell
  float i = LoadCell.getData(); // get output value
  if (i < 0)
  {
    i = i * (-1);
    lcd.setCursor(0, 1);
    lcd.print("-");
    lcd.setCursor(8, 1);
    lcd.print("-");
  }
  else
  {
    lcd.setCursor(0, 1);
    lcd.print(" ");
    lcd.setCursor(8, 1);
    lcd.print(" ");
  }

  lcd.setCursor(1, 1); // set cursor to secon row
  lcd.print(i, 1); // print out the retrieved value to the second row
  lcd.print("Kg ");
  float z = i / 28.3495;
  lcd.setCursor(9, 1);
  lcd.print(z, 2);
  lcd.print("oz ");

  if (i >= 5000)
  {
    i = 0;
    lcd.setCursor(0, 0); // set cursor to secon row
    lcd.print("  Over Loaded   ");
    delay(200);
  }
  if (digitalRead (taree) == LOW)
  {
    lcd.setCursor(0, 1); // set cursor to secon row
    lcd.print("   Taring...    ");
    LoadCell.start(1000);
    lcd.setCursor(0, 1);
    lcd.print("                ");
  }

  ///*
//  float weight = readWeight();
  float weight = LoadCell.getData();
  readWeight();
  // Kiểm tra tính ổn định của giá trị đọc
  if (isStable(weight)) {
    if(weight > 0.1){
      bytesSent = 0;
      sendData(weight);
    }
  }
  ///*

  
//  if (i > 0.1)
//  {
//    if (i == LoadCell.getData())
//    {
//      bytesSent = 0;
//      sendData(i);
//    }
//  }
}
