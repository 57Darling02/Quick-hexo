# from PIL import ImageTk, Image, ImageSequence
# def crop_top_half(image_path, save_path):
#     # 打开图像文件
#     image = Image.open(image_path)
#     # 获取图像的宽度和高度
#     width, height = image.size
#     # 定义剪裁区域：左上角和右下角坐标
#     # 剪裁上半部分，所以左上角的 y 坐标设为 0，右下角的 y 坐标设为原始高度的一半
#     top_half_box = (0, 0, width, height // 2)
#     # 对图像进行剪裁
#     top_half_image = image.crop(top_half_box)
#     top_half_image.save(save_path)
#
# # 示例用法
# input_image_path = "assets/console.png"
# output_image_path = "assets/close.png"
# crop_top_half(input_image_path, output_image_path)
import tkinter as tk

root = tk.Tk()
root.title("Truncated Label Example")

# 长文本内容
long_text = "This is a very long text that needs to be truncated if it exceeds the specified width in the GUI."

# 创建Label并设置anchor为"nw"，并使用ellipsis显示省略号
label = tk.Label(root, text=long_text, anchor="nw", width=00)
label.pack()

# 其他部件
button = tk.Button(root, text="Click me")
button.pack()

root.mainloop()