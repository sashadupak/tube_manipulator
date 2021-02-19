/* Sweep
 by BARRAGAN <http://barraganstudio.com>
 This example code is in the public domain.

 modified 8 Nov 2013
 by Scott Fitzgerald
 http://www.arduino.cc/en/Tutorial/Sweep
*/

#include <Servo.h>

Servo myservo;  // create servo object to control a servo
// twelve servo objects can be created on most boards

int pos = 0;    // variable to store the servo position

void setup() {
  myservo.attach(3);  // attaches the servo on pin 9 to the servo object
}

void loop() {
  delay(3000);

  // init servo
  myservo.write(93+10); // close_claws
  delay(700);
  myservo.write(93-10); // open claws
  delay(250);
  myservo.write(93); // stop
  
  delay(1000);

  // unscrew test tube cap
  myservo.write(93-40); // ccw rotation
  delay(1000);
  myservo.write(93); // stop

  delay(1000);

  // open claws after ccw rotation
  myservo.write(93+10); // open claws
  delay(250);
  myservo.write(93); //stop
  
  delay(2000);

  // pick test tube cap
  myservo.write(93+10); //close
  delay(300);
  myservo.write(93); //stop

  delay(1000);

  // screw test tube cap
  myservo.write(93+40); // cw rotation
  delay(1000);
  myservo.write(93); //stop

  // open claws after cw rotation
  myservo.write(93-10); // open claws
  delay(250);
  myservo.write(93); //stop

  //92 - 95 deg - stop
}
