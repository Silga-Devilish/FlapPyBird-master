import asyncio
from src.flappy import Flappy

from speech import speech_recognition,whether_speech_event
import threading

def run_speech_identify():
     print("在运行语音识别")
     while True:
         speech_recognition(3)

async def main():
    flappy_instance = Flappy()
    await flappy_instance.start()

if __name__ == "__main__":
    # 创建并启动一个线程来运行speech_identify（注意：调用函数而不是函数返回值）
     thread1 = threading.Thread(target=run_speech_identify)
     thread1.start()

    # 在主进程中运行asyncio事件循环
     asyncio.run(main())

    # 如果你希望主线程等待 speech_identify 线程完成再退出程序，
    # 可以添加以下代码。但由于 asyncio.run(main()) 会阻塞主线程，
    # 这里需要重新设计你的程序结构以确保正确地同时处理异步和同步任务。
    # thread1.join()

    # 一种可能的方法是，在main函数内部或通过回调函数安排主线程在适当的时候等待子线程结束。

    # 示例（仅供参考）：
    # 注意这将导致Flappy实例停止后才等待speech_identify线程结束
    # asyncio.get_event_loop().run_until_complete(thread1.join_coroutine())