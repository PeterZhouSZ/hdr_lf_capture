from tkinter import Tk, Label, Button, Entry

import serial
import os
import subprocess

import gphoto2 as gp

class CameraControl:
    def __init__(self, master, port, baud_rate):
        self.master = master
        master.title("Camera Control")

        self.ser = serial.Serial(port, baud_rate)
        self.callback = gp.check_result(gp.use_python_logging())
        self.camera = gp.check_result(gp.gp_camera_new())
        
        self.speed_label = Label(master, text="Current speed:")
        self.current_speed = Label(master, text="5", width=5)

        self.speed_label.grid(column=0, row=0)
        self.current_speed.grid(column=1, row=0)

        self.speed_down_button = Button(master, command=self.decrease_speed, text="−", height=2, width=10)
        self.speed_up_button = Button(master, command=self.increase_speed, text="+", width=10)
        self.speed_set_button = Button(master, command=self.send_speed, text="Set", width=10)

        self.speed_down_button.grid(column=2, row=0, sticky="ewns")
        self.speed_up_button.grid(column=3, row=0, sticky="ewns")
        self.speed_set_button.grid(column=4, row=0, sticky="ewns")

        self.location_label = Label(master, text="Current location:")
        self.current_location = Label(master, text="0")

        self.location_label.grid(column=0, row=1)
        self.current_location.grid(column=1, row=1)

        self.location_left_button = Button(master, text="<", height=2)
        self.location_right_button = Button(master, text=">")
        self.reset_button = Button(master, command=self.reset_location, text="Reset")

        self.location_left_button.bind("<ButtonPress>", self.move_backward)
        self.location_right_button.bind("<ButtonPress>", self.move_forward)

        self.location_left_button.bind("<ButtonRelease>", self.stop)
        self.location_right_button.bind("<ButtonRelease>", self.stop)

        self.location_left_button.grid(column=2, row=1, sticky="ewns")
        self.location_right_button.grid(column=3, row=1, sticky="ewns")
        self.reset_button.grid(column=4, row=1, sticky="ewns")

        self.destination_label = Label(master, text="Move to location:")
        self.current_destination = Label(master, text="0")

        self.destination_label.grid(column=0, row=2)
        self.current_destination.grid(column=1, row=2)
        
        self.destination_left_button = Button(master, command=self.decrease_destination, text="<", height=2)
        self.destination_right_button = Button(master, command=self.increase_destination, text=">")

        self.destination_left_button.grid(column=2, row=2, sticky="ewns")
        self.destination_right_button.grid(column=3, row=2, sticky="ewns")

        self.move_button = Button(master, command=self.move_to_location, text="Move")
        self.move_button.grid(column=4, row=2, sticky="ewns")

        self.status_label = Label(master, text="Stopped")
        self.status_label.grid(column=0, row=3)

        self.capture_button = Button(master, command=self.capture_image, text="Capture", height=2)
        self.capture_button.grid(column=2, row=3, sticky="ewns")

        self.capture_3d_button = Button(master, command=self.capture_3d, text="Capture 3D")
        self.capture_3d_button.grid(column=3, row=3, sticky="ewns")

        self.exit_button = Button(master, command=master.destroy, text="Exit")
        self.exit_button.grid(column=4, row=3, sticky="ewns")

    def increase_speed(self):
        new_speed = int(self.current_speed.cget("text")) + 1
        self.current_speed.configure(text=str(new_speed))

    def decrease_speed(self):
        new_speed = int(self.current_speed.cget("text")) - 1
        self.current_speed.configure(text=str(new_speed))

    def send_speed(self):
        self.ser.write(b'x' + self.current_speed.cget("text").encode('UTF-8'))

    def move_forward(self, event):
        self.status_label.configure(text="Moving forward")
        self.ser.write(b'1')

    def move_backward(self, event):
        self.status_label.configure(text="Moving backward")
        self.ser.write(b'2')

    def stop(self, event):
        self.status_label.configure(text="Stopped")
        self.ser.write(b'0')
        new_location = int(self.ser.readline())
        self.current_location.configure(text=str(new_location))

    def reset_location(self):
        self.ser.write(b'r')
        self.current_speed.configure(text="5")
        self.current_location.configure(text="0")
        
    def increase_destination(self):
        new_destination = int(self.current_destination.cget("text")) + 1
        self.current_destination.configure(text=str(new_destination))

    def decrease_destination(self):
        new_destination = int(self.current_destination.cget("text")) - 1
        self.current_destination.configure(text=str(new_destination))

    def move_to_location(self):
        self.ser.write(b'm' + self.current_destination.cget("text").encode('UTF-8'))
        process = self.ser.readline()
        self.current_location.configure(text=self.current_destination.cget("text"))

    def capture_image(self):
        gp.check_result(gp.gp_camera_init(self.camera))
        file_path = gp.check_result(gp.gp_camera_capture(
            self.camera, gp.GP_CAPTURE_IMAGE))
        target = os.path.join('/tmp', file_path.name)
        camera_file = gp.check_result(gp.gp_camera_file_get(
                self.camera, file_path.folder, file_path.name, gp.GP_FILE_TYPE_NORMAL))
        gp.check_result(gp.gp_file_save(camera_file, target))
        subprocess.call(['xdg-open', target])
        gp.check_result(gp.gp_camera_exit(self.camera))

    def capture_3d(self):
        gp.check_result(gp.gp_camera_init(self.camera))
        self.ser.write(b'm0')
        process = self.ser.readline()

        for x in range(5):
            self.current_location.configure(text=str(x+1))
            self.ser.write(b'f')
            process = self.ser.readline()
            
            file_path = gp.check_result(gp.gp_camera_capture(
                self.camera, gp.GP_CAPTURE_IMAGE))
            target = os.path.join('/tmp', file_path.name)
            camera_file = gp.check_result(gp.gp_camera_file_get(
                    self.camera, file_path.folder, file_path.name, gp.GP_FILE_TYPE_NORMAL))
            gp.check_result(gp.gp_file_save(camera_file, target))

        gp.check_result(gp.gp_camera_exit(self.camera))
