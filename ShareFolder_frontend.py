import sys

sys.dont_write_bytecode = True

from tkinter import *

import tkinter.font as t_font

import ShareFolder_backend 

import threading

import socket

import struct

import os

import errno

import time

import tkinter.filedialog as filedialog

import tkinter as tk

from tkinter import messagebox

from pip import * 





class Main_Application(tk.Frame):

    def __init__(self, master):

        self.master = master

        tk.Frame.__init__(self, self.master)

        self.dbPath = 0

        self.configure_gui()

        self.create_widgets()

        self.thread_stoped = False

    def configure_gui(self):

        self.master.title("Folder Sharing Program - selecting a Path")



    def create_widgets(self):

        

        WINDOW_SIZE = "550x150"

        master = self.master

        master.geometry (WINDOW_SIZE)

        helv = t_font.Font(family='Helvetica', size=20, weight='bold')

        #photo = 'runic.ico'

        #master.iconbitmap(photo)

       # photo=PhotoImage(file="/Users/shuycohen/Documents/Open University/commuication project/LATEST/folder.gif")

        self.input_path_label = tk.Label(master, text="Hello User!"+"\n Please Choose Shared Folder Path:")

        self.input_path_label.grid(row=1,column=10)

        self.input_entry = tk.Entry(master, text="", width=50)

        self.input_entry.configure(state='readonly')

        self.input_entry.grid(row=3,columnspan=20,column=0)

        self.browse1 = tk.Button(master, text="Browse", command=self.prompt_user_to_input_directory)

        #self.browse1.config(image=photo)

        self.browse1.grid(row=3,column=21)

        self.begin_button = tk.Button(master, text='Begin!',font=helv,command= self.FileShareScreen,state=DISABLED)

        self.begin_button.grid(row=8, column=10)

        self.spacer = tk.Label(master, text=" ")

        self.spacer.grid(row=5,column=0)



    def prompt_user_to_input_directory(self):

        input_path = tk.filedialog.askdirectory()

        self.input_entry.configure(state='normal')

        self.input_entry.delete(1, tk.END)  # Remove current text in entry

        self.input_entry.insert(0, input_path)  # Insert the path

        self.dbPath = input_path

        self.input_entry.configure(state='readonly')

        self.folder_sharing_directory=input_path

        self.begin_button.configure(state='normal')



    def refresh_fileList(self):

        self.list1.delete(0,END)

        rows = ShareFolder_backend.viewDB(self.folder_sharing_directory)

        for row in rows:

            self.list1.insert(END, row)



    def add_to_log_list(self, logItem):

        

        self.list2.insert(0, logItem)



    def open_folder_command(self):

        pathToOpen=self.folder_sharing_directory

        path=os.path.realpath(pathToOpen)

        os.startfile(path)



    def run_command(self):

        ShareFolder_backend.create(self.folder_sharing_directory, self.add_to_log_list)

        self.refresh_fileList()

        self.stop_b.configure(state='normal')

        self.refresh_b.configure(state='normal')

        self.run_b.configure(state = DISABLED)

        if(self.thread_stoped):
            run_thread_multicasat(self, 1)


    def refresh_command(self):

        ShareFolder_backend.create(self.folder_sharing_directory, self.add_to_log_list)

        self.refresh_fileList()



    def stop_command(self):

        self.thread.stop()

        self.add_to_log_list("Receving thread was stopped, to continue recieve files please press on RUN button")

        self.run_b.configure(state='normal')

        self.stop_b.configure(state = DISABLED)

        self.refresh_b.configure(state = DISABLED)

        self.thread_stoped = True


    def exit_command(self):

        self.master.os._exit(0)



    def FileShareScreen(self):

        master = self.master

        master.withdraw()

        WINDOW_SIZE = "600x300"

        window = tk.Toplevel(master)

        window.geometry(WINDOW_SIZE)

        window.title("Folder Sharing Program")



        #run button

        self.run_b=Button(window,text="Run",width=12,command=self.run_command)

        self.run_b.grid(row=1,column=0)

        


        #stop button

        self.stop_b=Button(window,text="Stop",width=12,command=self.stop_command,state=DISABLED)

        self.stop_b.grid(row=2,column=0)

        

        #refresh button

        self.refresh_b=Button(window,text="Refresh",width=12,command=self.refresh_command,state=DISABLED)

        self.refresh_b.grid(row=1,column=1)



        #open directory

        self.open_folder_b=Button(window, text="open folder", width=12, command=self.open_folder_command)

        self.open_folder_b.grid(row=2,column=1)

        self.l1=Label(window,text="Folder Name:")

        self.l1.grid(row=4,column=0,columnspan=2)



        #self.l2=Label(window,text="File Type:")

        #self.l2.grid(row=4,column=1)



        #files names

        self.files_list = tk.Label(window, text="Files Shared:")

        self.files_list.grid(row=3,column=0,sticky=W)

        self.list1=Listbox(window, height=6,width=65,bd=1)

        self.list1.grid(row=4,column=0,rowspan=6,columnspan=3)

        self.sb1=Scrollbar(window)

        self.sb1.grid(row=4,column=3,rowspan=3)

        self.list1.configure(yscrollcommand=self.sb1.set)

        self.sb1.configure(command=self.list1.yview)





        #status update list

        self.status_update = tk.Label(window, text="Current Status:")

        self.status_update.grid(row=10,column=0,sticky=W)

        self.list2=Listbox(window, height=6,width=65,bd=1)

        self.list2.grid(row=11,column=0,rowspan=10,columnspan=3)

        self.sb2=Scrollbar(window)

        self.sb2.grid(row=11,column=3,rowspan=3)

        self.list2.configure(yscrollcommand=self.sb2.set)

        self.sb2.configure(command=self.list2.yview)


        #running

        self.thread = run_thread_multicasat(self, 1)

        window.protocol("WM_DELETE_WINDOW",on_closing_and_deleteDB)





