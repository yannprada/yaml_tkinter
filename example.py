import tkinter as tk
from yamltk import Builder


# inherit Tk or Frame
class ExampleApp(tk.Tk):
    # required for root App, and each Branch
    yaml_file = 'example.yaml'
    
    # define this method, so that it is bound automatically
    # since it is referenced in the example.yaml file
    def on_checkbutton_foobar(self):
        # here is how to access tk variables
        foo = self.tk_variables['check_foo_var'].get()
        bar = self.tk_variables['check_bar_var'].get()
        foo = 'foo' if foo else ''
        bar = 'bar' if bar else ''
        self.tk_variables['check_foobar_var'].set(f'{foo} {bar}')


# Branch example
class TitleFrame(tk.Frame):
    yaml_file = 'title_frame.yaml'
    
    def on_button_exit(self):
        quit()


class Item(tk.Frame):
    yaml_file = 'item.yaml'


if __name__ == '__main__':
    builder = Builder(ExampleApp, [TitleFrame, Item])
    
    def on_button_add():
        builder.add_branch('Item', builder.tk_widgets['bottom_frame'])
    
    builder.tk_widgets['button_add'].configure(command=on_button_add)
    
    builder.root.mainloop()