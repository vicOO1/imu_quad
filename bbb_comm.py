# This script creates a 3D visualization 
# of an IMU's orientation in space
# by reading Euler angle data received
# over the network.

from visual import *
from PIL import Image
import socket
import sys
import os
import select
import signal
import struct
import threading

ip='192.168.1.8'
imu_port=9930

threads = []

deg2rad = 180.0/3.141592
img_width = 160
img_height = 120
MAX_PPM_IMG_SIZE = img_width*img_height*3

def signal_handler(singal, frame):
   sys.exit(0)

def parse_socket_data(data):
   global platform   
   global roll
   global pitch
   global yaw

   data_len = len(data)

   if (data_len % 24 == 0):
      while(data_len > 0):
         unpacked_data = struct.unpack('<I', data[:4])
         data_len -= 4
         if (int(unpacked_data[0]) == int(0xdeadbeef)):
            unpacked_data = struct.unpack('<I', data[4:8])
            data_len -= 4
            if (hex(unpacked_data[0]) != 0xdeadbeef):
               ts = int(unpacked_data[0])
               unpacked_data = struct.unpack('<f', data[8:12])
               data_len -= 4
               yaw = round(unpacked_data[0], 4)
               unpacked_data = struct.unpack('<f', data[12:16])
               data_len -= 4
               pitch = round(unpacked_data[0], 4)
               unpacked_data = struct.unpack('<f', data[16:20])
               data_len -= 4
               roll = round(unpacked_data[0], 4)
               unpacked_data = struct.unpack('<I', data[20:24])
               data_len -= 4
               if (int(unpacked_data[0]) == int(0xdeadbeef)):
                  my_str = str(ts) + ', ' + str(yaw) + ', ' + str(pitch) + ', ' + str(roll)
                  print(my_str)
                  axis=(cos(pitch)*cos(yaw),-cos(pitch)*sin(yaw),sin(pitch))
                  up=(sin(roll)*sin(yaw)+cos(roll)*sin(pitch)*cos(yaw),sin(roll)*cos(yaw)-cos(roll)*sin(pitch)*sin(yaw),-cos(roll)*cos(pitch))
                  platform.axis=axis
                  platform.up=up
                  platform.length=1.0
                  platform.width=0.65
                  plat_arrow.axis=axis
                  plat_arrow.up=up
                  plat_arrow.length=0.8
                  p_line.axis=axis
                  p_line.up=up
                  cil_roll.axis=(0.2*cos(roll),0.2*sin(roll),0)
                  cil_roll2.axis=(-0.2*cos(roll),-0.2*sin(roll),0)
                  cil_pitch.axis=(0.2*cos(pitch),0.2*sin(pitch),0)
                  cil_pitch2.axis=(-0.2*cos(pitch),-0.2*sin(pitch),0)
                  arrow_course.axis=(0.2*sin(yaw),0.2*cos(yaw),0)
                  L1.text = str(round(rad2deg(roll), 2))
                  L2.text = str(round(rad2deg(pitch), 2))
                  L3.text = str(round(rad2deg(yaw), 2))
               else:
                  print 'Expected 0xdeadbeef as footer but got something else'
   else:
      print 'data_len received to parse is not a multiple of 24'

def net_thread():
   global sock1
   global sock2
   global roll
   global pitch
   global yaw

   roll=0
   pitch=0
   yaw=0

   bin_data2 = ''

   print 'Listening for IMU data on ' + ip + ' port ' + str(imu_port)
   print 'Listening for CAM data on ' + ip + ' port ' + str(cam_port)
   while(1):
      sock_ready = select.select([sock1, sock2], [], [], 0.5)
      if sock_ready[0]:
         for sock in sock_ready[0]:
            if sock == sock1:
               bin_data1 = sock.recv(10000000)
               parse_socket_data(bin_data1)

            elif sock == sock2:
               bin_data2 += sock2.recv(10000000)
               print len(bin_data2)
               if len(bin_data2) >= MAX_PPM_IMG_SIZE+20:
                  bin_fd = open('bin_data', 'wb')
                  bin_fd.write(bin_data2)
                  bin_fd.flush()
                  bin_fd.close()
                  parse_cam_data(bin_data2) 
                  bin_data2 = ''

