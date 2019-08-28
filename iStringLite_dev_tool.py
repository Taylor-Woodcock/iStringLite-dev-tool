import tkinter as tk  # for python 3
from tkinter import messagebox
import pygubu
import socket
import math

# COMMANDS
Command_Readdress = 0x06
Command_Configure = 0x20
Command_DynamicReaddress = 0x14

class iStringLiteDevTool(pygubu.TkApplication):  
    def _create_ui(self):
        self.builder = builder = pygubu.Builder()
        builder.add_from_file('iStringLite_dev_tool.ui')

        self.mainwindow = builder.get_object('Fr_main', self.master)
        
        # set some window properties
        self.toplevel.resizable(False, False)
        self.set_title('iStringLite Dev Tool')

        # enable callback functions
        builder.connect_callbacks(self)

        self.hostname = self.builder.tkvariables.__getitem__('hostname')
        self.port = self.builder.tkvariables.__getitem__('port')
        self.controller_value = self.builder.tkvariables.__getitem__('controller_id_value')
        self.lighting_value = self.builder.tkvariables.__getitem__('lighting_id_value')
        self.factory_value = self.builder.tkvariables.__getitem__('factory_value')
        self.starting_id_value = self.builder.tkvariables.__getitem__('starting_id_value')

        self.hostname.set("169.254.1.1")

    # used for sending commands to the iStringLite devices
    def sendCommand(self, controlElementID: int, lightingElementID: int, command: int, data: bytes):
        # return if controller ID is invalid
        if (controlElementID < 0 or controlElementID > 255):
            return
        
        # return if lighting ID is invalid
        if (lightingElementID < 0 or lightingElementID > 255):
            return

        # return if command is invalid
        #if (Array.IndexOf(VALID_COMMANDS, command) == -1):
        #    return

        checksum = 0x00

        packetBuffer = bytearray(len(data) + 6) # create empty byte array

        length = len(packetBuffer)

        packetBuffer[0] = controlElementID
        packetBuffer[1] = lightingElementID
        packetBuffer[2] = (length>>8) & 0xff # length_high
        packetBuffer[3] = length & 0xff # length_low
        packetBuffer[4] = command
        packetBuffer[5] = checksum

        i = 0

        for x in data:
            packetBuffer[6 + i] = x
            i += 1

        for x in packetBuffer:
            checksum += x
            if(checksum >= 256):
                checksum -= 256

        packetBuffer[5] = checksum

        # send UDP packet
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(packetBuffer, (self.hostname.get(), self.port.get()))

    # when the controller ID changes
    def on_controller_id_change(self, value):
        self.controller_value.set(int(float(value)))

    # when the lighting ID changes
    def on_lighting_id_change(self, value):
        self.lighting_value.set(int(float(value)))

    # when the starting ID changes
    def on_starting_id_change(self, value):
        starting_id_value.set(int(float(value)))

    # turn factory mode on
    def on_factory_on_clicked(self):
        print("Factory Mode: On")
        self.factory_value.set("On")

        # factory mode code
        MASK = 0b00010000
        data = [MASK, 0x00, 0x00, 0x00, 0x00, 0x02, 0x00, 0x00, 0x00]
        self.sendCommand(self.controller_value.get(), self.lighting_value.get(), Command_Configure, data)

    # turn factory mode on
    def on_factory_off_clicked(self):
        print("Factory Mode: Off")
        self.factory_value.set("Off")

        # factory mode code
        MASK = 0b00010000
        data = [MASK, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
        self.sendCommand(self.controller_value.get(), self.lighting_value.get(), Command_Configure, data)

    def on_readdress_clicked(self):
        
        if(self.factory_value.get() == "Off"):
            messagebox.showwarning("Warning", "You must turn factory mode on to use this command")
            return

        print("Readdressing LEDs with an offset of", self.starting_id_value.get())

        # readdress code
        self.sendCommand(self.controller_value.get(), self.lighting_value.get(), Command_DynamicReaddress, [self.starting_id_value.get()])

if __name__ == '__main__':
    root = tk.Tk()
    app = iStringLiteDevTool(root)
    root.mainloop()
