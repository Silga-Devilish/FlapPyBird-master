import cv2

# 创建一个VideoCapture对象来获取视频源，参数0表示默认摄像头
camera = cv2.VideoCapture(0)

# 检查是否成功打开了摄像头
if not camera.isOpened():
    print("无法打开摄像头")
    exit()

while True:
    # 从摄像头捕获一帧图像
    ret, frame = camera.read()

    # ret是一个布尔值，表示是否成功读取到帧
    if not ret:
        print("无法获取视频帧，退出...")
        break

    # 显示当前帧
    cv2.imshow('摄像头画面', frame)

    # 按'q'键退出循环
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# 释放摄像头资源
camera.release()

# 关闭所有OpenCV窗口
cv2.destroyAllWindows()