signal.signal(signal.SIGINT, signal_handler)
sock1 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock1.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 1000000) 
sock1.setblocking(0)
sock2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock2.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 1000000) 
sock2.setblocking(0)

scene=display(title="IMU")
scene.range=(1.2,1.2,1.2)
scene.forward = (1,0,-0.25)
scene.up=(0,0,1)

# Second scene (Roll, Pitch, Yaw)
scene2 = display(title='IMU',x=0, y=0, width=500, height=200,center=(0,0,0), background=(0,0,0))
scene2.range=(1,1,1)
scene.width=500
scene.y=200

scene2.select()
#Roll, Pitch, Yaw
cil_roll = cylinder(pos=(-0.4,0,0),axis=(0.2,0,0),radius=0.01,color=color.red)
cil_roll2 = cylinder(pos=(-0.4,0,0),axis=(-0.2,0,0),radius=0.01,color=color.red)
cil_pitch = cylinder(pos=(0.1,0,0),axis=(0.2,0,0),radius=0.01,color=color.green)
cil_pitch2 = cylinder(pos=(0.1,0,0),axis=(-0.2,0,0),radius=0.01,color=color.green)
arrow_course = arrow(pos=(0.6,0,0),color=color.cyan,axis=(-0.2,0,0), shaftwidth=0.02, fixedwidth=1)

#Roll,Pitch,Yaw labels
label(pos=(-0.4,0.3,0),text="Roll",box=0,opacity=0)
label(pos=(0.1,0.3,0),text="Pitch",box=0,opacity=0)
label(pos=(0.55,0.3,0),text="Yaw",box=0,opacity=0)
label(pos=(0.6,0.22,0),text="N",box=0,opacity=0,color=color.yellow)
label(pos=(0.6,-0.22,0),text="S",box=0,opacity=0,color=color.yellow)
label(pos=(0.38,0,0),text="W",box=0,opacity=0,color=color.yellow)
label(pos=(0.82,0,0),text="E",box=0,opacity=0,color=color.yellow)
label(pos=(0.75,0.15,0),height=7,text="NE",box=0,color=color.yellow)
label(pos=(0.45,0.15,0),height=7,text="NW",box=0,color=color.yellow)
label(pos=(0.75,-0.15,0),height=7,text="SE",box=0,color=color.yellow)
label(pos=(0.45,-0.15,0),height=7,text="SW",box=0,color=color.yellow)

L1 = label(pos=(-0.4,0.22,0),text="-",box=0,opacity=0)
L2 = label(pos=(0.1,0.22,0),text="-",box=0,opacity=0)
L3 = label(pos=(0.7,0.3,0),text="-",box=0,opacity=0)

# Main scene objects
scene.select()
# Reference axis (x,y,z)
arrow(color=color.green,axis=(1,0,0), shaftwidth=0.02, fixedwidth=1)
arrow(color=color.green,axis=(0,-1,0), shaftwidth=0.02 , fixedwidth=1)
arrow(color=color.green,axis=(0,0,-1), shaftwidth=0.02, fixedwidth=1)
# labels
label(pos=(0,0,0.8),text="IMU",box=0,opacity=0)
label(pos=(1,0,0),text="X",box=0,opacity=0)
label(pos=(0,-1,0),text="Y",box=0,opacity=0)
label(pos=(0,0,-1),text="Z",box=0,opacity=0)
# IMU object
platform = box(length=1, height=0.05, width=1, color=color.red)
p_line = box(length=1,height=0.08,width=0.1,color=color.yellow)
plat_arrow = arrow(color=color.green,axis=(1,0,0), shaftwidth=0.06, fixedwidth=1)

try: 
   sock1.bind((ip, imu_port))
   sock2.bind((ip, cam_port))
except socket.error:
   unable_to_bind = True
else:
   sock_t = threading.Thread(target=net_thread)
   sock_t.daemon = True
   threads.append(sock_t)
   sock_t.start()
