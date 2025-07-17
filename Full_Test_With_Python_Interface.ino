const int dirPin1 = 2;   // Left
const int stepPin1 = 3;  
const int dirPin2 = 10;  // Bottom
const int stepPin2 = 11;
const int dirPin3 = 4;   // Front
const int stepPin3 = 5;
const int dirPin4 = 6;   // Right
const int stepPin4 = 7;
const int dirPin5 = 8;   // Back
const int stepPin5 = 9;
const int dirPin6 = 12;  // Top
const int stepPin6 = 13;

const int enablePin = A0;  // EN pin for TMC drivers

const int stepsPerRev = 1600; // 1 rev 1600
const int ultraFastDelay = 50; // Delayed time before spinning

void setup() {
  Serial.begin(9600);
  while (!Serial) {}

  Serial.setTimeout(2000);

  for (int i = 2; i <= 13; i++) {
    pinMode(i, OUTPUT);
    digitalWrite(i, LOW);
  }

  pinMode(enablePin, OUTPUT);
  digitalWrite(enablePin, HIGH);  // Disable motors first to prevent jiggling

  Serial.println("Waiting for cube string from Python...");
}

void loop() {
  if (Serial.available() > 0) {
    String cubeString = Serial.readStringUntil('\n');
    cubeString.trim();

    Serial.print("Received cube string length: ");
    Serial.println(cubeString.length());
    Serial.print("Received cube string: ");
    Serial.println(cubeString);

    if (cubeString.length() != 54) {
      Serial.println("Error: Cube string length not 54, please resend.");
      return; 
    }

    Serial.println("Cube string received:");
    Serial.println(cubeString);

    // Send ready for moves signal and flush immediately
    Serial.println("Waiting for moves from Python...");
    Serial.flush();

    // Wait for moves string
    while (Serial.available() == 0) {}

    String moves = Serial.readStringUntil('\n');
    moves.trim();

    Serial.print("Received moves: ");
    Serial.println(moves);

    digitalWrite(enablePin, LOW);  // Enable motors
    executeMoves(moves);
    digitalWrite(enablePin, HIGH); // Disable motors after solving

    Serial.println("Cube solved!");
  }
}

void executeMoves(String moves) {
  for (unsigned int i = 0; i < moves.length(); i++) {
    char move = moves[i];
    bool dir = HIGH;
    int steps = stepsPerRev / 4; // 90°

    if (move == ' ') continue;

    if (isLowerCase(move)) { dir = LOW; move = toupper(move); }

    switch (move) {
      case 'U': rotateMotor(stepPin6, dirPin6, dir, steps); break;
      case 'D': rotateMotor(stepPin2, dirPin2, dir, steps); break;
      case 'L': rotateMotor(stepPin1, dirPin1, dir, steps); break;
      case 'R': rotateMotor(stepPin4, dirPin4, dir, steps); break;
      case 'F': rotateMotor(stepPin3, dirPin3, dir, steps); break;
      case 'B': rotateMotor(stepPin5, dirPin5, dir, steps); break;
    }
    delay(ultraFastDelay);
  }
}

void rotateMotor(int stepPin, int dirPin, bool direction, int steps) {
  digitalWrite(dirPin, direction);
  delayMicroseconds(10);

  int pulseWidth = 100; //Speed of motors
  for (int i = 0; i < steps; i++) {
    digitalWrite(stepPin, HIGH);
    delayMicroseconds(pulseWidth);
    digitalWrite(stepPin, LOW);
    delayMicroseconds(pulseWidth);
  }
}

bool isLowerCase(char c) {
  return (c >= 'a' && c <= 'z');
}
