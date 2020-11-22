from tkinter import Tk, Label, Entry, Frame, Button, LEFT, END

class WindowLogin(Tk):
    """
    login window
    """

    def __init__(self):
        super(WindowLogin, self).__init__()

        #config window
        self.window_init()

        #add widgets
        self.add_widgets()

        #clear input when click reset button
        self.on_reset_button_click(lambda: self.clear_username_and_pwd())

    def window_init(self):
        """config window"""
        #title
        self.title('Login')
        self.resizable(False, False)

        #size and position
        window_width = 255
        window_height = 95
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        pos_x = (screen_width-window_width)/2
        pos_y = (screen_height-window_height)/2

        self.geometry('%dx%d+%d+%d' %
                      (window_width, window_height, pos_x, pos_y))


    def add_widgets(self):
        
        #username
        username_label = Label(self)
        username_label['text'] = 'username'
        username_label.grid(row=0, column=0, padx=10, pady=5)

        username_entry = Entry(self, name='username_entry')
        username_entry.grid(row=0, column=1)

        #pwd
        pwd_label = Label(self)
        pwd_label['text'] = 'password'
        pwd_label.grid(row=1, column=0, padx=10, pady=5)

        pwd_entry = Entry(self, name='pwd_entry')
        pwd_entry['show'] = '*'
        pwd_entry.grid(row=1, column=1)

        #reset and login button
        button_frame = Frame(self, name='button_frame')
        reset_button = Button(button_frame, name='reset_button')
        reset_button['text'] = 'reset'
        reset_button.pack(side=LEFT, padx=20)

        login_button = Button(button_frame, name='login_button')
        login_button['text'] = 'login'
        login_button.pack(side=LEFT)

        button_frame.grid(row=2, columnspan=2, pady=5)

    def get_server_ip(self):
        return self.children['ip_entry'].get()


    def get_username(self):
        return self.children['username_entry'].get()

    
    def get_pwd(self):
        return self.children['pwd_entry'].get()

    def clear_username_and_pwd(self):
        self.children['username_entry'].delete(0, END)
        self.children['pwd_entry'].delete(0, END)


    def on_login_button_click(self, command):
        login_button = self.children['button_frame'].children['login_button']
        login_button['command'] = command


    def on_reset_button_click(self, command):
        reset_button = self.children['button_frame'].children['reset_button']
        reset_button['command'] = command


    def on_window_closed(self, command):
        self.wm_protocol('WM_DELETE_WINDOW', command)
    

if __name__ == "__main__":
    window = WindowLogin()
    window.mainloop()
