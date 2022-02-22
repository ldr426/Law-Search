from tkinter import *
from tkinter import ttk
import tkinter as tk
import tkinter.messagebox
from PIL import Image, ImageTk
import pymysql

# 查询类型
select_type = '所有内容'
# 查询范围
select_range = '所有范围'
# 存放法规内容
legal_list = []

# ===============================================展示事件函数=============================================================
def show(index, num):
    root1 = tk.Tk()
    title_str = '法规内容'
    root1.title(title_str)
    # 设置窗口大小
    width = 800
    height = 500
    # 获取屏幕尺寸以计算布局参数，使窗口居屏幕中央
    alignstr = '%dx%d+%d+%d' % (
        width, height, (root1.winfo_screenwidth() - width) / 2, (root1.winfo_screenheight() - height) / 2)
    root1.geometry(alignstr)
    # 设置窗口是否可变长、宽，True：可变，False：不可变
    root1.resizable(width=False, height=False)
    _f = tk.Frame(root1)
    _s1 = tk.Scrollbar(_f, orient=tk.VERTICAL)
    _s2 = tk.Scrollbar(_f, orient=tk.HORIZONTAL)
    _b1 = tk.Text(_f, width=90, height=100, wrap=tk.NONE,
                  yscrollcommand=_s1.set,
                  xscrollcommand=_s2.set)
    legal_content = []
    legal_content = legal_list[num-1]
    str_ = "法规ID： " + str(legal_content[0])
    _b1.insert("end", str_)
    _b1.insert("end", '\n')
    str_ = "法规类别： " + str(legal_content[1])
    _b1.insert("end", str_)
    _b1.insert("end", '\n')
    str_ = "项目实施阶段： " + legal_content[2]
    _b1.insert("end", str_)
    _b1.insert("end", '\n')
    str_ = "法规标题： " + legal_content[3]
    _b1.insert("end", str_)
    _b1.insert("end", '\n')
    str_ = "法规二维码： " + legal_content[4]
    _b1.insert("end", str_)
    _b1.insert("end", '\n')
    str_ = "法规PDF： " + legal_content[5]
    _b1.insert("end", str_)
    _b1.insert("end", '\n')
    str_ = "法规URL： " + legal_content[6]
    _b1.insert("end", str_)
    _b1.insert("end", '\n')
    str_ = "法规分类： " + legal_content[7]
    _b1.insert("end", str_)
    _b1.insert("end", '\n')
    str_ = "法规级别： " + legal_content[8]
    _b1.insert("end", str_)
    _b1.insert("end", '\n')
    str_ = "法规关键字： " + legal_content[10]
    _b1.insert("end", str_)
    _b1.insert("end", '\n')
    _b1.insert("end", '法规内容： ')
    k = 0
    for i in legal_content[9]:
        k += 1
        _b1.insert("end", i)
        if k == 42:
            k = 0
            _b1.insert("end", '\n')
    _s1.pack(side=tk.RIGHT, fill=tk.Y)
    _s1.config(command=_b1.yview)
    _s2.pack(side=tk.BOTTOM, fill=tk.X)
    _s2.config(command=_b1.xview)
    _b1.pack(fill=tk.BOTH)
    _f.pack()
    # 设置按钮
    Button(root1, text='退出', relief=RAISED, width=6, height=1, font=("楷体", 15), command=root1.destroy).place(
        x=723,
        y=200)
    root1.mainloop()
# ===============================================展示事件函数=============================================================


# ===============================================查询事件函数=============================================================
def select():
    # 判断是否输入内容
    if len(entry1.get()) == 0:
        tkinter.messagebox.showinfo(title='提示', message='请输入内容！')
        return
    # 根据内容进行查询
    db = pymysql.connect(host='输入主机名', user='root', password='输入密码', port=3300, database='intelligence')
    cur = db.cursor()
    name = entry1.get()

    # 确定法规查询方式
    global select_type
    if select_type == '所有内容':
        select_type = 'message,remarks'
    elif select_type == '按标题查询':
        select_type = 'message'
    else:
        select_type = 'remarks'
    # 确定法规查询范围
    global select_range
    if select_range == '所有范围':
        sql = 'select *from legal where match(' + select_type + ') against ("' + name + ' " in natural LANGUAGE mode)'
    else:
        sql = 'select *from legal where match(' + select_type + ') against ("' + name + '" in NATURAL LANGUAGE MODE) ' \
             'and match(region)against("' + select_range + '" in NATURAL LANGUAGE MODE)'
    cur.execute(sql)
    result = cur.fetchall()
    if len(result) == 0:
        tkinter.messagebox.showinfo(title='提示', message='未找到相关内容！')
        return
    else:
        root = tk.Tk()
        title_str = '找到如下', len(result), '条内容：'
        root.title(title_str)
        # 设置窗口大小
        width = 800
        height = 500
        # 获取屏幕尺寸以计算布局参数，使窗口居屏幕中央
        alignstr = '%dx%d+%d+%d' % (
            width, height, (root.winfo_screenwidth() - width) / 2, (root.winfo_screenheight() - height) / 2)
        root.geometry(alignstr)
        # 设置窗口是否可变长、宽，True：可变，False：不可变
        root.resizable(width=False, height=False)
        f = tk.Frame(root)
        s1 = tk.Scrollbar(f, orient=tk.VERTICAL)
        s2 = tk.Scrollbar(f, orient=tk.HORIZONTAL)
        b1 = tk.Text(f, width=90, height=100, wrap=tk.NONE,
                     yscrollcommand=s1.set,
                     xscrollcommand=s2.set)
        global legal_list
        legal_list = result
        # 查询结果序号
        num = 1
        # 输出查询结果到新的窗口
        for search in result:
            lint_str = '序号： ' + str(num) + ' 法规ID: ' + str(search[0]) + '  法规名称： ' + search[3]
            b1.insert("end", lint_str)
            b1.insert("end", '\n')
            b1.insert("end", '\n')
            b = tk.Button(b1, text="点击查看详细内容", command=lambda index=num, num=num: show(index, num))
            b1.window_create("insert", window=b)
            b1.insert("end", '\n')
            b1.insert("end", '\n')
            num += 1
        s1.pack(side=tk.RIGHT, fill=tk.Y)
        s1.config(command=b1.yview)
        s2.pack(side=tk.BOTTOM, fill=tk.X)
        s2.config(command=b1.xview)
        b1.pack(fill=tk.BOTH)
        f.pack()
        # 设置按钮
        Button(root, text='退出', relief=RAISED, width=6, height=1, font=("楷体", 15), command=root.destroy).place(x=723,
                                                                                                               y=200)
        root.mainloop()
