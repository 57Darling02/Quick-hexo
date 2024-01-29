import os
import re
import subprocess
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox, filedialog, Menu, simpledialog
from datetime import date, datetime
import configparser
import webbrowser
from PIL import ImageTk, Image
import hexofuc
from queue import Queue


class MainUI:
    def readconfig(self):
        self.editor_path = self.config.get('local_path', 'editor_path')
        self.hexo_folder_root_path = self.config.get('local_path', 'hexo_folder_root_path')
        self.hexo_folder_path = self.hexo_folder_root_path + "/source"
        self.model_path = self.config.get('local_path', 'model_path')

    def save(self):
        self.ui.show_popup("配置保存中..", True, True, 300)
        with open('config/config.ini', 'w', encoding='utf-8') as configfile:
            self.config.write(configfile)

    def lord_model(self, title='hello world!'):
        if self.model_path != "":
            with open(self.model_path, 'r', encoding='utf-8') as f:
                source_code = f.read()
            model_content = source_code.replace('$TIME$', datetime.now().strftime("%Y-%m-%d %H:%M:%S")).replace(
                '$TITLE$', title[:-3])
        return model_content

    def choose_editor(self):
        get_editor_path = filedialog.askopenfilename(title="选择编辑器", filetypes=[("editor files", "*.exe")])
        if get_editor_path != "" and get_editor_path.endswith('.exe'):
            self.editor_path = get_editor_path
            self.config.set('local_path', 'editor_path', self.editor_path)
            self.save()
            return True
        else:
            self.ui.show_popup("取消选择")
            return False

    def check_editor(self):  # 找到编辑器返回True
        if os.path.isfile(self.editor_path):
            filename = os.path.basename(self.editor_path)
            if filename.lower().endswith(".exe"):
                return True
        else:
            return self.choose_editor()

    def open_mdfile(self, file_path):
        if self.check_editor():  # 检查editoer
            subprocess.Popen([self.editor_path, file_path])  # 打开操作
        else:
            print("请先选择编辑器，目前支持Microsoft VS Code和Typora")
            self.choose_editor()

    def choose_hexo_folder(self):  # 选择hexo根目录
        get_hexo_folder_root_path = filedialog.askdirectory(title="选择hexo根目录")
        if get_hexo_folder_root_path != "":
            self.hexo_folder_root_path = get_hexo_folder_root_path
            self.hexo_folder_path = self.hexo_folder_root_path + "/source"
            self.config.set('local_path', 'hexo_folder_root_path', self.hexo_folder_root_path)
            self.save()
            return True
        else:
            self.ui.show_popup("取消选择")
            return False

    def check_hexo_folder(self):
        if os.path.exists(self.hexo_folder_path):
            return True
        else:
            return self.choose_hexo_folder()

    def ImageProcess(self, path, r=False, width=0, height=0):  # resources/bg1.png
        photo = Image.open(path)
        if r:
            photo = photo.resize((width, height))
        img_out = ImageTk.PhotoImage(image=photo)
        return img_out

    def create_scrollable_text_area(self, parent, text):
        # 创建一个滚动条
        scrollbar = tk.Scrollbar(parent)
        scrollbar.pack(side=tk.RIGHT, fill=tk.BOTH)
        # 创建一个文本框
        text_area = tk.Text(parent, yscrollcommand=scrollbar.set, wrap=tk.WORD, state=tk.NORMAL, autoseparators=True,
                            height=1000)
        text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=text_area.yview)
        # 将文本放入文本框
        text_area.insert(tk.END, text)
        return text_area

    def __init__(self):
        # 初始化参数
        self.model_path = None
        self.editor_path = "C:/Typora.exe"
        self.hexo_folder_path = ""
        self.model_content = ""
        self.hexo_folder_root_path = ""
        self.help_url = "57d02.cn"
        self.Author_URI = "57d02.cn"
        self.hexo = None
        # 初始化配置读取
        self.config = configparser.ConfigParser()
        self.config.read('config/config.ini', encoding='utf-8')
        # 初始化监测队列
        self.fifo_queue = Queue()

        def monitor_data_changes(hexo_running=None, hexo_server_running=None, hexo_task=None):
            if hexo_running != self.hexo.running or hexo_server_running != self.hexo.serverunning or hexo_task != self.hexo.task:
                hexo_running = self.hexo.running
                hexo_server_running = self.hexo.serverunning
                hexo_task = self.hexo.task
                updata_gui()
            else:
                pass
            if self.hexo.root_folder != self.hexo_folder_root_path:
                self.hexo.root_folder = self.hexo_folder_root_path
            while not self.fifo_queue.empty():
                all_items = ''.join([self.fifo_queue.get() for _ in range(self.fifo_queue.qsize())])
                all_items = re.sub(r'\x1b\[[0-9;]*m', ' ', all_items)
                console_area.insert(tk.END, all_items)
                console_area.see(tk.END)
                print(all_items)

            root.after(200, lambda: monitor_data_changes(hexo_running, hexo_server_running, hexo_task))  # 每200毫秒更新一次

        # 定义页面作用函数！
        def updata_gui():
            if self.hexo.serverunning:
                serverBTN.configure(image=img['start'], command=lambda: self.hexo.stop_s())
                Label_hexo_serve.configure(text="hexo server running")
            else:
                serverBTN.configure(image=img['close'], command=lambda: self.hexo.server())
                Label_hexo_serve.configure(text="hexo server 未启动")
            if not self.hexo.running:
                LabelProcess.configure(text=self.hexo.task_status)  #
                self.ui.close_popup()
            else:
                LabelProcess.configure(text=self.hexo.task)

        def updataList(parent=""):
            if listbox.get_children():
                listbox.delete(*listbox.get_children())
            populate_treeview(self.hexo_folder_path, parent)
            print("刷新列表")

        def populate_treeview(folder_path, parent=""):
            try:
                for item in os.listdir(folder_path):
                    item_path = os.path.join(folder_path, item)
                    if os.path.isdir(item_path):
                        folder_item = listbox.insert(parent, "end", text=item, open=False)
                        listbox.bind('<Double-1>', lambda event: on_double_click(event))
                        listbox.bind("<Button-3>", lambda event: on_right_click(event))  # 绑定右键点击事件
                        populate_treeview(item_path, parent=folder_item)
                    elif item.endswith(".md"):
                        # 插入 .md 文件，并为其绑定事件
                        listbox.insert(parent, "end", text=item)
                        listbox.bind('<Double-1>', lambda event: on_double_click(event))
                        listbox.bind("<Button-3>", lambda event: on_right_click(event))  # 绑定右键点击事件
            except FileNotFoundError:
                self.ui.show_popup("未找到md文件")

        def get_item_path(item):
            path = ""
            while item != "":
                path = listbox.item(item, "text") + "/" + path
                item = listbox.parent(item)
            return path

        def on_right_click(event):
            menu.post(event.x_root, event.y_root)

        def on_double_click(event):
            point = get_point()
            x, y = event.x, event.y
            item = listbox.identify_row(y)
            column = listbox.identify_column(x)
            if not item and column:
                # 点击在表头上
                print("未选择")
                updataList()
            else:
                if point["type"] != "dir" or point["path"][-7:-1] == "_posts":
                    use_editor_open()
                else:
                    print("你可以右键打开该文件夹")
                    pass

        def get_point():  # 获取选项信息
            R = {"boolean": True}  # 真不懂怎么规范命名
            selected_items = listbox.selection()  # 获取所有被点击的项
            if len(selected_items) == 1:  # 只有一个项被选中
                selected_item = get_item_path(selected_items[0])
                # print(f"Full path: {os.path.join(self.hexo_folder_path, selected_item)}")
                Full_path = os.path.join(self.hexo_folder_path, selected_item)  # 获取被点击的项的路径
                R["path"] = Full_path
                if os.path.isdir(Full_path):
                    R["type"] = "dir"
                else:
                    R["path"] = R["path"][:-1]
                    R["type"] = "file"
                return R
            else:
                R["boolean"] = False
                # messagebox.showinfo("err","不能不选，也别多选TwT")
                return R

        def use_editor_open(file=""):  # 使用编辑器打开文件或文件夹
            point = get_point()
            if point["boolean"] and point["type"] == "dir":
                result = messagebox.askyesno("？", "是否使用编辑器打开这个文件夹？")
                if result:
                    self.open_mdfile(point["path"])
                else:
                    pass
            elif point["boolean"]:
                self.open_mdfile(point["path"])
            else:
                pass

        def new_post(path=''):
            if not path:
                path = self.hexo_folder_path + '/_posts'

            nowtime = date.today().strftime("%Y%m%d")
            input_value = simpledialog.askstring("新建", "请输入filename", initialvalue=nowtime + ".md")
            if input_value != None:
                out_path = path + "/" + input_value
                if not os.path.exists(out_path):
                    model_content = self.lord_model(input_value)
                    if messagebox.askyesno("choose", "是否使用模板：\n" + model_content[:100]):
                        with open(out_path, 'w', encoding='utf-8') as file:
                            file.write(model_content)  # 写入一些内容到文件中
                        updataList()
                    else:
                        with open(out_path, 'w') as file:
                            file.write("")  # 写入一些内容到文件中
                        updataList()
                    self.open_mdfile(out_path)
                    self.ui.show_popup("开始创作吧！")
                else:
                    updataList()
                    if messagebox.askyesno("提示", "文件已存在,是否打开？"):
                        self.open_mdfile(out_path)
            else:
                pass

        def creat_new_md():
            point = get_point()
            if point["boolean"] and point["type"] == "dir":
                new_post(point['path'])
            else:
                self.ui.show_popup("选文件夹吧！懒得写了")

        def del_md():
            point = get_point()
            if point["boolean"] and point["type"] == "dir":
                self.ui.show_popup("别选文件夹！懒得写了！")
            elif point["boolean"]:
                if os.path.isfile(point["path"]):
                    os.remove(point["path"])
                    updataList()
                    self.ui.show_popup("删除成功")
                else:
                    updataList()
                    print(point["path"])
                    self.ui.show_popup("文件不存在")

        def on_closing():
            self.save()
            print("goodbye!")
            root.destroy()  # 关闭窗口

        def check():
            if self.check_editor() and self.check_hexo_folder():
                self.ui.show_popup('应该没问题')
            elif not self.check_editor() or not self.check_hexo_folder():
                pass

        # 读取配置

        # check_bash()
        root = tk.Tk()
        self.root = root
        self.ui = hexofuc.Loading_ui(root)

        root_width = 678
        root_height = 520
        root.title("hexo快速创作")
        self.hexo = hexofuc.Hexo(root, self.hexo_folder_root_path, self.fifo_queue)
        self.readconfig()

        root.iconbitmap('icons/Logo.ico')
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        # 设置窗口的位置和大小
        root.geometry('{}x{}+{}+{}'.format(root_width, root_height, int((screen_width - root_width) / 2),
                                           int((screen_height - root_height) / 2)))

        # 构造页面
        fucts_frame = tk.Frame(root, bg="#5F9F9F")
        files_frame = tk.Frame(root, bg="black")
        files_scrollbar = tk.Scrollbar(files_frame, orient="vertical")
        listbox = ttk.Treeview(files_frame, yscrollcommand=files_scrollbar.set, selectmode="browse")
        self.listbox = listbox
        menu = Menu(root, tearoff=0)
        fucts_frame.place(relwidth=0.7, relheight=1, anchor="ne", relx=1, rely=0)
        files_frame.place(relwidth=0.3, relheight=1, anchor="nw", relx=0, rely=0)
        files_scrollbar.pack(side="right", fill="y")
        listbox.heading("#0", text="/_source", anchor="w")
        listbox.tag_configure("md_file", foreground="blue")
        # listbox.bind("<Buttom-1>", on_treeview_click)
        listbox.bind('<Double-1>', lambda event: on_double_click(event))
        listbox.bind("<Button-3>", lambda event: on_right_click(event))
        listbox.pack(side="right", fill="both", expand=True)
        files_scrollbar.config(command=listbox.yview)
        menu.add_command(label="使用编辑器打开", command=lambda: use_editor_open())
        menu.add_command(label="新建md", command=lambda: creat_new_md())
        menu.add_command(label="删除md", command=lambda: del_md())
        menu.add_command(label="刷新", command=lambda: updataList())
        menu.add_command(label="选择hexo目录", command=lambda: [self.choose_hexo_folder(), updataList()])
        # 构造fuct_frame
        navigation_bar = tk.Frame(fucts_frame, bg="#F0F0F0")
        navigation_bar.pack(side="top", fill="x")
        navigation_bottom_bar = tk.Frame(fucts_frame, bg="#F0F0F0")
        navigation_bottom_bar.pack(side="bottom", fill="x")
        view_frame = tk.Frame(fucts_frame, bg="#dadada")
        view_frame.pack(side="top", fill="both", expand=True)
        # 构造 navigation_bar
        img = {}
        img["bg"] = (self.ImageProcess("resources/bg2.png", True, 76, 25))
        img["bigbg"] = (self.ImageProcess("resources/bg.png", True, 128, 60))
        img['start'] = self.ImageProcess("resources/start.png", True, 20, 12)
        img['close'] = self.ImageProcess("resources/close.png", True, 20, 12)

        # HomeLabel = tk.Button(navigation_bar,image=img["bg"],bd=0,bg=navigation_bar["bg"],compound="center",text='Home',activebackground=navigation_bar["bg"])
        # HomeLabel.grid(row=0 , column=0,padx=1,pady=5)
        checkLabel = tk.Button(navigation_bar, text="Check", command=lambda: check(), padx=18, compound="center",
                               image=img["bg"], bg=navigation_bar["bg"], bd=0, activebackground=navigation_bar["bg"])
        checkLabel.grid(row=0, column=0, padx=1, pady=5)
        HelpLabel = tk.Button(navigation_bar, text="Help", command=lambda: webbrowser.open(self.help_url), padx=18,
                              compound="center", image=img["bg"], bg=navigation_bar["bg"], bd=0,
                              activebackground=navigation_bar["bg"])
        HelpLabel.grid(row=0, column=1, padx=1, pady=5)
        AuthorLabel = tk.Button(navigation_bar, text="Author", command=lambda: webbrowser.open(self.Author_URI),
                                padx=18, compound="center", image=img["bg"], bg=navigation_bar["bg"], bd=0,
                                activebackground=navigation_bar["bg"])
        AuthorLabel.grid(row=0, column=2, padx=1, pady=5)

        setting_menu = tk.Menu(navigation_bar, tearoff=0)

        setting_menu.add_command(label="save", command=lambda: [self.save()])

        setting_menu.add_command(label="选择hexo根目录", command=lambda: [self.choose_hexo_folder()])
        setting_menu.add_command(label="选择编辑器", command=lambda: self.choose_editor())
        setting_menu.add_command(label="查看控制台输出", command=lambda: self.ui.show_popup('左下角控制台信息开关\n↙↙↙↙', True, 3000))
        settingLabel = tk.Button(navigation_bar, text="setting", padx=18,
                                 compound="center", image=img["bg"], bg=navigation_bar["bg"], bd=0,
                                 activebackground=navigation_bar["bg"])
        settingLabel.bind("<Button-1>", lambda event: [
            setting_menu.tk_popup(settingLabel.winfo_rootx() - 10, settingLabel.winfo_rooty() + 30)])
        settingLabel.grid(row=0, column=3, padx=1, pady=5)

        # navigation_botto,_bar

        def update_scroll_region():
            mainframe.configure(scrollregion=btnframe.bbox("all"))

        def console_button_fuct():
            if console_view.winfo_ismapped():
                console_view.place_forget()
                consoleBTN.configure(image=img['close'])
                mainframe.place_configure(relheight=1)
                TFvscrollbar.place_configure(relheight=1)
            else:
                console_view.place(relheight=0.25, relwidth=1, relx=0, rely=1, anchor='sw')
                consoleBTN.configure(image=img['start'])
                mainframe.place_configure(relheight=0.75)
                TFvscrollbar.place_configure(relheight=0.75)

        # tk.Label(navigation_bottom_bar, text="控制台").pack(side="left")
        consoleBTN = hexofuc.TooltipButton(navigation_bottom_bar, bg=navigation_bottom_bar["bg"], bd=0,
                                           activebackground=navigation_bottom_bar["bg"], image=img['close'],
                                           command=lambda: console_button_fuct(), text='控制台')
        consoleBTN.pack(side="left", padx=5)
        tk.Label(navigation_bottom_bar, text="执行:").pack(side="left")
        serverBTN = tk.Button(navigation_bottom_bar, bg=navigation_bottom_bar["bg"], bd=0,
                              activebackground=navigation_bottom_bar["bg"], image=img['close'],
                              command=lambda: self.hexo.server())
        serverBTN.pack(side="right", padx=5)
        LabelProcess = tk.Label(navigation_bottom_bar, text="", width=33, justify='left', anchor='nw')
        LabelProcess.pack(side="left", padx=5)
        Label_hexo_serve = tk.Label(navigation_bottom_bar, text="hexo serve未启动")
        Label_hexo_serve.pack(side="right", padx=5)
        # navigation_bar.grid_rowconfigure(0, weight=1, minsize=20)  # 设置第0行的最小大小为50
        # 构造 view_frame
        mainframe = tk.Canvas(view_frame, bg="#dadada")  # 放各种按钮
        # mainframe.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        mainframe.place(relheight=1, relwidth=0.95, rely=0, relx=0, anchor='nw')
        TFvscrollbar = tk.Scrollbar(view_frame, orient=tk.VERTICAL, command=mainframe.yview)
        TFvscrollbar.place(relheight=1, relwidth=0.05, rely=0, relx=1, anchor='ne')
        mainframe.configure(yscrollcommand=TFvscrollbar.set)
        mainframe.bind("<Configure>", lambda event: update_scroll_region())
        # mainframe.bind("<Configure>", lambda event: mainframe.configure(scrollregion=mainframe.bbox("all")))
        btnframe = tk.Frame(mainframe, bg=mainframe['bg'])
        mainframe.create_window((0, 0), window=btnframe, anchor="nw")

        def create_buttons(config):
            config = config['button_command']
            if not config:
                return []
            buttons = []
            for key, value in config.items():
                # 创建按钮
                key = key.replace('\\n', '\n')
                button = tk.Button(btnframe, image=img["bigbg"], bd=0, bg=mainframe["bg"], compound="center",
                                   padx=10, pady=20, activebackground=mainframe["bg"],
                                   text=key, command=lambda v=value: [self.hexo.domore(v),
                                                                      self.ui.show_popup('正在执行命令：\n' + str(v), False,
                                                                                         False)])
                buttons.append(button)
                button.bind("<MouseWheel>",
                            lambda event: mainframe.yview_scroll(int(-1 * (event.delta / 120)) * 1, "units"))
            return buttons

        def place_buttons(buttons):
            # 摆放按钮在布局中
            row = 0
            column = 1
            for button in buttons:
                button.grid(row=row, column=column)
                column += 1
                if column == 3:
                    column = 0
                    row += 1

        buttons = create_buttons(self.config)
        place_buttons(buttons)
        btn1 = tk.Button(btnframe, image=img["bigbg"], bd=0, bg=mainframe["bg"], compound="center", text='尝试结束进程',
                         padx=10, pady=20,
                         activebackground=mainframe["bg"], command=lambda: [self.hexo.stop_s()])
        btn1.grid(row=0, column=0)
        btn2 = tk.Button(btnframe, image=img["bigbg"], bd=0, bg=mainframe["bg"], compound="center", text='new post',
                         padx=10, pady=20,
                         activebackground=mainframe["bg"], command=lambda: [new_post()])
        btn2.grid(row=0, column=1)
        # btn3 = tk.Button(mainframe, image=img["bigbg"], bd=0, bg=mainframe["bg"], compound="center", text='启动服务\nhexo s', padx=10, pady=20,
        #                  activebackground=mainframe["bg"], command=lambda :[self.hexo.server()])
        # btn3.grid(row=0, column=2)
        # btn4 = tk.Button(mainframe, image=img["bigbg"], bd=0, bg=mainframe["bg"], compound="center", text='推送(depoly)\nhexo d',padx=10,pady=20,
        #                  activebackground=mainframe["bg"],command=lambda :[self.hexo.deploy()])
        # btn4.grid(row=1, column=0)
        # btn5 = tk.Button(mainframe, image=img["bigbg"], bd=0, bg=mainframe["bg"], compound="center", text='一键打包\ncl&&g', padx=10,
        #                  pady=20,
        #                  activebackground=mainframe["bg"],command=lambda :[self.hexo.domore("hexo cl&&hexo g")])
        # btn5.grid(row=1, column=1)
        # btn6 = tk.Button(mainframe, image=img["bigbg"], bd=0, bg=mainframe["bg"], compound="center", text='一键打包发布\ncl&&g&&d', padx=20,
        #                  pady=20,command=lambda :[self.hexo.domore("hexo cl&&hexo g&&hexo d")],
        #                  activebackground=mainframe["bg"])
        # btn6.grid(row=1, column=2)
        # btn7 = tk.Button(mainframe, image=img["bigbg"], bd=0, bg=mainframe["bg"], compound="center",
        #                  text='一键打包启动服务\ncl&&g&&s\nlocalhost:4000', padx=10,
        #                  pady=20,command=lambda :[self.hexo.domore("hexo cl&&hexo g&&hexo s",''''''),self.hexo.set_server_running(True)],
        #                  activebackground=mainframe["bg"])
        # btn7.grid(row=2, column=0)
        # btn8 = tk.Button(mainframe, image=img["bigbg"], bd=0, bg=mainframe["bg"], compound="center",
        #                  text='使用gulp\n压缩生成文件\nglup', padx=10,
        #                  pady=20,command=lambda :self.hexo.domore("gulp"),
        #                  activebackground=mainframe["bg"])
        # btn8.grid(row=2, column=1)
        # 生成自定义按钮？

        console_view = tk.Frame(view_frame, bg='red')
        console_area = self.create_scrollable_text_area(console_view, "Welcome to HEXO快速创造\n")
        console_area.place(relwidth=1, relheight=1, anchor="nw", rely=0, relx=0)

        # 执行监测
        monitor_data_changes()
        self.check_editor()
        self.check_hexo_folder()
        populate_treeview(self.hexo_folder_path)  # 初始显示根目录下的文件和文件夹
        root.protocol("WM_DELETE_WINDOW", on_closing)
        root.mainloop()
