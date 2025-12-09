"""
PyTeapot module for drawing rotating cube using OpenGL as per
quaternion or yaw, pitch, roll angles received over serial port.
"""

import pygame
import math
import socket
from OpenGL.GL import *
from OpenGL.GLU import *
from pygame.locals import *


class DMP_Object:
    def __init__(self,qw,qx,qy,qz,ypr,accel_with_gravity,accel_without_gravity,temp,rssi,seq):
        self.qw = qw
        self.qx = qx
        self.qy = qy
        self.qz = qz
        self.ypr = ypr
        self.accel_with_gravity = accel_with_gravity
        self.accel_without_gravity = accel_without_gravity
        self.temp = temp
        self.rssi = rssi
        self.seq = seq

useSerial = False # set true for using serial for data transmission, false for wifi
useQuat = False   # set true for using quaternions, false for using y,p,r angles
dmpdata={"qw":0.0,"qx":0.0,"qy":0.0,"qz":0.0,"raw":None}
current_state = DMP_Object(0,0,0,0,[0,0,0],[0,0,0],[0,0,0],0,0,0)

if(useSerial):
    import serial
    ser = serial.Serial('/dev/ttyUSB0', 38400)
else:
    UDP_IP = "0.0.0.0"
    UDP_PORT = 4210
    sock = socket.socket(socket.AF_INET, # Internet
                         socket.SOCK_DGRAM) # UDP
    sock.bind((UDP_IP, UDP_PORT))
    sock.sendto(bytes("Hello device", "utf-8"), ("192.168.0.64", 1330))


def main():
    video_flags = OPENGL | DOUBLEBUF
    pygame.init()
    screen = pygame.display.set_mode((960, 720), video_flags)
    pygame.display.set_caption("PyTeapot IMU orientation visualization")
    resizewin(960, 720)
    init()
    frames = 1
    ticks = pygame.time.get_ticks()
    fps = 0
    while 1:
        event = pygame.event.poll()
        if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
            break
        if(useQuat):
            [w, nx, ny, nz, temp, rssi] = read_data()
        else:
            [yaw, pitch, roll, temp, rssi] = read_data()
        if(useQuat):
            draw(w, nx, ny, nz,fps,temp, rssi)
        else:
            draw(1, yaw, pitch, roll, fps ,temp, rssi)
        pygame.display.flip()
        frames += 1
        fps = ((frames*1000)/(pygame.time.get_ticks()-ticks))
    print("fps: %d" % ((frames*1000)/(pygame.time.get_ticks()-ticks)))
    if(useSerial):
        ser.close()


def resizewin(width, height):
    """
    For resizing window
    """
    if height == 0:
        height = 1
    glViewport(0, 0, width, height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, 1.0*width/height, 0.1, 100.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()


def init():
    glShadeModel(GL_SMOOTH)
    glClearColor(0.0, 0.0, 0.0, 0.0)
    glClearDepth(1.0)
    glEnable(GL_DEPTH_TEST)
    glDepthFunc(GL_LEQUAL)
    glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST)


def cleanSerialBegin():
    if(useQuat):
        try:
            line = ser.readline().decode('UTF-8').replace('\n', '')
            w = float(line.split('w')[1])
            nx = float(line.split('a')[1])
            ny = float(line.split('b')[1])
            nz = float(line.split('c')[1])
        except Exception:
            pass
    else:
        try:
            line = ser.readline().decode('UTF-8').replace('\n', '')
            yaw = float(line.split('y')[1])
            pitch = float(line.split('p')[1])
            roll = float(line.split('r')[1])
        except Exception:
            pass


def read_data():
    if(useSerial):
        ser.reset_input_buffer()
        cleanSerialBegin()
        line = ser.readline().decode('UTF-8').replace('\n', '')
        print(line)
    else:
        # Waiting for data from udp port 5005
        data, address = sock.recvfrom(4096)
        data = data.decode("utf-8").replace('\x00','').strip("\n").split(",")
        data[15] = data[15]
        current_state = DMP_Object(
        float(data[0]),float(data[1]),float(data[2]),float(data[3]),#Quaternion
        [float(data[4]),float(data[5]),float(data[6])],#YPR 
        [int(data[7]),int(data[8]),int(data[9])],#Accel with gravity
        [int(data[10]),int(data[11]),int(data[12])],#Accel without gravity
        float(data[13]),float(data[14]),data[15])
        dmpdata["raw"] = current_state
        dmpdata["qw"] = current_state.qw
        dmpdata["qx"] = current_state.qx
        dmpdata["qy"] = current_state.qy
        dmpdata["qz"] = current_state.qz
        return [current_state.ypr[0],current_state.ypr[1],current_state.ypr[2] ,current_state.temp, current_state.rssi]
        #return [current_state.qw,current_state.qx,current_state.qy,current_state.qz]
                
    # if(useQuat):
    #     w = float(line.split('w')[1])
    #     nx = float(line.split('a')[1])
    #     ny = float(line.split('b')[1])
    #     nz = float(line.split('c')[1])
    #     return [w, nx, ny, nz, current_state.temp, current_state.rssi]
    # else:
    #     yaw = float(line.split('y')[1])
    #     pitch = float(line.split('p')[1])
    #     roll = float(line.split('r')[1])
    #     return [yaw, pitch, roll, current_state.temp, current_state.rssi]


