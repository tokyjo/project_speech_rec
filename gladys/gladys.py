from vosk import Model, KaldiRecognizer
from pydub import AudioSegment
from gtts import gTTS
import pyaudio
import pyttsx3  
import requests
import json
import wave
import os 
import alsa_error as a


FORMAT = pyaudio.paInt16
CHANNELS = 1
SAMPLING_RATE= 44104
FRAME_PER_BUFFER =8820 #chunk
DEVICE_INDEX= -1

NB_QUESTION= 3

model_path="/home/unravel/IoT/project/vosk-model-small-fr-pguyot-0.3"
#model_path="/home/username/project_IoT/vosk-model-small-fr-pguyot-0.3"
quest_url="http://127.0.0.1:5000"

FOLDER_Q = "/home/unravel/IoT/project/gladys/questions/"
FOLDER_A= "/home/unravel/IoT/project/gladys/responses/"
#FOLDER_Q = "/home/username/project_IoT/gladys/questions/"
#FOLDER_A= "/home/username/project_IoT/gladys/responses/"


class _GTTS():
    engine=None
    def __init__(self,mytext,path):
        self.path = path
        self.engine = gTTS(text=mytext, lang='fr', slow=False)
        self.engine.save(path)
        
    def save(self):
        dist=self.path[:-4]+".wav"
        print(dist)
        sound = AudioSegment.from_mp3(self.path)
        self.path=dist
        sound.export(dist,format="wav")
    
    def speak(self): 
        print("path audio: ",self.path)   
        #os.system("aplay -D 'plughw:2,0' "+self.path) 
        os.system("aplay "+self.path)      


class _Audiofile():
    chunk=1024

    def __init__(self):
        self.wf=None    
        self.mic = pyaudio.PyAudio()
        
    def play(self,file):
        self.wf=wave.open(file,'rb')
        self.stream = self.mic.open(
            format = self.mic.get_format_from_width(self.wf.getsampwidth()),
            channels = self.wf.getnchannels(),
            rate = self.wf.getframerate(),
            output = True,
            output_device_index=DEVICE_INDEX
        )

        data = self.wf.readframes(self.chunk)
        while data != b'':
            self.stream.write(data)
            data = self.wf.readframes(self.chunk)

    def stop(self):
        self.stream.close()
        self.mic.terminate()

    def record(self,file):
        seconds =5
        frames=[]
        self.stream= self.mic.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=SAMPLING_RATE,
            input=True,
            frames_per_buffer=FRAME_PER_BUFFER,
            input_device_index=DEVICE_INDEX
        )
        print("recording")
        for i in range (0,int(SAMPLING_RATE/FRAME_PER_BUFFER*seconds)):
            data=self.stream.read(FRAME_PER_BUFFER)
            frames.append(data)
        
        self.stream.stop_stream()
        self.stop()

        obj=wave.open(file, "wb")
        obj.setnchannels(CHANNELS)
        obj.setsampwidth(self.mic.get_sample_size(FORMAT))
        obj.setframerate(SAMPLING_RATE)
        obj.writeframes(b"".join(frames))
        obj.close
        print("recording done")


