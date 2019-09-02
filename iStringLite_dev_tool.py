import tkinter as tk  # for python 3
from tkinter import messagebox
import pygubu
import socket
import math
import time
import random

# COMMANDS
Command_Readdress = 0x06
Command_Configure = 0x20
Command_DynamicReaddress = 0x14
Command_SetColour = 0x10


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
        self.controller_value = self.builder.tkvariables.__getitem__(
            'controller_id_value')
        self.lighting_value = self.builder.tkvariables.__getitem__(
            'lighting_id_value')
        self.factory_value = self.builder.tkvariables.__getitem__(
            'factory_value')
        self.starting_id_value = self.builder.tkvariables.__getitem__(
            'starting_id_value')
        self.end_id_value = self.builder.tkvariables.__getitem__(
            'end_id_value')

        self.hostname.set("169.254.1.1")

    def sendCommand(self, controlElementID: int, lightingElementID: int, command: int, data: bytes):
        """Formats and send UDP packets to the iSLAP protocol specification.

        Arguments:
            controlElementID {int} -- The ID of the controller the packet is intended for (255 = broadcast)
            lightingElementID {int} -- The ID of the lighting element the packet is intended for (255 = broadcast)
            command {int} -- The ID of the command being sent
            data {bytes} -- The payload of the packet being sent
        """
        # return if controller ID is invalid
        if (controlElementID < 0 or controlElementID > 255):
            return

        # return if lighting ID is invalid
        if (lightingElementID < 0 or lightingElementID > 255):
            return

        checksum = 0x00

        packetBuffer = bytearray(len(data) + 6)  # create empty byte array

        length = len(packetBuffer)

        packetBuffer[0] = controlElementID
        packetBuffer[1] = lightingElementID
        packetBuffer[2] = (length >> 8) & 0xff  # length_high
        packetBuffer[3] = length & 0xff  # length_low
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

    def on_controller_id_change(self, value):
        """Updates the controller ID value spinbox when the scroll bar is updated

        Arguments:
            value {[float]} -- The value of the controller ID scrollbar
        """
        self.controller_value.set(int(float(value)))

    def on_lighting_id_change(self, value):
        """Updates the lighting ID value spinbox when the scroll bar is updated

        Arguments:
            value {[float]} -- The value of the lighting ID scrollbar
        """
        self.lighting_value.set(int(float(value)))

    def on_starting_id_change(self, value):
        """Updates the starting ID value spinbox when the scroll bar is updated

        Arguments:
            value {[float]} -- The value of the starting ID scrollbar
        """
        self.starting_id_value.set(int(float(value)))

    def on_end_id_change(self, value):
        """Updates the starting ID value spinbox when the scroll bar is updated

        Arguments:
            value {[float]} -- The value of the starting ID scrollbar
        """
        self.end_id_value.set(int(float(value)))

    def on_factory_on_clicked(self):
        """Generates the payload for enabling Factory Mode
        """
        print("Factory Mode: On")
        self.factory_value.set("On")

        # factory mode code
        MASK = 0b00010000
        data = [0x10, 0x00, 0x00, 0x00, 0x00, 0x02, 0x00, 0x00, 0x5C]
        # IMPORTANT NOTE: LE must be 0 for this to work!
        self.sendCommand(self.controller_value.get(),
                         0, Command_Configure, data)

    # turn factory mode on
    def on_factory_off_clicked(self):
        """Generates the payload for enabling Normal Operation Mode
        """
        print("Factory Mode: Off")
        self.factory_value.set("Off")

        # factory mode code
        MASK = 0b00010000
        data = [0x10, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x5C]
        # IMPORTANT NOTE: LE must be 0 for this to work!
        self.sendCommand(self.controller_value.get(),
                         0, Command_Configure, data)

    def on_readdress_clicked(self):
        """Generates the payload for readdressing lighting elements.
           Note: Factory Mode must be enabled to readdress LEDs
        """
        # protect against trying to readdress without Factory Mode enabled
        if(self.factory_value.get() == "Off"):
            messagebox.showwarning(
                "Warning", "You must turn factory mode on to use this command")
            return

        # protect against trying to readdress LEDs in  opposing order
        if(self.starting_id_value.get() > self.end_id_value.get()):
            messagebox.showwarning(
                "Warning", "The starting ID cannot be greater than the end ID")
            return

        print("Readdressing LEDs to", self.starting_id_value.get(),
              "-", self.end_id_value.get())

        # send readdress packet with payload range
        self.sendCommand(self.controller_value.get(), self.lighting_value.get(
        ), Command_Readdress, list(range(self.starting_id_value.get(), self.end_id_value.get() + 1)))

    def on_readdress_test_clicked(self):
        """Used for testing if the readdress packet was received successfully
           by testing five LEDs starting at the new ID
        """
        button_text = self.builder.tkvariables.__getitem__(
            'readdress_test_text')

        # send a random colour change command to the first five LEDs starting at the new ID
        testNumber = 5
        for x in range(5):
            # set button to the current test number
            # TODO: Currently doesn'tupdate due to time.sleep(). after() would fix this
            button_text.set(testNumber)

            print("Testing LED", self.starting_id_value.get() +
                  x, "controller", self.controller_value.get())

            # send a SetColour command with random RGB value
            self.sendCommand(self.controller_value.get(), self.starting_id_value.get(
            ) + x, Command_SetColour, [random.randint(1, 255), random.randint(1, 255), random.randint(1, 255)])

            time.sleep(1)

        button_text.set("Test")  # reset button text


if __name__ == '__main__':
    root = tk.Tk()
    app = iStringLiteDevTool(root)
    root.mainloop()