class run_thread_multicasat(object):

    #Run recieve multicast script in backround

    def __init__(self, master, interval):

        self.path = master.folder_sharing_directory

        self.master = master

        stop_thread_milticast = False

        self.interval=interval

        self._stop = threading.Event()

        thread=threading.Thread(target=self.run,args=())

        thread.deamon=True

        thread.start()



    def add_to_log_list(self, logItem):

        self.master.add_to_log_list(logItem)



    def stop(self):

        self._stop.set()
       


    def stopped(self):

        return self._stop.isSet()



    def run(self):

        #Reciver: recive files with UDP mulicast connection

            multicast_group = '224.10.10.10'

            server_address = ('', 10000)



            # Create the socket

            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

            # Bind to the server address

            sock.bind(server_address)

            # Tell the operating system to add the socket to

            # the multicast group on all interfaces.



            group = socket.inet_aton(multicast_group)

            mreq = struct.pack('4sL', group, socket.INADDR_ANY)

            sock.setsockopt(

                socket.IPPROTO_IP,

                socket.IP_ADD_MEMBERSHIP,

                mreq

            )

            self.add_to_log_list('\nWaiting to receive files')
            host_name = socket.gethostname()
            
            while True:

                if not self.stopped():

                    try:

                        

                        #for view in the window

                        c,addr = sock.recvfrom(1024)

                        d,addr = sock.recvfrom(1024)
                        if(socket.gethostbyname(host_name)!=addr[0] ):
                            self.add_to_log_list('\nStart to receive file...')

                        f_name = c.decode('ascii')

                        f_type = d.decode('ascii')

                        #create file on relevant path

                        DBPath_name = os.path.join(self.path, f_name)

                        if ('\\'  in f_name) or f_type == 'dir':

                            new_dir = f_name.split('\\')


                            cur_dir = self.path

                            

                            for a in new_dir:

                                if ('.' not in a):

                                    cur_dir = os.path.join(cur_dir,a)

                            

                            if not os.path.isdir(cur_dir):

                                        os.makedirs(cur_dir)



                        if(f_type ==  'txt'):

                            e,addr = sock.recvfrom(1024)

                            file = open(DBPath_name,"w")

                            data = e.decode('ascii')

                            file.write(data)

                            file.close()

                        elif(f_name == 'sharefolders.db'):

                            e,addr = sock.recvfrom(999999)

                            file = open(DBPath_name, "wb")

                            data = e

                            file.write(data)

                            file.close()

                            ShareFolder_backend.checkDB(self.path, self.master.add_to_log_list)

                            self.master.refresh_fileList()

                            

                        elif(f_type == 'binary' and f_type!='pyc'):

                            e,addr = sock.recvfrom(999999)

                            file = open(DBPath_name, "wb")

                            data = e

                            file.write(data)

                            file.close()

                        else:

                            self.add_to_log_list('File type is unknown!')


                        if(socket.gethostbyname(host_name)!=addr[0] ):
                            self.add_to_log_list('Received {} bytes from {}'.format(len(c), addr[0]))
                            self.add_to_log_list('For file: {}'.format(c))
                        sock.sendto(b'ack', addr)





                    except Exception:

                        if not self.stopped():

                            

                            multicast_group = '224.10.10.10'

                            server_address = ('', 10000)

                            # Create the socket

                            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)



                            # Bind to the server address

                            sock.bind(server_address)



                            # Tell the operating system to add the socket to

                            # the multicast group on all interfaces.

                            group = socket.inet_aton(multicast_group)

                            mreq = struct.pack('4sL', group, socket.INADDR_ANY)

                            sock.setsockopt(

                                socket.IPPROTO_IP,

                                socket.IP_ADD_MEMBERSHIP,

                                mreq

                            )
                            self.add_to_log_list('\nWaiting to receive files')

                else:
                    return




def on_closing_and_deleteDB():



        if messagebox.askokcancel("Quit", "Do you want to quit?"):

            root.destroy()

            fileToRemove = os.path.join(main_app.dbPath,"sharefolders.db")

            pycToRemove = os.path.join(main_app.dbPath,"__pycache__")

            if os.path.isfile(fileToRemove):

                os.remove(fileToRemove)



            if os.path.isdir(pycToRemove):

                os.remove(pycToRemove)



            os._exit(0)





def on_closing():



        if messagebox.askokcancel("Quit", "Do you want to quit?"):

            root.destroy()

            os._exit(0)





if __name__ == '__main__':

   root = tk.Tk()

   main_app = Main_Application(root)

   root.protocol("WM_DELETE_WINDOW",on_closing)

   root.mainloop()