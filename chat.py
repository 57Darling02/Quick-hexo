import configparser
import tkinter as tk
from tkinter import Button

# 创建配置解析器对象
config = configparser.ConfigParser()

# 读取配置文件
config.read('config.ini')

# 创建主窗口
root = tk.Tk()
root.title("Button Generator")
num = 2
# 从配置文件中获取所有按钮信息
for i in range(1,num+1):#btcon[0][1] text    btcon[1][1] command

    btcon = config.items("Button"+str(i))
    print(btcon[1][1])
    button_command = eval("lambda :"+btcon[1][1])
    button = Button(root, text=btcon[0][1], command=button_command)
    button.pack()  # 将按钮添加到主窗口中
# for button_info in buttons:
#     print(button_info)
#     print("00000")
#     button_text = button_info[1]  # 获取按钮文本
#     button_command = eval(button_info[1]['command'])  # 获取按钮命令，并将其转换为Python函数或方法
#
#     button = Button(root, text=button_text, command=button_command)  # 创建按钮并添加到主窗口中
#     button.pack()  # 将按钮添加到主窗口中



    # 这里只获取了两个按钮的信息，你可以根据需要添加更多按钮
# print(buttons)
# 循环创建按钮并添加到主窗口中


# 运行主循环，显示主窗口
root.mainloop()