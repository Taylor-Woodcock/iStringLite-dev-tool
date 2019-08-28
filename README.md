# iStringLite-dev-tool
A development tool to interface with MK-Illumination iStringLite network attached LEDs.

This was made to help readdress strings of LEDs. While attaching together two strings where IDs range from 1-40 x 2, a solution was needed to readdress the LEDs to 1-80. In the future, I intend to implement all commands to provide a powerful, lightweight developer tool for the scarcely documented iStringLites.

## Preview
![preview](https://i.imgur.com/ntHVp4A.png)

## Commands
| Command Byte  | Dommand Description | Implemented |
| ------------- | ------------- | ------------- |
| 0x00 | Command_Update_1bit | No |
| 0x01 | Command_AddressMap | No |
| 0x04 | Command_Update_8bit | No |
| 0x05 | Command_AvailableIDs | No |
| 0x06 | Command_Readdress | No |
| 0x07 | Command_Update_8bitGreyscale | No |
| 0x08 | Command_Update_16bit | No |
| 0x0C | Command_Update_24bit | No |
| 0x10 | Command_SetColour | No |
| 0x13 | Command_Reset | No |
| 0x14 | Command_DynamicReaddress | Yes |
| 0x15 | Command_SetDeviceType | No |
| 0x16 | Command_EnablePowerLine | No |
| 0x20 | Command_Configure | Partial |
| 0x21 | Command_SetOutputMode | No |
| 0x22 | Command_SetPWMOutputLevel | No |
| 0x23 | Command_DynamicReaddressType | No |
| 0x24 | Command_WriteEffectBlock | No |
| 0x25 | Command_KeepAlive | No |
| 0x26 | Command_EffectTrigger | No |

## Notes
Its worth noting Python isn't my strong suit. That said, I felt Python would best suit this project to allow for cross platform support while on the field.

This project uses tkinter and is intended to run on **Python 3** and above.
