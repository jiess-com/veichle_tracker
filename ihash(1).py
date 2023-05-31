import tkinter
import tkinter.filedialog
import tkinter.ttk
import PIL.Image
import imagehash

a = None
#####################################整体页面布局#################################################
window = tkinter.Tk()
window.title('农民画侵权检测')
window.geometry('640x360')
window.resizable(False, False)
########################################获取第一张图片##############################################
lbl_img1 = tkinter.Label(window, text='原始图片')
lbl_img1.grid(column=0, row=0)

txt_img1 = tkinter.Entry(window, width=60)
txt_img1.grid(column=1, row=0)


def select_img1():
    filename = tkinter.filedialog.askopenfilename()
    txt_img1.delete(0, tkinter.END)
    txt_img1.insert(0, filename)


btn_img1 = tkinter.Button(window, text='上 传 ...', command=select_img1)
btn_img1.grid(column=2, row=0)
##########################################获取第二张图片############################################
lbl_img2 = tkinter.Label(window, text='检测图片 ')
lbl_img2.grid(column=0, row=1)

txt_img2 = tkinter.Entry(window, width=60)
txt_img2.grid(column=1, row=1)


def select_img2():
    filename = tkinter.filedialog.askopenfilename()
    txt_img2.delete(0, tkinter.END)
    txt_img2.insert(0, filename)


btn_img2 = tkinter.Button(window, text='上 传 ...', command=select_img2)
btn_img2.grid(column=2, row=1)
######################################################################################
lbl_hash1 = tkinter.Label(window, text='原始图片哈希值')
lbl_hash1.grid(column=0, row=2)

str_hash1 = tkinter.StringVar()
txt_hash1 = tkinter.Entry(window, width=60, state='readonly', textvariable=str_hash1)#Entry输入单行文本
txt_hash1.grid(column=1, row=2)
######################################################################################
lbl_hash2 = tkinter.Label(window, text='检测图片哈希值 ')
lbl_hash2.grid(column=0, row=3)

str_hash2 = tkinter.StringVar()
txt_hash2 = tkinter.Entry(window, width=60, state='readonly', textvariable=str_hash2)
txt_hash2.grid(column=1, row=3)
######################################################################################
lbl_diff = tkinter.Label(window, text='作品相似度 ')
lbl_diff.grid(column=0, row=4)

str_diff = tkinter.StringVar()
txt_diff = tkinter.Entry(window, width=60, state='readonly', textvariable=str_diff)
txt_diff.grid(column=1, row=4)

lbl_method = tkinter.Label(window, text='请选择哈希算法')
lbl_method.grid(column=0, row=5)
######################################################################################
cbb_method = tkinter.ttk.Combobox(window, state='readonly', value='chen')#复选框
cbb_method['values'] = ('均值哈希算法', '感知哈希算法','差值哈希算法',  '小波哈希算法', '颜色直方图')
cbb_method.current(0)
cbb_method.grid(column=1, row=5)
######################################################################################

def compute():
    hash1, hash2 = None, None
    method = cbb_method.get()
    img1 = PIL.Image.open(txt_img1.get())
    img2 = PIL.Image.open(txt_img2.get())
    print(type(img1))
    print(type(img2))
    #################################################

    #################################################
    if method == '均值哈希算法':
        hash1 = imagehash.average_hash(img1)
        hash2 = imagehash.average_hash(img2)
    elif method == '颜色直方图':
        hash1 = imagehash.colorhash(img1)
        hash2 = imagehash.colorhash(img2)
    elif method == '差值哈希算法':
        hash1 = imagehash.dhash(img1)
        hash2 = imagehash.dhash(img2)
    elif method == '感知哈希算法':
        hash1 = imagehash.phash(img1)
        hash2 = imagehash.phash(img2)
    elif method == '小波哈希算法':
        hash1 = imagehash.whash(img1)
        hash2 = imagehash.whash(img2)
    str_hash1.set(str(hash1))
    str_hash2.set(str(hash2))
    str_diff.set(str((64-int(str(hash1-hash2)))/64*100)+'%')


btn_compute = tkinter.Button(window, text='开始检测', command=compute)
btn_compute.grid(column=2, row=5)
window.mainloop()
