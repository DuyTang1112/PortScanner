import tkinter as tk
import socket as sk
import sqlite3 as db
import threading
import time
import tkinter.ttk as ttk

class PortScannerDAL:
    def __init__(self):
        pass
    def __connect_(self):
        pass
    def read_host(self, host_ip, host_name = None):
        pass
    def create_host(self, host_ip, host_name):
        pass
    def create_scan(self, host_id):
        pass
    def update_scan_end_time(self, scan_id):
        pass
    def read_port_status(self, host_ip, host_name):
        pass
    def create_port_status(self, scan_id, port, is_open):
        pass
    def __close_connection_(self):
        pass
    def __del__(self):
        pass

class ResultsDialog(tk.Toplevel):
    def __init__(self, master, host_ip, host_name):
        pass

class PortScanner:
    def __init__(self):
        pass
    def __init_gui(self):
        pass
    def __start_scanner(self):
        pass
    def start_scanner(self):
        pass
    def scan_port(self, port):
        pass
    def __view_results(self):
        pass
    def __update_host_name(self):
        pass
if __name__ == '__main__':
    ps = PortScanner()