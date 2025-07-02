import sys
sys.path.append('..')
import tkinter as tk
import yamltk


# name must match in the yaml file
class Root(tk.Tk):
    # required for root App, and each Branch
    yaml_file = 'root.yaml'
    
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
    builder = yamltk.Builder(Root, [TitleFrame, Item])
    builder.root.mainloop()