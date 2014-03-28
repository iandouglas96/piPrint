# piPrint (v0.1a)
## Run your 3D Printer with only a Raspberry Pi

Ian D. Miller
info [at] pxlweavr [dot] com
http://www.pxlweavr.com

Kenan Bitikofer

## Warning
piPrint is currently under heavy development.  It seems to be working fairly well at the moment, but is not considered stable.  If you just want to get a 3D Printer up and running, consider looking at other options at http://www.reprap.org.

## Documentation
Put the files contained in the server directory on the pi, then run

    sudo python server.py
    
It isn't a bad idea to add this to your .profile to run on startup

In piPrintControl.py, change the top two ip addresses to the address of your pi, then run

    python piPrintControl.py
    
You will then be able to remotely control the printer over the local network.