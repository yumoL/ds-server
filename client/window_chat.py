from tkinter import Toplevel, Text, Button, END, UNITS
from tkinter.scrolledtext import ScrolledText

class WindowChat(Toplevel):

    def __init__(self):
        super(WindowChat, self).__init__()

        #config size
        self.geometry('%dx%d' % (795, 505))
        self.resizable(False, False)

        #add widgets
        self.add_widgets()
        self.on_send_button_click(lambda: self.append_msg(sender='user1',msg='lalala'))

    def add_widgets(self):
        #chat history
        chat_history_area = ScrolledText(self)
        chat_history_area['width'] = 110
        chat_history_area['height'] = 30
        chat_history_area.grid(row=0, column=0, columnspan=2)

        chat_history_area.tag_config('green', foreground='green')
        self.children['chat_history_area'] = chat_history_area

        #input message
        chat_input_area = Text(self, name='chat_input_area')
        chat_input_area['width'] = 100
        chat_input_area['height'] = 7
        chat_input_area.grid(row=1, column=0, pady=10)

        #send button
        send_button = Button(self, name='send_button')
        send_button['text'] = 'send'
        send_button['width'] = 5
        send_button['height'] = 2
        send_button.grid(row=1, column=1)


    def set_title(self, username):
        self.title(f'Hi, {username}')


    def on_send_button_click(self, command):
        """
        execute command when clicking send_button
        """
        self.children['send_button']['command'] = command


    def get_input(self):
        return self.children['chat_input_area'].get(0.0, END)


    def clear_input(self):
        self.children['chat_input_area'].delete(0.0, END)

    
    def append_msg(self, sender, msg, send_time='2020-11-13 12:29'):
        #TODO: send_time may be obtained from redis server, currently it is hard-coded
        send_info = f'{sender}: {send_time}\n'
        self.children['chat_history_area'].insert(END, send_info, 'green')
        self.children['chat_history_area'].insert(END, msg+'\n')

        #scroll down automatically
        self.children['chat_history_area'].yview_scroll(3, UNITS)

    def on_window_closed(self, command):
        #TODO:releae resource when user close window and quit
        self.wm_protocol('WM_DELETE_WINDOW', command)


if __name__ == "__main__":
    WindowChat().mainloop()
