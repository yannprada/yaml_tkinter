import sys
sys.path.append('..')

# copy everything below for the README

from tk_double_scale import DoubleScale
import tkinter as tk
import yamltk


# The name must match in the yaml file
class Root(tk.Tk):
    # Specify the YAML file that defines the layout
    yaml_file = 'root.yaml'
    
    # Executed after the widget has been built
    def post_build(self):
        self.button_add.configure(command=self.on_add_button)

    def on_add_button(self):
        # Use the builder to add a new 'Item' branch inside the bottom_frame
        # The name parameter is in the tkinter sense
        # Here self.bottom_frame is valid because of the name parameter 
        # in the yaml file
        self.builder.add_branch(branch_name='Item', name=None, 
                                parent=self.bottom_frame)

    # Define this method, so that it is bound automatically
    # since it is referenced in the example.yaml file
    def on_checkbutton_foobar(self):
        # here is how to access tk variables
        foo = 'foo' if self.check_foo_var.get() else ''
        bar = 'bar' if self.check_bar_var.get() else ''
        self.check_foobar_var.set(f'{foo} {bar}')


# Branch example
class TitleFrame(tk.Frame):
    yaml_file = 'title_frame.yaml'
    
    def post_build(self, title, color, foo=None, quz=0):
        self.title_label.configure(
            text=title, fg=color
        )
        print(foo, quz)     # > bar 1
    
    def on_button_exit(self):
        quit()


class Item(tk.Frame):
    yaml_file = 'item.yaml'


if __name__ == '__main__':
    # A Root branch is required to build the application (name can be anything)
    # other branches are optional
    builder = yamltk.Builder(Root, [TitleFrame, Item, DoubleScale])
    builder.root.radio_var.set('tea')
    builder.root.mainloop()