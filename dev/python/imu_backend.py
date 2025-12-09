import socket
import sys
import threading, time
#!/usr/bin/env python

# noinspection PyUnresolvedReferences
import vtkmodules.vtkInteractionStyle
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkCommonTransforms import vtkTransform
from vtkmodules.vtkFiltersSources import vtkSphereSource
from vtkmodules.vtkRenderingAnnotation import vtkAxesActor
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkPolyDataMapper,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkRenderer
)


def visualizer(dmpdata):
    colors = vtkNamedColors()

    # create a Sphere
    sphereSource = vtkSphereSource()
    sphereSource.SetCenter(0.0, 0.0, 0.0)
    sphereSource.SetRadius(0.2)

    # create a mapper
    sphereMapper = vtkPolyDataMapper()
    sphereMapper.SetInputConnection(sphereSource.GetOutputPort())

    # create an actor
    sphereActor = vtkActor()
    sphereActor.SetMapper(sphereMapper)
    sphereActor.RotateWXYZ(dmpdata["qw"],dmpdata["qx"],dmpdata["qy"],dmpdata["qz"])

    # a renderer and render window
    renderer = vtkRenderer()
    renderWindow = vtkRenderWindow()
    renderWindow.SetWindowName('Axes')
    renderWindow.AddRenderer(renderer)

    # an interactor
    renderWindowInteractor = vtkRenderWindowInteractor()
    renderWindowInteractor.SetRenderWindow(renderWindow)

    # add the actors to the scene
    renderer.AddActor(sphereActor)
    renderer.SetBackground(colors.GetColor3d('SlateGray'))

    transform = vtkTransform()
    transform.Translate(1.0, 0.0, 0.0)


    axes = vtkAxesActor()
    #  The axes are positioned with a user transform
    axes.SetUserTransform(transform)
    axes.RotateWXYZ(dmpdata["qw"],dmpdata["qx"],dmpdata["qy"],dmpdata["qz"])

    # properties of the axes labels can be set as follows
    # this sets the x axis label to red
    # axes.GetXAxisCaptionActor2D().GetCaptionTextProperty().SetColor(colors.GetColor3d('Red'));

    # the actual text of the axis label can be changed:
    # axes->SetXAxisLabelText('test');

    renderer.AddActor(axes)

    renderer.GetActiveCamera().Azimuth(50)
    renderer.GetActiveCamera().Elevation(-30)

    renderer.ResetCamera()
    renderWindow.SetWindowName('Axes')
    renderWindow.Render()

    # begin mouse interaction
    renderWindowInteractor.Start()
    axes.RotateWXYZ(dmpdata["qw"],dmpdata["qx"],dmpdata["qy"],dmpdata["qz"])

    time.sleep(2)
    renderWindow.Render()
    axes.RotateWXYZ(dmpdata["qw"],dmpdata["qx"],dmpdata["qy"],dmpdata["qz"])

    time.sleep(2)

    renderWindow.Render()

# if len(sys.argv) == 3:
#     ip = sys.argv[1]
#     port = int(sys.argv[2])
# else:
#     print("Run like : python3 server.py <arg1:server ip:this system IP 192.168.1.6> <arg2:server port:4444 >")
#     exit(1)


ESP_IP = "0.0.0.0"
ESP_PORT = 4210

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

def webserver(dmpdata=None) -> None:
    # Create a UDP socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # Bind the socket to the port
    server_address = (ESP_IP, ESP_PORT)
    s.bind(server_address)
    print("Do Ctrl+c to exit the program !!")
    s.sendto(bytes("Hello device", "utf-8"), ("192.168.0.64", 1330))
    print("####### Server is listening #######")
    while True:
        data, address = s.recvfrom(4096)
        data = data.decode("utf-8").replace('\x00','').strip("\n").split(",")
        data[15] = data[15]
        print(data)
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

def main():
    dmpdata={"qw":0.0,"qx":0.0,"qy":0.0,"qz":0.0,"raw":None}
    threadlist = []

    threadlist.append(threading.Thread(
        target=webserver, args=[dmpdata]
    ))
    # threadlist.append(threading.Thread(
    #     target=visualizer, args=[dmpdata]
    # ))

    for x in threadlist:
        x.start()

    # for x in threadlist:
    #     x.join()  

if __name__ == "__main__":
    main()
    pass


