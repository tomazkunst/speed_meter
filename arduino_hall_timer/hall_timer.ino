int SENSOR = 8;
int SENSOR1 = 7;
int SENSOR2 = 4;
int Led = 13 ;
unsigned long old_time;
unsigned long new_time;
unsigned long old_time1;
unsigned long new_time1;
unsigned long old_time2;
unsigned long new_time2;

unsigned long period = 0;
int val;
int prev;
int val1;
int prev1;
int val2;
int prev2;

void setup()
{
   Serial.begin(9600);
   pinMode (SENSOR, INPUT);
   pinMode (SENSOR1, INPUT);
   pinMode (SENSOR2, INPUT);
   pinMode (Led, OUTPUT) ;
   old_time = millis();
   old_time1 = millis();
   old_time2 = millis();
}

void loop()
{
   digitalWrite (Led, LOW);
   val = digitalRead (SENSOR);
   val1 = digitalRead (SENSOR1);
   val2 = digitalRead (SENSOR2);
   if (val == LOW && prev == HIGH)
   {
     new_time = millis();
     Serial.println("1:" + String(new_time - old_time));
     old_time = new_time;
     digitalWrite (Led, HIGH);
     delay(1);
   }
   prev = val;
   if (val1 == LOW && prev1 == HIGH)
   {
     new_time1 = millis();
     Serial.println("2:" + String(new_time1 - old_time1));
     old_time1 = new_time1;
     digitalWrite (Led, HIGH);
     delay(1);
   }
   prev1 = val1;
   if (val2 == LOW && prev2 == HIGH)
   {
     new_time2 = millis();
     Serial.println("3:" + String(new_time2 - old_time2));
     old_time2 = new_time2;
     digitalWrite (Led, HIGH);
     delay(1);
   }
   prev2 = val2;
}
