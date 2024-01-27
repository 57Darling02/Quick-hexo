import os
import subprocess
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox,filedialog,Menu,simpledialog
from datetime import date, datetime
import configparser
import webbrowser
from PIL import ImageTk, Image, ImageSequence
import hexofuc
from queue import Queue
editor_path ="C:/Typora.exe"
hexo_folder_path =""
model_content = ""
hexo_folder_root_path =""
config = configparser.ConfigParser()
config.add_section('local_path')
help_url = "57d02.cn"
Author_URI = "57d02.cn"
def readConfig():
    global editor_path
    global hexo_folder_path
    global model_content
    global hexo_folder_root_path
    global bash_path
    config.read('config.ini')
    editor_path = config.get('local_path', 'editor_path')
    hexo_folder_root_path =config.get('local_path', 'hexo_folder_root_path')
    hexo_folder_path = hexo_folder_root_path+"/source"
    model_path = config.get('local_path', 'model_path')
    # print(editor_path,hexo_folder_path)
    if model_path !="":
        with open('./model.md', 'r',encoding='utf-8') as f:
            source_code = f.read()
        model_content = source_code.replace('$TIME$', datetime.now().strftime("%Y-%m-%d %H:%M:%S"))  # 替换文本
        # 将修改后的内容写入新的md文件
        # print(model_content)
    return hexo_folder_root_path
readConfig()
def choose_editor():
    global editor_path
    # print(editor_path)
    editor_path = filedialog.askopenfilename(title="选择编辑器", filetypes=[("editor files", "*.exe")])
    if editor_path!="":
        config.set('local_path', 'editor_path', editor_path)
    else:
        editor_path ="?"
def check_editor():#找到编辑器返回True
    if os.path.isfile(editor_path):
        return True
    elif editor_path=="?":
        return False
    else:
        messagebox.showinfo("?","编辑器路径错误，请选择你的Microsoft VS Code目录下下Code.exe或者Typora目录下的Typora.exe\n快捷方式亦可")
        choose_editor()
        return check_editor()
def open_mdfile(file_path):
    if check_editor():#检查editoer
        subprocess.Popen([editor_path, file_path])#打开操作
    else:
        print("请先选择编辑器，目前支持Microsoft VS Code和Typora")
        choose_editor()
def choose_hexo_folder():   #选择hexo根目录
    global hexo_folder_path
    global hexo_folder_root_path
    hexo_folder_root_path = filedialog.askdirectory(title="选择hexo根目录")
    if hexo_folder_root_path !="":
        hexo_folder_path = hexo_folder_root_path + "/source"
        config.set('local_path', 'hexo_folder_root_path', hexo_folder_root_path)
        print("Selected source folder:", hexo_folder_path)
    else:
        messagebox.showinfo("提示","取消选择")

    return hexo_folder_path
def check_hexo_folder():
    if os.path.exists(hexo_folder_path):
        # print("hexo_folder正常")
        return True
    elif hexo_folder_root_path !="":
        choose_hexo_folder()
        return check_hexo_folder()
    else:
        return False
def ImageProcess(path,r=False,width = 0,height = 0):# assets/bg1.png
    photo = Image.open(path)
    if r:
        photo = photo.resize((width, height))
    img_out = ImageTk.PhotoImage(image=photo)
    return img_out