def draw(w, nx, ny, nz, fps=1, temp=0, rssi=0):
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glTranslatef(0, 0.0, -7.0)

    drawText((-2.6, 1.8, 2), "PyTeapot", 18)
    drawText((-2.6, 1.6, 2), "Module to visualize quaternion or Euler angles data", 16)
    drawText((-2.6, -2, 2), "Press Escape to exit.", 16)
    drawText((-2.6, -1.9, 2), "FPS: %d  Temp: %.2f °C  RSSI: %d" %(fps,temp, rssi), 16)

    if(useQuat):
        [yaw, pitch , roll] = quat_to_ypr([w, nx, ny, nz])
        drawText((-2.6, -1.8, 2), "Yaw: %f, Pitch: %f, Roll: %f" %(yaw, pitch, roll), 16)

        glRotatef(2 * math.acos(w) * 180.00/math.pi, -1 * nx, nz, ny)
    else:
        yaw = nx
        pitch = ny
        roll = nz
        drawText((-2.6, -1.8, 2), "Yaw: %f, Pitch: %f, Roll: %f" %(yaw, pitch, roll), 16)
        drawText((-2.6, 20, 2), "Yaw: %f, Pitch: %f, Roll: %f" %(yaw, pitch, roll), 16)

        glRotatef(-roll, 0.00, 0.00, 1.00)
        glRotatef(pitch, 1.00, 0.00, 0.00)
        glRotatef(yaw, 0.00, 1.00, 0.00)

    glBegin(GL_QUADS)
    glColor3f(0.0, 1.0, 0.0)
    glVertex3f(1.0, 0.2, -1.0)
    glVertex3f(-1.0, 0.2, -1.0)
    glVertex3f(-1.0, 0.2, 1.0)
    glVertex3f(1.0, 0.2, 1.0)

    glColor3f(1.0, 0.5, 0.0)
    glVertex3f(1.0, -0.2, 1.0)
    glVertex3f(-1.0, -0.2, 1.0)
    glVertex3f(-1.0, -0.2, -1.0)
    glVertex3f(1.0, -0.2, -1.0)

    glColor3f(1.0, 0.0, 0.0)
    glVertex3f(1.0, 0.2, 1.0)
    glVertex3f(-1.0, 0.2, 1.0)
    glVertex3f(-1.0, -0.2, 1.0)
    glVertex3f(1.0, -0.2, 1.0)

    glColor3f(1.0, 1.0, 0.0)
    glVertex3f(1.0, -0.2, -1.0)
    glVertex3f(-1.0, -0.2, -1.0)
    glVertex3f(-1.0, 0.2, -1.0)
    glVertex3f(1.0, 0.2, -1.0)

    glColor3f(0.0, 0.0, 1.0)
    glVertex3f(-1.0, 0.2, 1.0)
    glVertex3f(-1.0, 0.2, -1.0)
    glVertex3f(-1.0, -0.2, -1.0)
    glVertex3f(-1.0, -0.2, 1.0)

    glColor3f(1.0, 0.0, 1.0)
    glVertex3f(1.0, 0.2, -1.0)
    glVertex3f(1.0, 0.2, 1.0)
    glVertex3f(1.0, -0.2, 1.0)
    glVertex3f(1.0, -0.2, -1.0)
    glEnd()


def drawText(position, textString, size):
    font = pygame.font.SysFont("Courier", size, True)
    textSurface = font.render(textString, True, (255, 255, 255, 255), (0, 0, 0, 255))
    textData = pygame.image.tostring(textSurface, "RGBA", True)
    glRasterPos3d(*position)
    glDrawPixels(textSurface.get_width(), textSurface.get_height(), GL_RGBA, GL_UNSIGNED_BYTE, textData)

def quat_to_ypr(q):
    yaw   = math.atan2(2.0 * (q[1] * q[2] + q[0] * q[3]), q[0] * q[0] + q[1] * q[1] - q[2] * q[2] - q[3] * q[3])
    pitch = -math.asin(2.0 * (q[1] * q[3] - q[0] * q[2]))
    roll  = math.atan2(2.0 * (q[0] * q[1] + q[2] * q[3]), q[0] * q[0] - q[1] * q[1] - q[2] * q[2] + q[3] * q[3])
    pitch *= 180.0 / math.pi
    yaw   *= 180.0 / math.pi
    yaw   -= -0.13  # Declination at Chandrapur, Maharashtra is - 0 degress 13 min
    roll  *= 180.0 / math.pi
    return [yaw, pitch, roll]


if __name__ == '__main__':
    main()