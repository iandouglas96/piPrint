import xmlrpclib
import time
import Tkinter, tkFont, tkFileDialog, ttk
import thread
from os import path
from socket import error as socket_error

proxy = xmlrpclib.ServerProxy("http://192.168.1.76:8000/")
getinfoproxy = xmlrpclib.ServerProxy("http://192.168.1.76:8000/") #Use 2 proxies, one for sending, one for getting

file_opt = options = {}
options['defaultextension'] = '.txt'
options['filetypes'] = [('all files', '.*'), ('gcode files', '.gcode')]
options['initialdir'] = '~'
options['title'] = 'Choose file to upload'

filepath = "./"
filename = "."

def get_path():
    global filepath
    global filename
    filepath = tkFileDialog.askopenfilename(**file_opt)
    filename = path.basename(filepath)
    pathtext.set(filename)

def show_temp():
	while True:
		try:
			data = getinfoproxy.get_info()
			temptext.set(str(data[0])+"C")
			timetext.set(time.strftime("%T"))
			if (data[2] == 0):
				progress.set(0)
				progtext.set("Not Printing")
			else:
 				progress.set((data[1]*100)//data[2])
				progtext.set("Line "+str(data[1])+"/"+str(data[2])+" "+str((data[1]*100)//data[2])+"%")
			if (data[3]): #Are we heating?
				templabel.configure(fg = "red")
			else:
				templabel.configure(fg = "black")
		except socket_error:
			timetext.set("Connection Lost")
		time.sleep(1)
		
def set_temp():
	if not proxy.set_temp(int(tempfield.get())):
		print "Error"
		
def move_x(dir):
	if not proxy.x_step(10*dir):
		print "Error"
	
def move_y(dir):
	if not proxy.y_step(10*dir):
		print "Error"
	
def move_z(dir):
	if not proxy.z_step(10*dir):
		print "Error"
	
def move_e(dir):
	if not proxy.e_step(10*dir):
		print "Error"
	
def upload_file():
	with open(filepath, "rb") as handle:
		binary_data = xmlrpclib.Binary(handle.read())
	proxy.server_receive_file(filename,binary_data)

def start_print():
	proxy.print_file(filename)
	
def stop_print():
	proxy.stop_print()

root = Tkinter.Tk()
root.wm_title("piPrint")
root.geometry("500x200")
font = tkFont.Font(family="Helvetica", size=15, weight="bold")
temptext = Tkinter.StringVar()
templabel=Tkinter.Label(root,textvariable=temptext, font=font)
temptext.set("0C")
templabel.grid(row=1, column=4)
timetext = Tkinter.StringVar()
timelabel=Tkinter.Label(root,textvariable=timetext, font=font)
timetext.set("00:00:00")
timelabel.grid(row=0, column=4)

xposbutton=Tkinter.Button(root, text="+X", repeatdelay=500, repeatinterval=10, command=lambda: move_x(1))
xposbutton.grid(row=0, column=0)
xnegbutton=Tkinter.Button(root, text="-X", repeatdelay=500, repeatinterval=10, command=lambda: move_x(-1))
xnegbutton.grid(row=1, column=0)

yposbutton=Tkinter.Button(root, text="+Y", repeatdelay=500, repeatinterval=10, command=lambda: move_y(1))
yposbutton.grid(row=0, column=1)
ynegbutton=Tkinter.Button(root, text="-Y", repeatdelay=500, repeatinterval=10, command=lambda: move_y(-1))
ynegbutton.grid(row=1, column=1)

zposbutton=Tkinter.Button(root, text="Up", repeatdelay=500, repeatinterval=10, command=lambda: move_z(1))
zposbutton.grid(row=0, column=2)
znegbutton=Tkinter.Button(root, text="Down", repeatdelay=500, repeatinterval=10, command=lambda: move_z(-1))
znegbutton.grid(row=1, column=2)

eposbutton=Tkinter.Button(root, text="Extrude", repeatdelay=500, repeatinterval=10, command=lambda: move_e(1))
eposbutton.grid(row=0, column=3)
enegbutton=Tkinter.Button(root, text="Retract", repeatdelay=500, repeatinterval=10, command=lambda: move_e(-1))
enegbutton.grid(row=1, column=3)

chgtemplabel=Tkinter.Label(root, text='Temp to Set:')
chgtemplabel.grid(row=2, column=0)
tempfield=Tkinter.Entry(width=4)
tempfield.insert(Tkinter.END, "0")
tempfield.grid(row=2, column=1)
settempbutton=Tkinter.Button(root, text="Set", command=set_temp)
settempbutton.grid(row=2, column=2)

browsebutton=Tkinter.Button(root, text="Browse", command=get_path)
browsebutton.grid(row=3, column=0)

uploadbutton=Tkinter.Button(root, text="Upload File", command=upload_file)
uploadbutton.grid(row=3, column=1)

printbutton=Tkinter.Button(root, text="Print", command=start_print)
printbutton.grid(row=3, column=2)

stopbutton=Tkinter.Button(root, text="Kill Print", command=stop_print)
stopbutton.grid(row=3, column=3)

pathtext = Tkinter.StringVar()
filelabel=Tkinter.Label(root,textvariable=pathtext, font=font, width=20)
pathtext.set("No File Selected")
filelabel.grid(row=3, column=4)

progress = Tkinter.IntVar()
progressbar = ttk.Progressbar(orient=Tkinter.HORIZONTAL, length=480, mode="determinate", variable=progress)
progressbar.grid(row=4, column=0, columnspan=5)

progtext = Tkinter.StringVar()
proglabel=Tkinter.Label(root,textvariable=progtext, font=font)
progtext.set("Not Printing")
proglabel.grid(row=5, column=0, columnspan=5)

thread.start_new_thread(show_temp, ())
root.mainloop()