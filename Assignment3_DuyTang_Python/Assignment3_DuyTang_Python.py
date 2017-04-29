import tkinter as tk
from tkinter.messagebox import *
import socket as sk
import sqlite3 as db
import threading
import time
import tkinter.ttk as ttk

class PortScannerDAL:
    def __init__(self):
        self.is_conn_open = False
        self.__connect_()
    def __connect_(self):
        if not self.is_conn_open:
            self.conn = db.connect('PortScanner.sqlite3')
            self.conn.row_factory = db.Row
            self.cur = self.conn.cursor()
            self.is_conn_open = True
    def read_host(self, host_ip, host_name = None):
        if host_name==None:
            self.cur.execute('select * from Host where HostIP=?',(host_ip,))
        else:
            self.cur.execute('select * from Host where HostName=? and HostIP=?',(host_name,host_ip))
        return self.cur.fetchall()
    def create_host(self, host_ip, host_name):
        # check if a host is already in the database
        self.cur.execute('select * from Host where HostName=? and HostIP=?',(host_name,host_ip))
        if len(self.cur.fetchall())==0:
            print("inserted")
            self.cur.execute('INSERT INTO Host (HostName,HostIP) VALUES(?, ?)', (host_name, host_ip))
            self.conn.commit()
        self.cur.execute('select * from Host where HostName=? and HostIP=?',(host_name,host_ip))
        return self.cur.fetchone()
    def create_scan(self, host_id):
        curtime=time.ctime(time.time())
        self.cur.execute('INSERT INTO Scan (HostId,ScanStartTime) VALUES(?,?)', (host_id,curtime))
        self.conn.commit()
        self.cur.execute('select * from Scan where HostID=? and ScanStartTime=?',(host_id,curtime))
        return self.cur.fetchone()
    def update_scan_end_time(self, scan_id):
        self.cur.execute('UPDATE Scan SET ScanEndTime=? WHERE ScanId=?', (time.ctime(time.time()), scan_id))
        self.conn.commit()
        pass
    def read_port_status(self, host_ip, host_name):
        self.cur.execute('SELECT ps.*, s.ScanStartTime FROM PortStatus ps JOIN Scan s on ps.ScanId = s.ScanId JOIN Host h on h.HostId = s.HostId WHERE h.HostIP = ? AND h.HostName = ?',(host_ip,host_name))
        return self.cur.fetchall()
    def create_port_status(self, scan_id, port, is_open):
        self.cur.execute('INSERT INTO PortStatus VALUES(?,?,?)',(scan_id,port,is_open))
        self.conn.commit()
    def __close_connection_(self):
        if self.is_conn_open:
            self.conn.commit()
            self.conn.close()
            self.is_conn_open = False
    def __del__(self):
        self.__close_connection_() 

class ResultsDialog(tk.Toplevel):
    def __init__(self, master, host_ip, host_name):
        tk.Toplevel.__init__(self,master)
        self.title('Result for host: {}/ IP address: {}'.format(host_name, host_ip))
        self.frame=tk.Frame(self)
        self.frame.pack(expand=True, fill=tk.BOTH, side=tk.TOP)
        self.treeview = ttk.Treeview(self.frame)
        self.treeview['columns'] = ('PortNumber','IsPortOpen' ,'ScanStartTime')
        #self.treeview['displaycolumns'] = ('PortNumber','IsPortOpen' ,'ScanStartTime')
        self.treeview.heading('#0', text='Scan Id')
        self.treeview.heading('PortNumber', text='Port Number')
        self.treeview.heading('IsPortOpen', text='Is Open')
        self.treeview.heading('ScanStartTime', text='Scan Time')
        self.treeview.pack(expand=True, fill=tk.BOTH, side=tk.LEFT)
        self.dal=PortScannerDAL()
        rows=self.dal.read_port_status(host_ip,host_name)
        for row in self.treeview.get_children():
            self.treeview.delete(row)
        for row in rows:
            self.treeview.insert('',tk.END,text=row['ScanId'],values = (row['PortNumber'], 'No' if row['IsPortOpen']==0 else 'Yes', row['ScanStartTime']))
        del self.dal

