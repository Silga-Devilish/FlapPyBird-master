import time
import cv2
import mediapipe as mp

import pygame
import numpy as np


def process_frame(img,self):
    yPos=0
    xPos=0
    avgx=300
    avgy=300

    start_time = time.time()
    scaler = 1
    imgWidth=1920
    imgHeight = 1080
    img_RGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = model.process(img_RGB)
    if results.multi_face_landmarks:
        sumx=0
        sumy=0
        for face_landmark in results.multi_face_landmarks:
            for i, lm in enumerate(face_landmark.landmark):
                xPos = int(lm.x * imgWidth)
                yPos = int(lm.y * imgHeight)
                cv2.putText(img, str(i), (xPos - 25, yPos + 5), cv2.FONT_HERSHEY_SIMPLEX, 0.2, (0, 0, 255), 1)
                sumx+=xPos
                sumy+=yPos
            avgx = sumx/len(face_landmark.landmark)
            avgy = sumy / len(face_landmark.landmark)
            mp_drawing.draw_landmarks(
                image=img,
                landmark_list=face_landmark,
                connections=mp_face_mech.FACEMESH_TESSELATION,
                connection_drawing_spec=mp_drawing_styles.get_default_face_mesh_tesselation_style()
            )
            mp_drawing.draw_landmarks(
                image=img,
                landmark_list=face_landmark,
                connections=mp_face_mech.FACEMESH_CONTOURS,
                connection_drawing_spec=mp_drawing_styles.get_default_face_mesh_contours_style()
            )
            mp_drawing.draw_landmarks(
                image=img,
                landmark_list=face_landmark,
                connections=mp_face_mech.FACEMESH_IRISES,
                connection_drawing_spec=mp_drawing_styles.get_default_face_mesh_iris_connections_style()
            )
    else:
        img = cv2.putText(img, 'No Face Detected', (25 * scaler, 50 * scaler), cv2.FONT_HERSHEY_SIMPLEX,
                              1.25 * scaler, (0, 0, 255), 2 * scaler)
    end_time = time.time()
    FPS = 1 / (end_time - start_time)

    cv2.putText(img, 'FPS' + str(int(FPS)), (25 * scaler, 100 * scaler), cv2.FONT_HERSHEY_SIMPLEX,
                          1.25 * scaler, (0, 0, 255), 2 * scaler)

    return img,avgx,avgy
def face_identify():
    camera = cv2.VideoCapture(0)
    cv2.namedWindow('Camera Feed', cv2.WINDOW_NORMAL)
    cv2.resizeWindow('Camera Feed', 1920, 1080)
    mp_face_mech = mp.solutions.face_mesh
    model = mp_face_mech.FaceMesh(static_image_mode=False,
                                  max_num_faces=2,
                                  refine_landmarks=True,
                                  )
    mp_drawing = mp.solutions.drawing_utils
    mp_drawing_styles = mp.solutions.drawing_styles
    camera.open(0)
    while camera.isOpened():
        success, frame = camera.read()
        if not success:
            print('Error')
            break

        frame,x,y= process_frame(frame,mp_face_mech,model,mp_drawing,mp_drawing_styles)
        cv2.imshow('Camera Feed', frame)

        if cv2.waitKey(1) in [ord('q'), 27]:
            break

    camera.release()
    cv2.destroyAllWindows()

def get_frame():
    ret, frame = camera.read()
    running = True

    if not ret:
        print("Error: Failed to open camera.")
        running = False
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame = np.rot90(frame)
    frame = pygame.surfarray.make_surface(frame)

    return frame