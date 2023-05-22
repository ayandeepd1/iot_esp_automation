from http.server import SimpleHTTPRequestHandler, HTTPServer
from numpy.lib.shape_base import split
import requests
import io
from threading import Thread
import scipy.io.wavfile
import numpy
import speech_recognition as sr

r = sr.Recognizer()

stats=""

url_get="http://localhost/handler.php?action=" #fflounge.000webhostapp.com

my_data={"a":["a","ke","se","is","8","ace"], "b":["b", "be", "bi","bhi","bee","bii","bill"], "light":["light", "live", "like", "lights","flight","flights"], "fan":["fan", "fans", "san","sans","sam","phan","send","science", "pan"],"hello":["hello"]}

def update_stats(status):
    for each in status:
        post_resp=requests.post(url=url_get + each, data='{"password": "mypass"}')
        print(each+':'+post_resp.text)

def recog_familiar(text,resp):
    resp=bytearray(resp,"utf-8")
    words=text.split()
    result_val=[]#{"type":-1,"ind":""}
    for i in range(0, len(words)):

        if words[i] =="hello":
            return bytes(bytearray([53]) + resp)
        
        elif words[i] in my_data["light"]:
            try:
                if words[i+1] in my_data["a"] and 'l1' not in result_val:
                    result_val.append('l1')
                    i+=2
                elif words[i+1] in my_data["b"] and 'l2' not in result_val:
                    result_val.append('l2')
                    i+=2
            except IndexError:
                continue
       
        elif words[i] in my_data["fan"]:
            result_val.append('f1')
   

    understood=False
    for res in result_val:   
        if res=='l1':
            resp[0] = 49 if resp[0]==48 else 48
            understood=True
    
        elif res=='l2':
            resp[1] = 49 if resp[1]==48 else 48
            understood=True
    
        elif res=='f1':
            resp[2] = 49 if resp[2]==48 else 48
            understood=True
    
            
    if not understood:
        resp=bytearray([57]) + resp
    else:
        t=Thread(target=update_stats,args=[result_val])
        t.start()
        resp=bytearray([48]) + resp
    
    return bytes(resp)



class handler(SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type','text/html')
        self.end_headers()
        get_resp=requests.get(url_get+"get").text
        
        try:
            int(get_resp)
            get_resp = '0' + get_resp
            self.wfile.write(bytes(get_resp,"utf-8"))
        except:
            print("portal_error")
            self.wfile.write(bytes("8000","utf-8"))

        self.wfile.flush()
        print('\t' + get_resp)


    def do_POST(self):
        self.send_response(200)
        self.send_header('Content-type','text/plain')
        self.end_headers()
        audio_buff_len = int(self.headers.get_all('Content-length', 0)[0])
        audio_buff = self.rfile.read(audio_buff_len)
        print(audio_buff_len)
        if audio_buff_len>8000:
            audio_numpy = numpy.array( bytearray(audio_buff), dtype=numpy.int8)
            temp_wav=io.BytesIO()
            scipy.io.wavfile.write(temp_wav,8000,audio_numpy)

            get_resp=requests.get(url_get+"get").text

            try:
                int(get_resp)
            except:
                print("portal_error")
                self.wfile.write(bytes('8000',"utf-8"))
                self.wfile.flush()
                return
            
            print(get_resp)

            AUDIO_FILE = (temp_wav)
            with sr.AudioFile(AUDIO_FILE) as source:
                audio = r.record(source)  
            
            try:
                recog_text=r.recognize_google(audio,language="en-IN")#,key="AIzaSyD-ieh7ZwJFC9yD_ezoVT_XXWUQVZIyJ1w")
                print(recog_text,end="\t")
                
                recog_results=recog_familiar(str(recog_text).lower(), get_resp)
                print(recog_results)
                self.wfile.write(recog_results)
                self.wfile.flush()
                
            except:
                self.wfile.write(bytes('7' + get_resp,"utf-8"))
                self.wfile.flush()
                print("not_recognized")
                
        
                
with HTTPServer(('', 5901), handler) as server:
    server.serve_forever()
