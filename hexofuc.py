import os
import threading
import time
import webbrowser
from tkinter import messagebox  # 从tkinter模块中导入messagebox，用于显示消息框。
import subprocess
import datetime
class Hexo:
    def __init__(self,root,hexo_folder_root_path):
        self.root = root#放tk父控件
        self.process = None  # 初始化进程变量为None。
        self.root_folder = hexo_folder_root_path
        self.running = False
        self.serve = False
    def get_time(self):
        return datetime.datetime.now().strftime("%Y%m%d")

    def cmd_run(self,command="hexo"):
        global stderr, stdout
        path = self.root_folder
        self.process = subprocess.Popen(["cmd", "/c", command], cwd=path, shell=True)
        try:
            self.process.wait()
            stdout, stderr = self.process.communicate()
        except KeyboardInterrupt:
            self.process.terminate()
            messagebox.showinfo("err","程序终止"+str(stderr))
        finally:
            messagebox.showinfo("info",str(stdout)+str(stderr))
            self.process = None
            self.running = False
    def cl(self):
        if not self.running:
            self.running = True
            threading.Thread(target=lambda :self.cmd_run("hexo cl")).start()
        else:
            messagebox.showinfo("提示",'请等待上一个进程完成！')
    def generate(self):
        if not self.running:
            self.running = True
            threading.Thread(target=lambda :self.cmd_run("hexo g")).start()
        else:
            messagebox.showinfo("提示",'请等待上一个进程完成！')
    def sever(self):
        try:
            if not self.running:
                self.running = True
                threading.Thread(target=lambda: self.cmd_run("hexo s -p 4000")).start()
                self.serve = True
                # self.ro

            else:
                self.stop_hexo_s()
                # messagebox.showinfo("提示",'请等待上一个进程完成！')
        except KeyboardInterrupt:
            self.process.terminate()
            pass
    def stop_hexo_s(self):
        if os.name == 'nt':
            subprocess.run(['taskkill', '/F', '/T', '/PID', str(self.process.pid)], shell=True)
        else:
            self.process.terminate()

    def deploy(self):
        if not self.running:
            self.running = True
            threading.Thread(target=lambda :self.cmd_run("hexo d")).start()
        else:
            messagebox.showinfo("提示",'请等待上一个进程完成！')

    def domore(self,command):
        if not self.running:
            self.running = True
            threading.Thread(target=lambda: self.cmd_run(command)).start()
        else:
            messagebox.showinfo("提示", '请等待上一个进程完成！')
