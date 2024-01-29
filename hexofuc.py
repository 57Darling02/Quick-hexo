import datetime
import os
import subprocess
import threading
from tkinter import messagebox  # 从tkinter模块中导入messagebox，用于显示消息框。
import chardet
import tkinter as tk


class Hexo:
    def __init__(self,root,hexo_folder_root_path,fifo_queue):
        self.root = root#放tk父控件
        self.process = None  # 初始化进程变量为None。
        self.root_folder = hexo_folder_root_path
        self.running = False
        self.serverunning = False
        self.task =""
        self.task_status = ""
        self.hexo_console_text = None
        self.fifoqueue = fifo_queue

    def cmd_run(self,command="hexo",mid_do='',final_do = ''):
        global stderr, stdout
        path = self.root_folder
        self.process = subprocess.Popen(["cmd", "/c", command], cwd=path, shell=True,stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        self.task = str(command)
        while True:
            output = self.process.stdout.readline().decode('utf-8','ignore')
            if not output:
                break
            self.fifoqueue.put(output)
        try:
            if mid_do!='':
                exec(mid_do)
            self.process.wait()
            stdout, stderr = self.process.communicate()
            self.task_status = "Done"
        except KeyboardInterrupt:
            self.process.terminate()
            messagebox.showinfo("err","程序终止"+str(stderr))
        finally:
            if final_do != '':  # 如果最后一个执行的命令是hexo s，则打开浏览器
                exec(final_do)
            self.process = None
            self.running = False
    def set_server_running(self,boolean):
        self.serverunning = boolean
    def server(self):
        try:
            if not self.running:
                self.running = True
                threading.Thread(target=lambda: self.cmd_run("hexo s -p 4000")).start()
                self.serverunning = True
            else:
                self.stop_s()
                messagebox.showinfo("提示",'请等待上一个进程完成！')
        except KeyboardInterrupt:
            self.process.terminate()
            self.serverunning =False
            pass
    def stop_s(self):
        if self.running:
            if os.name == 'nt':
                subprocess.run(['taskkill', '/F', '/T', '/PID', str(self.process.pid)], shell=True)
            else:
                self.process.terminate()
            self.serverunning = False
            self.task = "stop"

    def domore(self,command,mid_do='',final_do = ''):
        if not self.running:
            self.running = True
            threading.Thread(target=lambda: self.cmd_run(command,mid_do,final_do)).start()
        else:
            messagebox.showinfo("提示", '请等待上一个进程完成！')
            pass
class HoverButton(tk.Button):
    def __init__(self, master=None, **kwargs):
        tk.Button.__init__(self, master, **kwargs)
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)

    def on_enter(self, event):
        self.show_tooltip()

    def on_leave(self, event):
        self.hide_tooltip()

    def show_tooltip(self):
        tooltip_text = self.cget("text")
        if tooltip_text:
            x, y, _, _ = self.bbox("insert")
            x += self.winfo_rootx() + 25
            y += self.winfo_rooty() - 20
            self.tooltip = tk.Toplevel(self)
            self.tooltip.wm_overrideredirect(True)
            self.tooltip.wm_geometry(f"+{x}+{y}")
            label = tk.Label(self.tooltip, text=tooltip_text, justify='left', background="#ffffe0", relief='solid', borderwidth=1, font=("Arial", "8", "normal"))
            label.pack(ipadx=1)

    def hide_tooltip(self):
        if hasattr(self, 'tooltip'):
            self.tooltip.destroy()
class ui:
    def close_popup(self):
        self.popup.withdraw()
        self.popup.grab_release()

    def show_popup(self, msg,allow_close=True, withdraw = True, duration=500):
        if allow_close:
            self.popup.protocol("WM_DELETE_WINDOW", self.close_popup)
        else:
            self.popup.protocol("WM_DELETE_WINDOW", lambda :None)

        self.popup.deiconify()
        # self.popup.grab_set()
        self.message_label.configure(text=msg)
        self.popup.lift()
        if withdraw:
            self.popup.after(duration, self.close_popup)
        else:
            pass
    def __init__(self,parent):
        self.popup = tk.Toplevel(parent)
        self.popup.protocol("WM_DELETE_WINDOW", self.close_popup)
        self.popup.title("message")
        self.popup.transient(parent)  # 将窗口声明为临时窗口，不在任务栏显示图标
        screen_width = self.popup.winfo_screenwidth()
        screen_height = self.popup.winfo_screenheight()
        x = (screen_width / 2) - (200 / 2)
        y = (screen_height / 2) - (100 / 2)
        self.popup.geometry(f"200x100+{int(x)}+{int(y)}")
        self.message_label = tk.Label(self.popup, wraplength=180)
        self.message_label.pack(expand=True)
        self.popup.withdraw()