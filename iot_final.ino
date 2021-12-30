#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <WiFiClient.h>


const char ssid[] = "One";
const char password[] = "12345678";

String recog_server;
const char status_server[] = "http://fflounge.000webhostapp.com/iot/handler.php?action=get";

volatile  int indx=0;

short post_code, get_code;

volatile bool speech=false;

uint8_t audio_buff[24100];

unsigned long time1=4000;

byte states[]={0,0,0};
byte pins[]={12,13,14};

WiFiClient client;
HTTPClient http;

void ICACHE_RAM_ATTR write_buff(){
  timer1_write(625);
  if(indx<24000){
    uint8_t mic_val=system_adc_read()/4;
    
    audio_buff[indx]=mic_val;
    indx++;
    if(!speech && (mic_val>150 || mic_val<120)){
      speech=true;  
    }
  }
}

void change_state(const char* resp, byte idx){
  for(byte i=idx;i<idx+3;i++){
    if (states[i]!=resp[i]-'0'){
      states[i]=resp[i]-'0';
      digitalWrite(pins[i], states[i]);
    }
  }
}

void setup() {
  pinMode(A0,INPUT);
  pinMode(2, 1);
  
  Serial.begin(115200);

  WiFi.begin(ssid, password);
  HTTPClient http;
  
  while(WiFi.status() != WL_CONNECTED){
    delay(200);
    if (digitalRead(2)){
      digitalWrite(2, 0);
    }
    else{
      digitalWrite(2, 1);
    }
  }  
  
  Serial.println("\n"+WiFi.localIP().toString());
  
  http.begin(client,"http://fflounge.000webhostapp.com/iot/handler.php?action=ip");
  while(http.GET()!=200){
    Serial.println("getting server ip...");
  }  
  recog_server=http.getString();
  http.end();
  Serial.println(recog_server);
  
  http.begin(client,recog_server);
  Serial.println(http.GET());
  http.end();
  
  for(byte i=0;i<3;i++){
    pinMode(pins[i], 1);
  }
  
  time1=millis();
  
  timer1_attachInterrupt(write_buff);
  timer1_enable(TIM_DIV16, TIM_EDGE, TIM_SINGLE);
  timer1_write(625);
}

void loop() { 
  if(WiFi.status() == WL_CONNECTED){
   if (millis()-time1>=2700){
    
    digitalWrite(2, 0);

    if(speech){
     
     Serial.print("sending audio\npost_code: ");
      
      http.begin(client, recog_server);
      
      http.addHeader("Content-Type", "text/plain");
      post_code = http.POST(audio_buff,indx);
      const char* resp=http.getString().c_str();
      
      if(post_code>0 && post_code<400){
           
        switch(resp[0]-'0'){
          case 5: change_state(resp,1);
                  Serial.println("hi there");
                  break;
                  
          case 9: change_state(resp,1);
                  Serial.println("error. (values kept same)");
                  break;
          
          default:change_state(resp,0);
                  Serial.println(resp);
        }
      }
      else{
       Serial.println(post_code);
       Serial.println(indx);       
      }
      
      http.end();
      
    }
    
    if(post_code<=0 || post_code>=400){
      
      http.begin(client,recog_server);
      
      Serial.println("sending get req ");
      
      get_code=http.GET();
      
      if (get_code>0 && get_code<400){
        const char* resp= http.getString().c_str();
        change_state(resp,0);       
      }
      else{
        Serial.print("get_code: ");
        Serial.println(get_code);
      }
      
      http.end();
    }
    speech=false;
    digitalWrite(2, 1);
    indx=0;
    post_code=-1;
    time1=millis();
    
  }
 }
  else{
    ESP.restart();
  }
}
    
