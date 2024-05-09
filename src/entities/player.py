from enum import Enum
from itertools import cycle
import pygame
from ..utils import GameConfig, clamp
from .entity import Entity
from .floor import Floor
from .pipe import Pipe, Pipes
from face import face_identify,process_frame
import time
import cv2
import mediapipe as mp
class PlayerMode(Enum):
    SHM = "SHM"
    NORMAL = "NORMAL"
    CRASH = "CRASH"


class Player(Entity):
    def __init__(self, config: GameConfig) -> None:
        image = config.images.player[0]
        x = int(config.window.width * 0.2)
        y = 300
        super().__init__(config, image, x, y)
        self.min_y = -2 * self.h
        self.max_y = config.window.viewport_height - self.h * 0.75
        self.img_idx = 0
        self.img_gen = cycle([0, 1, 2, 1])
        self.frame = 0
        self.crashed = False
        self.crash_entity = None
        self.set_mode(PlayerMode.SHM)
        self.cap = cv2.VideoCapture(1)
        cv2.namedWindow('Camera Feed', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('Camera Feed', 1920, 1080)
        self.mp_face_mech = mp.solutions.face_mesh
        self.model = self.mp_face_mech.FaceMesh(static_image_mode=False,
                                      max_num_faces=2,
                                      refine_landmarks=True,
                                      )
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        self.cap.open(0)
    def set_mode(self, mode: PlayerMode) -> None:
        self.mode = mode
        if mode == PlayerMode.NORMAL:
            self.reset_vals_normal()
            self.config.sounds.wing.play()
        elif mode == PlayerMode.SHM:
            self.reset_vals_shm()
        elif mode == PlayerMode.CRASH:
            self.stop_wings()
            self.config.sounds.hit.play()
            if self.crash_entity == "pipe":
                self.config.sounds.die.play()
            self.reset_vals_crash()
    def reset_vals_normal(self) -> None:
        self.vel_y = -9  # player's velocity along Y axis
        self.max_vel_y = 10  # max vel along Y, max descend speed
        self.min_vel_y = -8  # min vel along Y, max ascend speed
        self.acc_y = 1  # players downward acceleration

        self.rot = 80  # player's current rotation
        self.vel_rot = 0  # player's rotation speed
        self.rot_min = 0  # player's min rotation angle
        self.rot_max = 0  # player's max rotation angle

        self.flap_acc = -9  # players speed on flapping
        self.flapped = False  # True when player flaps
    def reset_vals_shm(self) -> None:
        self.vel_y = 4  # player's velocity along Y axis
        self.max_vel_y = 5  # max vel along Y, max descend speed
        self.min_vel_y = -5  # min vel along Y, max ascend speed
        self.acc_y = 1 # players downward acceleration

        self.rot = 0  # player's current rotation
        self.vel_rot = 0  # player's rotation speed
        self.rot_min = 0  # player's min rotation angle
        self.rot_max = 0  # player's max rotation angle

        self.flap_acc = 0  # players speed on flapping
        self.flapped = False  # True when player flaps
    def reset_vals_crash(self) -> None:
        self.acc_y = 2
        self.vel_y = 7
        self.max_vel_y = 15
        self.vel_rot = -8
    def update_image(self):
        self.frame += 1
        if self.frame % 5 == 0:
            self.img_idx = next(self.img_gen)
            self.image = self.config.images.player[self.img_idx]
            self.w = self.image.get_width()
            self.h = self.image.get_height()
    def tick_shm(self) -> None:
        if self.vel_y >= self.max_vel_y or self.vel_y <= self.min_vel_y:
            self.acc_y *= -1
        self.vel_y += self.acc_y
        self.y += self.vel_y

    def process_frame(self,img):
        yPos = 0
        xPos = 0
        avgx = 300
        avgy = 300

        start_time = time.time()
        scaler = 1
        imgWidth = 1920
        imgHeight = 1080
        img_RGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = self.model.process(img_RGB)
        if results.multi_face_landmarks:
            sumx = 0
            sumy = 0
            for face_landmark in results.multi_face_landmarks:
                for i, lm in enumerate(face_landmark.landmark):
                    xPos = int(lm.x * imgWidth)
                    yPos = int(lm.y * imgHeight)
                    cv2.putText(img, str(i), (xPos - 25, yPos + 5), cv2.FONT_HERSHEY_SIMPLEX, 0.2, (0, 0, 255), 1)
                    sumx += xPos
                    sumy += yPos
                avgx = sumx / len(face_landmark.landmark)
                avgy = sumy / len(face_landmark.landmark)
                self.mp_drawing.draw_landmarks(
                    image=img,
                    landmark_list=face_landmark,
                    connections=self.mp_face_mech.FACEMESH_TESSELATION,
                    connection_drawing_spec=self.mp_drawing_styles.get_default_face_mesh_tesselation_style()
                )
                self.mp_drawing.draw_landmarks(
                    image=img,
                    landmark_list=face_landmark,
                    connections=self.mp_face_mech.FACEMESH_CONTOURS,
                    connection_drawing_spec=self.mp_drawing_styles.get_default_face_mesh_contours_style()
                )
                self.mp_drawing.draw_landmarks(
                    image=img,
                    landmark_list=face_landmark,
                    connections=self.mp_face_mech.FACEMESH_IRISES,
                    connection_drawing_spec=self.mp_drawing_styles.get_default_face_mesh_iris_connections_style()
                )
        else:
            img = cv2.putText(img, 'No Face Detected', (25 * scaler, 50 * scaler), cv2.FONT_HERSHEY_SIMPLEX,
                              1.25 * scaler, (0, 0, 255), 2 * scaler)
        end_time = time.time()
        FPS = 1 / (end_time - start_time)

        cv2.putText(img, 'FPS' + str(int(FPS)), (25 * scaler, 100 * scaler), cv2.FONT_HERSHEY_SIMPLEX,
                    1.25 * scaler, (0, 0, 255), 2 * scaler)
        cv2.imshow('Camera Feed', img)
        return img, avgx, avgy

    def tick_normal(self) -> None:
        success,img=self.cap.read()
        self.y = self.process_frame(img)[2]
        self.rotate()

    def tick_crash(self) -> None:
        if self.min_y <= self.y <= self.max_y:
            self.y = clamp(self.y + self.vel_y, self.min_y, self.max_y)
            # rotate only when it's a pipe crash and bird is still falling
            if self.crash_entity != "floor":
                self.rotate()

        # player velocity change
        if self.vel_y < self.max_vel_y:
            self.vel_y += self.acc_y

    def rotate(self) -> None:
        self.rot = clamp(self.rot + self.vel_rot, self.rot_min, self.rot_max)

    def draw(self) -> None:
        self.update_image()
        if self.mode == PlayerMode.SHM:
            self.tick_shm()
        elif self.mode == PlayerMode.NORMAL:
            self.tick_normal()
        elif self.mode == PlayerMode.CRASH:
            self.tick_crash()
        self.draw_player()

    def draw_player(self) -> None:
        rotated_image = pygame.transform.rotate(self.image, self.rot)
        rotated_rect = rotated_image.get_rect(center=self.rect.center)
        self.config.screen.blit(rotated_image, rotated_rect)

    def stop_wings(self) -> None:
        self.img_gen = cycle([self.img_idx])

    def flap(self) -> None:
        if self.y > self.min_y:
            self.vel_y = self.flap_acc
            self.flapped = True
            self.rot = 80
            self.config.sounds.wing.play()

    def crossed(self, pipe: Pipe) -> bool:
        return pipe.cx <= self.cx < pipe.cx - pipe.vel_x

    def collided(self, pipes: Pipes, floor: Floor) -> bool:
        """returns True if player collides with floor or pipes."""

        # if player crashes into ground
        if self.collide(floor):
            self.crashed = True
            self.crash_entity = "floor"
            return True

        for pipe in pipes.upper:
            if self.collide(pipe):
                self.crashed = True
                self.crash_entity = "pipe"
                return True
        for pipe in pipes.lower:
            if self.collide(pipe):
                self.crashed = True
                self.crash_entity = "pipe"
                return True

        return False