class PortScanner:
    def __init__(self):
        self.minport=0
        self.maxport=1023
        self.master=tk.Tk()
        self.top=tk.Toplevel(self.master)
        self.master.withdraw()
        self.__update_host_name()
        self.__init_gui()
    def __init_gui(self):
        self.top.title('Port Scanner')
        self.top.resizable(width=False, height=False)
        frame1=tk.Frame(self.top)
        frame1.pack(side=tk.TOP,expand=True,fill=tk.X)
        iplabel=tk.Label(frame1,text="Host IP:",width=15)
        iplabel.pack(side=tk.LEFT)
        self.ipvar=tk.StringVar(value=self.IP_address)
        self.ipentry=tk.Entry(frame1,textvariable=self.ipvar)
        self.ipentry.pack(side=tk.RIGHT)
        frame2=tk.Frame(self.top)
        frame2.pack(side=tk.TOP,expand=True,fill=tk.X)
        hostlabel=tk.Label(frame2, text = 'Host name:',width=15)
        hostlabel.pack(side=tk.LEFT)
        self.hostnamelb=tk.Label(frame2,text=self.hostname)
        self.hostnamelb.pack()
        frameb=tk.Frame(self.top)
        frameb.pack(side=tk.TOP,expand=True,fill=tk.X)
        self.scan= tk.Button(frameb,text= 'Scan',width=20,command=self.__start_scanner)
        self.scan.pack(side=tk.RIGHT)
        frameb=tk.Frame(self.top)
        frameb.pack(side=tk.TOP,expand=True,fill=tk.X)
        self.viewRes= tk.Button(frameb,text= 'View results',width=20,command=self.__view_results)
        self.viewRes.pack(side=tk.RIGHT)
        frame3=tk.Frame(self.top)
        frame3.pack(side=tk.TOP,expand=True,fill=tk.X)
        self.status=tk.Label(frame3,text='Scanner is idle',anchor='w')
        self.status.pack(side=tk.LEFT)
        self.master.mainloop()

    def __start_scanner(self):
        self.scan['state']=tk.DISABLED
        self.IP_address=self.ipvar.get()
        print(self.IP_address)
        try:
            temp=sk.gethostbyaddr(self.IP_address)
            print(temp)
            self.hostname=temp[0]
            self.hostnamelb['text']=self.hostname
            t=threading.Thread(target=self.start_scanner)
            t.start()
        except sk.herror:
            print('Error connecting to the IP')
            showerror('Error','Cannot connect to IP address')
            self.scan['state']=tk.NORMAL
        
    def start_scanner(self):
        self.dal=PortScannerDAL()
        id=self.dal.create_host(self.IP_address,self.hostnamelb['text'])['HostId']
        print(id)
        self.scanid=self.dal.create_scan(id)[0]
        print(self.scanid)
        for i in range(self.minport,self.maxport+1):
            self.scan_port(i)
        self.dal.update_scan_end_time(self.scanid)
        #back to idle state
        self.status['text']='Finished Scanning'
        self.scan['state']=tk.NORMAL
        del self.dal
        

    def scan_port(self, port):
        self.status['text']='Scanning port number {}'.format(port)
        s = sk.socket(sk.AF_INET,sk.SOCK_STREAM)
        isopen=1 if s.connect_ex((self.IP_address,port))==0 else 0
        s.close()
        self.dal.create_port_status(self.scanid,port,isopen)

    def __view_results(self):
        res=ResultsDialog(self.top,self.IP_address,self.hostname)

    def __update_host_name(self):
        self.IP_address=sk.gethostbyname(sk.gethostname())
        self.hostname=sk.gethostbyaddr(self.IP_address)[0]

if __name__ == '__main__':
    ps = PortScanner()