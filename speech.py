from aip import AipSpeech
import pyaudio
import wave
import threading
#准备APPID，APIKEY，secretKey
APP_ID = "67452641"
API_KEY = "xIdMTaac8ubhQ3J4Jp5v1RNq"
SECRET_KEY = "wqKJpfpb2MCisTD9KeTVVLQvltG9WN6g"
client = AipSpeech(APP_ID,API_KEY,SECRET_KEY)

whether_speech_event = threading.Event()  # 在全局作用域定义Event对象
speech_exit =threading.Event()

def reset_speech_event():
    """
    重置语音识别事件，表示尚未识别到特定语音指令。
    """
    global whether_speech_event
    whether_speech_event.clear()  # 将事件状态设置为未发生

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
    #传递参数：文件、文件格式、采样频率、PID（中文1537）
    result = client.asr(open('test3.wav', 'rb').read(), 'wav', 16000, {'dev_pid': 1537})

    print('录音结束')


    recognized_text = ""  # 初始化 recognized_text，默认为空字符串
    # 添加错误处理和指令检测逻辑
    if 'result' in result and result['result']:  # 确保'result'存在且不为空
        recognized_text = result['result'][0]
        trigger_phrases_start = ["开始游戏。", "游戏开始。", "开始。"]
        trigger_phrases_exit = ["退出游戏。", "游戏退出。", "退出。", "游戏关闭。", "关闭游戏。"]
        if recognized_text in trigger_phrases_start:
                print("检测到开始指令！")
                whether_speech_event.set()
        elif recognized_text in trigger_phrases_exit:
                print("检测到退出指令！")
                speech_exit.set()
        else:
                print("未检测到特定指令。")
    else:
        print("语音识别返回结果中没有找到'result'或结果为空。")


    stream.stop_stream()
    stream.close()
    p.terminate()
    wf.close()
    print(result['result'][0])
    return result['result'][0]