def init():

    def monitor_data_changes():
        while not gui_queue.empty():
            updata_gui()
            root.after(100, updata_gui)  # 每100毫秒更新一次
    #定义页面作用函数！
    def updata_gui():
        if hexo.serve:
            btn3.configure(text="关闭服务\ncrtl+C",command=lambda :hexo.stop_hexo_s())
        else:
            btn3.configure(text="启动服务\nhexo s", command=lambda: hexo.sever())
    def updataList(parent=""):
        if listbox.get_children():
            listbox.delete(*listbox.get_children())
        populate_treeview(hexo_folder_path,parent)
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
            messagebox.showinfo("这是提示信息", "未找到md文件")
    def get_item_path(item):
        path = ""
        while item != "":
            path = listbox.item(item, "text") + "/" + path
            item = listbox.parent(item)
        return path

    def on_right_click(event ):
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
                print(point["path"][-7:])
    def get_point():#获取选项信息
        R = {"boolean":True}#真不懂怎么规范命名
        selected_items = listbox.selection()  # 获取所有被点击的项
        if len(selected_items) == 1:  # 只有一个项被选中
            selected_item = get_item_path(selected_items[0])
            print(f"Full path: {os.path.join(hexo_folder_path, selected_item)}")
            Full_path = os.path.join(hexo_folder_path, selected_item)  # 获取被点击的项的路径
            R["path"]=Full_path
            if os.path.isdir(Full_path):
                R["type"]="dir"
            else:
                R["path"] = R["path"][:-1]
                R["type"]="file"
            return R
        else:
            R["boolean"]=False
            # messagebox.showinfo("err","不能不选，也别多选TwT")
            return R
    def use_editor_open(file=""): #使用编辑器打开文件或文件夹
        point = get_point()
        if point["boolean"] and point["type"]=="dir":
            result = messagebox.askyesno("？", "是否使用编辑器打开这个文件夹？")
            if result:
                open_mdfile(point["path"])
            else:
                pass
        elif point["boolean"]:
            open_mdfile(point["path"])
        else:
            pass

    def creat_new_md():
        point = get_point()
        nowtime = date.today().strftime("%Y%m%d")
        if point["boolean"] and point["type"]=="dir":
            input_value = simpledialog.askstring("新建", "请输入filename", initialvalue=nowtime+".md")
            if input_value !=None:
                out_path =point["path"]+"/"+input_value
                if not os.path.exists(out_path):
                    if messagebox.askyesno("choose","是否使用模板内容：\n"+model_content[:100]):
                        with open(out_path, 'w',encoding='utf-8') as file:
                            file.write(model_content)  # 写入一些内容到文件中
                        updataList()
                    else:
                        with open(out_path, 'w') as file:
                            file.write("")  # 写入一些内容到文件中
                        updataList()
                    open_mdfile(out_path)
                    messagebox.showinfo("创建成功","开始创作吧！")
                else:
                    updataList()
                    if messagebox.askyesno("提示","文件已存在,是否打开？"):
                        open_mdfile(out_path)
            else:
                messagebox.showinfo("提示","选文件夹吧！懒得写了")
        pass
    def del_md():
        point = get_point()
        if point["boolean"] and point["type"] == "dir":
            messagebox.showinfo("提示","别选文件夹！懒得写了！")
        elif point["boolean"]:
            if os.path.isfile(point["path"]):
                os.remove(point["path"])
                updataList()
                messagebox.showinfo("提示","删除成功")
            else:
                updataList()
                print(point["path"])
                messagebox.showinfo("提示","文件不存在")
    def on_closing():
        save()
        print("goodbye!")
        root.destroy()  # 关闭窗口

    def save():
        print("正在保存配置..")
        with open('config.ini', 'w') as configfile:
            config.write(configfile)

    def check():
        if check_editor() and check_hexo_folder():
            messagebox.showinfo("检查完成", '应该没问题')
    #读取配置
    readConfig()
    check_editor()
    check_hexo_folder()
    # check_bash()
    root = tk.Tk()
    root_width = 678
    root_height = 520
    root.title("hexo快速创作")
    gui_queue = Queue()
    monitor_data_changes()
    iconIMG = ImageProcess(path="assets/logo.png", r=False)
    root.iconphoto(True, iconIMG)
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    # 计算窗口的左上角的坐标
    x = int((screen_width - root_width) / 2)
    y = int((screen_height - root_height) / 2)
    # 设置窗口的位置和大小
    root.geometry('{}x{}+{}+{}'.format(root_width, root_height, x, y))

    #构造页面
    fucts_frame = tk.Frame(root, bg="#5F9F9F")
    files_frame = tk.Frame(root, bg="black")
    right_scrollbar = tk.Scrollbar(files_frame, orient="vertical")
    listbox = ttk.Treeview(files_frame, yscrollcommand=right_scrollbar.set, selectmode="browse")
    menu = Menu(root, tearoff=0)
    fucts_frame.place(relwidth=0.7, relheight=1,anchor="ne",relx=1,rely=0)
    files_frame.place(relwidth=0.3, relheight=1,anchor="nw",relx=0,rely=0)
    right_scrollbar.pack(side="right", fill="y")
    listbox.heading("#0", text="/_source", anchor="w")
    listbox.tag_configure("md_file", foreground="blue")
    # listbox.bind("<Buttom-1>", on_treeview_click)
    populate_treeview(hexo_folder_path)
    # update_listbox(hexo_folder_path)  # 初始显示根目录下的文件和文件夹
    listbox.pack(side="right", fill="both", expand=True)
    right_scrollbar.config(command=listbox.yview)
    menu.add_command(label="使用编辑器打开", command=lambda: use_editor_open())
    menu.add_command(label="新建md", command=lambda: creat_new_md())
    menu.add_command(label="删除md", command=lambda: del_md())
    menu.add_command(label="刷新", command=lambda: updataList())
    menu.add_command(label="选择hexo目录", command=lambda: [choose_hexo_folder(),updataList()])
    # 构造fuct_frame
    navigation_bar = tk.Frame(fucts_frame,bg="#F0F0F0")
    navigation_bar.place(height=38,relwidth=1,anchor="nw",relx=0,rely=0)
    view_frame = tk.Frame(fucts_frame,bg="#dadada")
    view_frame.place(x=0,y=38,relheight=1,relwidth=1,anchor="nw")
    # 构造 navigation_bar
    img = {}
    img["bg"] = (ImageProcess("assets/bg2.png",True,76,25))
    img["bigbg"] = (ImageProcess("assets/bg.png",True,128,60))
    HomeLabel = tk.Button(navigation_bar,image=img["bg"],bd=0,bg=navigation_bar["bg"],compound="center",text='Home',activebackground=navigation_bar["bg"])
    HomeLabel.grid(row=0 , column=0,padx=1,pady=5)
    checkLabel = tk.Button(navigation_bar,text="Check",command=lambda :check(),padx=8,compound="center",image=img["bg"],bg=navigation_bar["bg"],bd=0,activebackground=navigation_bar["bg"])
    checkLabel.grid(row=0,column=1,padx=1,pady=5)
    HelpLabel = tk.Button(navigation_bar , text="Help",command=lambda : webbrowser.open(help_url),padx=8,compound="center",image=img["bg"],bg=navigation_bar["bg"],bd=0,activebackground=navigation_bar["bg"])
    HelpLabel.grid(row=0,column=2,padx=1,pady=5)
    AuthorLabel = tk.Button(navigation_bar, text="Author", command=lambda: webbrowser.open(Author_URI),padx=8,compound="center",image=img["bg"],bg=navigation_bar["bg"],bd=0,activebackground=navigation_bar["bg"])
    AuthorLabel.grid(row=0, column=3,padx=1,pady=5)
    saveLabel = tk.Button(navigation_bar, text="save", command=lambda: [save(),messagebox.showinfo('U•ェ•*U',"配置信息保存成功")], padx=8,
                            compound="center", image=img["bg"], bg=navigation_bar["bg"], bd=0,
                            activebackground=navigation_bar["bg"])
    saveLabel.grid(row=0, column=4, padx=1, pady=5)
    # navigation_bar.
    # navigation_bar.grid_rowconfigure(0, weight=1, minsize=20)  # 设置第0行的最小大小为50
    # 构造 view_frame
    toolframe = tk.Frame(view_frame,bg="#dadada")#放各种按钮
    toolframe.place(relwidth=1,relheight=1,anchor="nw",rely=0,relx=0)
    hexo = hexofuc.Hexo(root, hexo_folder_root_path)
    btn1 =tk.Button(toolframe,image=img["bigbg"],bd=0,bg=toolframe["bg"],compound="center",text='清理\nhexo cl',padx=10,pady=20,
                    activebackground=toolframe["bg"],command=lambda :hexo.cl())
    btn1.grid(row=0,column=0)
    btn2 = tk.Button(toolframe, image=img["bigbg"], bd=0, bg=toolframe["bg"], compound="center", text='生成\nhexo g',padx=10,pady=20,
                     activebackground=toolframe["bg"],command=lambda :hexo.generate())
    btn2.grid(row=0, column=1)
    btn3 = tk.Button(toolframe, image=img["bigbg"], bd=0, bg=toolframe["bg"], compound="center", text='启动服务\nhexo s',padx=10,pady=20,
                     activebackground=toolframe["bg"],command=lambda :hexo.sever())
    btn3.grid(row=0, column=2)
    btn4 = tk.Button(toolframe, image=img["bigbg"], bd=0, bg=toolframe["bg"], compound="center", text='推送(depoly)\nhexo d',padx=10,pady=20,
                     activebackground=toolframe["bg"],command=lambda :hexo.deploy())
    btn4.grid(row=1, column=0)
    btn5 = tk.Button(toolframe, image=img["bigbg"], bd=0, bg=toolframe["bg"], compound="center", text='一键打包\ncl&&g', padx=10,
                     pady=20,
                     activebackground=toolframe["bg"],command=lambda :[hexo.domore("hexo cl&&hexo g")])
    btn5.grid(row=1, column=1)
    btn6 = tk.Button(toolframe, image=img["bigbg"], bd=0, bg=toolframe["bg"], compound="center", text='一键打包发布\ncl&&g&&d', padx=20,
                     pady=20,command=lambda :hexo.domore("hexo cl&&hexo g&&hexo d"),
                     activebackground=toolframe["bg"])
    btn6.grid(row=1, column=2)
    btn7 = tk.Button(toolframe, image=img["bigbg"], bd=0, bg=toolframe["bg"], compound="center",
                     text='一键打包+本地测试\ncl&&g&&s\nlocalhost:4000', padx=10,
                     pady=20,command=lambda :[hexo.domore("hexo cl&&hexo g"),webbrowser.open("localhost:4000")],
                     activebackground=toolframe["bg"])
    btn7.grid(row=2, column=0)
    btn8 = tk.Button(toolframe, image=img["bigbg"], bd=0, bg=toolframe["bg"], compound="center",
                     text='一键打包+网页测试\ncl&&g&&d\n自定义网站', padx=10,
                     pady=20,
                     activebackground=toolframe["bg"])
    btn8.grid(row=2, column=1)
    btn9 = tk.Button(toolframe, image=img["bigbg"], bd=0, bg=toolframe["bg"], compound="center",
                     text='使用gulp\n压缩生成文件\nglup', padx=10,
                     pady=20,command=lambda :hexo.domore("gulp"),
                     activebackground=toolframe["bg"])
    btn9.grid(row=2, column=2)

    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()