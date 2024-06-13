from tkinter import *
from tkinter.ttk import *

class App(Tk):

    def __init__(self):
        super().__init__()
        self.__win()
        self.tk_label_username = self.__tk_label_username(self)
        self.tk_button_test = self.__tk_button_test(self)

    def __win(self):
        self.title("Tkinter布局助手")
        # 设置窗口大小、居中
        width, height = 600, 500
        
        screenwidth = self.winfo_screenwidth()
        screenheight = self.winfo_screenheight()
        geometry = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
        self.geometry(geometry)
        
        self.resizable(width=False, height=False)

    def __tk_label_username(self, parent):
        label = Label(parent,text="用户名：",anchor="center", )
        label.place(x=66, y=19, width=50, height=30)
        return label
    def __tk_button_test(self, parent):
        btn = Button(parent, text="测试", takefocus=False,)
        btn.place(x=170, y=20, width=50, height=30)
        return btn

    def show(self):
        self.mainloop()

if __name__ == "__main__":
    app = App()
    app.show()