#include <Adafruit_NeoPixel.h>
#include <ESP8266WiFi.h>
#include <ESPAsyncTCP.h>
#include <ESPAsyncWebServer.h>

//Network credentials

const char* ssid = "II";
const char* password = "gaastra6518";

// Create AsyncWebServer object on port 80
AsyncWebServer server(80);

#define PIN 4
#define NUMPIXELS 60

Adafruit_NeoPixel strip = Adafruit_NeoPixel(NUMPIXELS, PIN, NEO_GRB + NEO_KHZ800);

void setup() {
   strip.begin();
  // Serial port for debugging purposes
  Serial.begin(115200);

  // Connect to Wi-Fi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi..");
  }
  
 // Print ESP Local IP Address
  Serial.println(WiFi.localIP());

  /*
   * Set up the wifi server routing.
   * Colour API format:
   * <ip>/colour?r=[0,255]&g=[0,255]&b=[0,255]
   */

  //Listen for the /colour method
  server.on("/colour", HTTP_GET, [] (AsyncWebServerRequest *request){
    // We are handling a colour request
    // Extract the r,g, and b parameters
     String redInput = request->getParam("r")->value();
     String greenInput = request->getParam("g")->value();
     String blueInput = request->getParam("b")->value();
    // Then, update the led

    //Map to the analog (pwm) value
    
    int analog_r = redInput.toInt();
    int analog_g = greenInput.toInt();
    int analog_b = blueInput.toInt();


    /*
    int analog_r = redInput.toInt()*1023/255;
    int analog_g = greenInput.toInt()*1023/255;
    int analog_b = blueInput.toInt()*1023/255;
    */
    
   for(int i=0;i<NUMPIXELS;i++){
    strip.setPixelColor(i, strip.Color(analog_r,analog_g,analog_b));
    strip.show();
  }
  Serial.println("r: " + String(analog_r)+ "g: "+ String(analog_g) + "b: "+ String(analog_b));
  Serial.println(analog_g);
  request->send(200, "text/plain", "OK");
  });

   // Start server
  server.begin();
}


// the loop function runs over and over again forever
void loop() {

}