class Gladys():
    def __init__(self):
        ## init vosk
        self.model = Model(lang='fr')
        self.recognizer = KaldiRecognizer(self.model,SAMPLING_RATE) #frequency which should be checked 
        self.recognizer.SetWords(True)

        ##init pyAudio
        self.listening = False
        self.rec =False
        #request
        self.count=0
        self.questions={}
        self.responses=[]  

    def get_questions(self,url):
        req = requests.get(url)
        jsonobj= json.loads(req.text)
        self.questions=jsonobj["questions"]
        

    def get_audio(self,url):
        audio_file=FOLDER_Q+"question_"+str(self.count)+".wav"
        with open(audio_file, 'wb') as a:
            resp = requests.get(url)
            if resp.status_code == 200:
                a.write(resp.content)
                print('downloaded')
            else:
                print(resp.reason)
                exit(1)
        self.play_audio(audio_file)
        

    def play_audio(self,file):
        Au=_Audiofile(file)
        Au.play()
        Au.stop()
        
    def get_response(self):
        self.listening= True
        Au=_Audiofile()
        Au.stream = Au.mic.open(format=FORMAT,channels=CHANNELS,rate=SAMPLING_RATE,input=True,frames_per_buffer=FRAME_PER_BUFFER)
        print("start recording")
        while self.listening:
            Au.stream.start_stream()
            try:
                data= Au.stream.read(4410)
                if self.recognizer.AcceptWaveform(data):
                    result = self.recognizer.Result()
                    response = result[14:-3] # split dictionnary and get the string
                    Au.stream.close()
                    print('reponse : ', response)
                    print("stop recording")
                    if response !='exprimer':
                        self.responses.append(response)
                    else: 
                        self.rec=True
                    return response
            except OSError:
                pass

    def response_tts(self):
        dict={}
        for i in range(NB_QUESTION):
            path=FOLDER_A+"response_"+str(i)+".wav"
            wf=wave.open(path,'rb')
            while True:
                data =wf.readframes(44104)
                if len(data)==0:
                    break
                
                if self.recognizer.AcceptWaveform(data):
                    print("Result:")
                    result = self.recognizer.Result()
                    dict=json.loads(result)
                    self.responses.append(dict.get("text"))

            dict=json.loads(self.recognizer.FinalResult())
            print("dict=",dict)
            if dict["text"]!='':
                self.responses.append(dict.get("text"))
            print(self.responses)

        self.send_responses()

    # def test_response_tts(self):
       
    #     path="/home/unravel/Downloads/fable.wav"
    #     wf=wave.open(path,'rb')
    #     while True:
    #         data =wf.readframes(44100)
    #         if len(data)==0:
    #             break
    #         if self.recognizer.AcceptWaveform(data):
    #             print("Result:")
    #             result = self.recognizer.Result()
    #             dict=json.loads(result)
    #             self.responses.append(dict.get("text"))

    #     dict=json.loads(self.recognizer.FinalResult())
    #     self.responses.append(dict.get("text"))

    #     print (self.responses)
    #    #self.send_responses()

    def play_question_gtts(self):
        path=FOLDER_Q+"question_"+str(self.count)+".mp3"
        gtts = _GTTS(self.questions[self.count],path)
        gtts.save()
        print("speak")
        gtts.speak()
        del(gtts)

    def record_audio(self):
        Au=_Audiofile()
        path_file=FOLDER_A+"response_"+str(self.count)+".wav"
        Au.record(path_file)

    def send_responses(self):
        data = {}
        data["responses"]=self.responses
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        req = requests.post(quest_url,data=json.dumps(data),headers=headers)
    
    def send_audio(self):
        audiofile=FOLDER_A+"response_"+str(self.count)+".wav"
        url=quest_url+"/audio/"+str(self.count)
        files = {'file': open(audiofile, 'rb')}
        req=requests.post(url, files=files)
        print(req.text)


def routine():
    gladys=Gladys()
    print("fetch questions from server")
    gladys.get_questions(quest_url)
    for i in range (NB_QUESTION):
        gladys.play_questions()
        gladys.get_response()
        if gladys.rec:
            gladys.record_audio()
        gladys.count+=1
    gladys.send_responses()

def routine_2():    
        gladys=Gladys()
        print("fetch questions audio from server")
        gladys.get_questions(quest_url)
        for i in range (NB_QUESTION):
            gladys.play_question_gtts()
            gladys.record_audio()
            gladys.count+=1

        print("session finished")
        print("now... uploading response to server")    
        gladys.count =0
        for i in range(NB_QUESTION):
            gladys.send_audio() 
            gladys.count +=1   
        gladys.response_tts()


if __name__=='__main__':
    with a.noalsaerr():
        #routine_2()
        gladys=Gladys()
        gladys.response_tts()
        
    

        

    
"""
"RATE" is the "sampling rate", i.e. the number of frames per second
"CHUNK" is the (arbitrarily chosen) number of frames the (potentially very long) signals are split into in this example
each frame will have 2 samples as "CHANNELS=2", but the term "samples" is seldom used in this context (because it is confusing)
size of each sample is 2 bytes (= 16 bits) in this example
size of each frame is 4 bytes
each element of "frames" should be 4096 bytes. sys.getsizeof() reports the storage space 
needed by the Python interpreter, which is typically a bit more than the actual size of the raw data.

RATE * RECORD_SECONDS is the number of frames that should be recorded. 
Since the for loop is not repeated for each frame but only for each chunk, the number of loops has to be divided by the chunk size CHUNK.
"""
