from aip import AipSpeech
import pyaudio
import wave
#准备APPID，APIKEY，secretKey
APP_ID = "42409573"
API_KEY = "1GRXRCxc9SnEvy0m7WWuxG6F"
SECRET_KEY = "tggblfIeFzFQ3G5CRqL87ztWnRYbnIme"
client = AipSpeech(APP_ID,API_KEY,SECRET_KEY)

def speech_recognition(sec):
    #创建音频对象
    p=pyaudio.PyAudio()
    #创建音频流:采样位数，声道数，缓冲区大小，input=True
    stream=p.open(format=pyaudio.paInt16,channels=1,rate=16000,input=True,frames_per_buffer=1024)
    #创建打开音频文件
    wf=wave.open('test3.wav','wb')
    #设置音频文件属性:声道数，采样位，采样频率
    wf.setnchannels(1)
    wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
    wf.setframerate(16000)
    print('开始录音')
    for s in range(int(16000*sec/1024)):
        data = stream.read(1024)
        wf.writeframes(data)
    data = open('test3.wav', 'rb').read()
    result = client.asr(open('test3.wav', 'rb').read(), 'wav', 16000, {'dev_pid': 1537})
    print('录音结束')
    stream.stop_stream()
    stream.close()
    p.terminate()
    wf.close()
    print(result['result'][0])
    return result['result'][0]