# ===============================================查询事件函数=============================================================


# ===============================================初始化窗口win============================================================
# 初始化Tk() 即窗口对象
win = tk.Tk()
# 设置窗口标题
win.title('Python GUI 全文检索')
# 设置窗口大小
width = 800
height = 500
# 获取屏幕尺寸以计算布局参数，使窗口居屏幕中央
alignstr = '%dx%d+%d+%d' % (
    width, height, (win.winfo_screenwidth() - width) / 2, (win.winfo_screenheight() - height) / 2)
win.geometry(alignstr)
# 设置窗口是否可变长、宽，True：可变，False：不可变
win.resizable(width=False, height=False)
# ===============================================初始化窗口win============================================================


# ===============================================设置背景图片=============================================================
# 创建画布，设置要显示的图片，把画布添加至应用程序窗口
canvas_root = tkinter.Canvas(win, width=800, height=600)
im_root = ImageTk.PhotoImage(Image.open('background.jpg').resize((800, 600)))
canvas_root.create_image(400, 300, image=im_root)
canvas_root.pack()
# ===============================================设置背景图片=============================================================


# ===============================================设置窗口控件=============================================================
# 导航栏标签
Label(win, fg='white', bg='blue', font=("楷体", 20), text="\t\t欢迎使用法律法规库全文检索系统\t\t\t").place(x=0, y=0)
Label(win, font=("楷体", 20), relief=GROOVE, text="请输入您要查询的内容").place(x=255, y=50)
# 设置输入框
entry1 = tk.Entry(win, width=5, font=("楷体", 15), relief=GROOVE)
entry1.place(x=250, y=100, height=30, width=300)
# 设置按钮
Button(win, text='查询', relief=RAISED, width=6, height=1, font=("楷体", 15), command=select).place(x=250, y=300)
Button(win, text='退出', relief=RAISED, width=6, height=1, font=("楷体", 15), command=win.destroy).place(x=480, y=300)
# ===============================================设置窗口控件=============================================================


# ===============================================第一个选项===============================================================
# 创建第一个label
Label(win, text="选择查询类型", relief=GROOVE, font=("楷体", 15)).place(x=150, y=200, height=30, width=150)


def show_select_1(*args):
    # print("post_command: show_select")
    global select_type
    select_type = cbx_1.get()


# 设置选项数据
data1 = ["所有内容", "按标题查询", "按正文查询"]
# 创建选项窗口 并调好参数
cbx_1 = ttk.Combobox(win, width=12, height=8, font=("楷体", 12), postcommand=show_select_1)
cbx_1.place(x=150, y=150, height=30, width=150)
# 给选项添加设置好的数据
cbx_1["values"] = data1
# 设置为默认显示第一个数据
cbx_1.current(0)

cbx_1.bind("<<ComboboxSelected>>", show_select_1)  # #给下拉菜单绑定事件
# ===============================================第一个选项===============================================================


# ===============================================第二个选项===============================================================
# 创建第二个label
Label(win, text="选择查询范围", relief=GROOVE, font=("楷体", 15)).place(x=500, y=200, height=30, width=150)


def show_data_2(*args):
    # print("Event: ComboboxSelected")
    global select_range
    select_range = cbx_2.get()


# 设置选项数据
data2 = ['所有范围', '国家', '北京', '天津', '河北', '山西', '内蒙古', '辽宁', '吉林', '黑龙江', '上海',
         '江苏', '浙江', '安徽', '福建', '江西', '山东', '河南', '湖北', '湖南', '广东', '广西',
         '海南', '重庆', '四川', '贵州', '云南', '西藏自治', '陕西', '甘肃', '青海', '宁夏', '新疆']
# 创建选项窗口 并调好参数
cbx_2 = ttk.Combobox(win, width=12, height=8, font=("楷体", 12))
cbx_2.place(x=500, y=150, height=30, width=150)
# 给选项添加设置好的数据
cbx_2["values"] = data2
# 设置为默认显示第一个数据
cbx_2.current(0)

cbx_2.bind("<<ComboboxSelected>>", show_data_2)  # #给下拉菜单绑定事件
# ===============================================第二个选项===============================================================


# 进入消息循环
win.mainloop()
