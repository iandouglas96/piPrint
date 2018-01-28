# NOTE:
piPrint development ceased a while ago.  I no longer have the hardware that this code was built to run.  Consider the code unsupported and undeveloped, though feel free to still email me with questions.

# piPrint (v0.3a)
## Run your 3D Printer with only a Raspberry Pi

Ian D. Miller
info [at] pxlweavr [dot] com
http://www.pxlweavr.com

Kenan Bitikofer
kbitikofer [at] gmail [dot] com

## Warning
piPrint is currently under heavy development.  It seems to be working fairly well at the moment, but is not considered stable.  If you just want to get a 3D Printer up and running, consider looking at other options at http://www.reprap.org.

## Documentation
A video of piPrint in action is here: http://youtu.be/JW6yJvLF7Jk  It gives a general ideas of the capabilites and interface of the printer.

Put the files contained in the server directory on the pi.  Edit server.py to change the ip address at the bottom to whatever the pi's address is.  If using a different thermistor from the Honeywell 100K, update the temp lookup table in TempSensor.py.  Pin assignments can also be set at the top of server.py.  When this configuration is complete, run

    sudo python server.py
    
It isn't a bad idea to add this to your .profile to run on startup.

In piPrintControl.py, change the top two ip addresses to the address of your pi, then, on another computer, run

    python piPrintControl.py
    
You will then be able to remotely control the printer over the local network.

NEW: piPrint now supports laser engraving.  To engrave, hook up a laser driver circuit to the hotend pins.  Files with the .ngc extension are assumed to be laser engraving files from Inkscape GCodeTools, and will be treated accordingly.
