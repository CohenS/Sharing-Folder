from sys import *
import sqlite3
import socket
import struct
import os
import shutil

DBName = "sharefolders.db"
dont_write_bytecode = True

def checkDB(path, add_to_log_list):
    #COMPARE DB FILE TO THE CONTENT OF THE FOLDER
    DBPath = os.path.join(path,DBName)
    cur_files = createList(path)
    db_files = viewDB(path)

    for f in cur_files:
        f = f.replace(path,'')
        f = f.replace('\\','',1)
        if('.' in f):
            if f.endswith(".txt"):
                r = searchDB(DBPath,f,"txt")

            else:
                r = searchDB(DBPath,f,"binary")

        else:
            r = searchDB(DBPath,f,"dir")

        if r == [] and not f.endswith(".pyc"):
            if os.path.isdir(f):
                fileTOremove = os.path.join(path,f)
                shutil.rmtree(fileTOremove)
                add_to_log_list("Dir was removed because no longer exists:")
                add_to_log_list(f)

            else:
                fileTOremove = os.path.join(path,f)
                os.remove(fileTOremove)
                add_to_log_list("File was removed because no longer exists:")
                add_to_log_list(f)

    #to check if need to delete folder after file was removed
    cur_files = createList(path) #updated list
    db_files = viewDB(path)

    for f in cur_files:
        f = f.replace(path,'')
        f = f.replace('\\','',1)

        if('.' in f):
            if f.endswith(".txt"):
                r = searchDB(DBPath,f,"txt")

            else:
                r = searchDB(DBPath,f,"binary")

        else:
            r = searchDB(DBPath,f,"dir")

        if r==[]:
            if os.path.isdir(f):
                fileTOremove = os.path.join(path,f)
                shutil.rmtree(fileTOremove)
                add_to_log_list(f'Dir was removed because no longer exists: {f}')


def connect_send(f_path, f_name,f_type,add_to_log_list):
    #Sender: send files with UDP multicast connection

    message = b'very important data'
    multicast_group = ('224.10.10.10', 10000)
    # Create the datagram socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Set a timeout so the socket does not block
    # indefinitely when trying to receive data.

    sock.settimeout(0.2)

    # Set the time-to-live for messages to 1 so they do not
    # go past the local network segment.
    ttl = struct.pack('b', 1)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)

    try:
        # Send data to the multicast group
        sentCount = sock.sendto(f_name.encode('ascii'), multicast_group)
        sock.sendto(f_type.encode('ascii'), multicast_group)
        if(f_type == 'txt'):
            file = open(os.path.join(f_path,f_name),"r")#if text file
            data_f = file.read(1024)
            sock.sendto(data_f.encode('ascii'),multicast_group)
            add_to_log_list('[+] Text file has been sent: {}'.format(f_name))
        elif(f_type == 'binary' and f_type!='pyc') :
                    file = open(os.path.join(f_path,f_name), "rb")  # if binary file
                    data_f = file.read(999999)
                    sock.sendto(data_f,multicast_group)
                    add_to_log_list('[+] Binary file has been sent: {}'.format(f_name))
        elif(f_type == 'dir'):
            add_to_log_list('[+] Dir file has been sent')

        else:
            add_to_log_list('[+] File not found!')

        # Look for responses from all recipients
        
        #while True:
        #    add_to_log_list('waiting to receive')
        #    try:
        #        data, server = sock.recvfrom(16)
        #    except socket.timeout:
        #        add_to_log_list('timed out, no more responses')
        #        break

        #    else:
        #        add_to_log_list('received {!r} from {}'
        #            .format(data, server))
        

    finally:
        sock.close()


def createList(path):
    #Create name list of all files that located on "path"
    #TODO: add files that inside folders
    filesToReturn = []
    dirs = []
    # r=root, d=directories, f = files

    for root, _, files in os.walk(path):
        if root==path:
            for file in files:
                filesToReturn.append(file)

        elif root!=os.path.join(path,'__pycache__'):
            if files!=[]:
                for file in files:
                    filesToReturn.append(os.path.join(root,file))

            else:
                filesToReturn.append(root)
    return filesToReturn

def create(path, add_to_log_list):

    #create DB of the files
    path.replace("/","\\")
    DBPath = os.path.join(path,DBName)
    add_to_log_list('Creating DB files')
    createDB(DBPath)
    files = createList(path)
    db_f=DBName
    add_to_log_list("Start to sending data to all users")
    for f in files:
        f = f.replace(path,'')
        f = f.replace('\\','',1)

        if('.' in f):
            if f!=DBName and f!='__pycache__':
                if f.endswith(".txt"):
                    insertDB(DBPath,f,"txt")
                    connect_send(path,f,"txt",add_to_log_list)

                elif f.endswith(".pyc"):
                    continue

                else:
                    insertDB(DBPath,f,"binary")
                    connect_send(path,f,"binary",add_to_log_list)

            elif f!='__pycache__':
                db_f=f#need to send it in last priority

        else:
            #dirs
            insertDB(DBPath,f,"dir")
            connect_send(path,f,"dir",add_to_log_list)

    insertDB(DBPath,db_f,"binary")
    connect_send(path,db_f,"binary",add_to_log_list)

def view_list(path):
    #create DB of the files
    DBPath = os.path.join(path,DBName)
    createDB(DBPath)
    files = createList(path)

    for f in files:
        f = f.replace(path,'')
        f = f.replace('\\','',1)

        if ('.' in f):
            if f.endswith(".txt"):
                insertDB(DBPath,f,"txt")

            elif f.endswith(".pyc"):
                continue

            else:
                insertDB(DBPath,f,"binary")

        else:
             #dirs
            insertDB(DBPath,f,"dir")


def createDB(DBPath):
    conn=sqlite3.connect(DBPath)
    cur=conn.cursor()
    cur.execute("DROP TABLE IF EXISTS sharefolder")
    cur.execute("CREATE TABLE IF NOT EXISTS sharefolder(name TEXT PRIMARY KEY,typefolder TEXT)")

    #cur.execute("CREATE TABLE IF NOT EXISTS sharefolder(name TEXT PRIMARY KEY,typefolder TEXT)")
    conn.commit
    conn.close()

def insertDB(DBPath,name,typefolder):
    conn=sqlite3.connect(DBPath)
    cur=conn.cursor()
    row = searchDB(DBPath,name,typefolder)

    if row ==[]:#check if same doc isn't exists
        cur.execute("INSERT INTO sharefolder VALUES (?,?)",(name,typefolder))
        conn.commit()

    conn.close()

def viewDB(path):

    DBPath=os.path.join(path,DBName)
    conn=sqlite3.connect(DBPath)
    cur=conn.cursor()
    cur.execute("SELECT * FROM sharefolder")
    rows=cur.fetchall()
    conn.close()

    return rows

def searchDB(DBPath,name="",typefolder=""):
    conn=sqlite3.connect(DBPath)
    cur=conn.cursor()
    cur.execute("SELECT * FROM sharefolder WHERE name=? AND typefolder=?", (name,typefolder))
    rows=cur.fetchall()
    conn.close()
    return rows

def deleteDB(DBPath,name):
    conn=sqlite3.connect(DBPath)
    cur=conn.cursor()
    cur.execute("DELETE FROM sharefolder WHERE name=?",(name,))
    conn.commit()
    conn.close()