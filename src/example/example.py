import sys
sys.path.append('..')

# copy everything below for the README

"""
You can find explanations in the comments here, or inside the different yaml 
files of this example project.

I suggest starting by reading the `if __name__ == '__main__':` section at the 
bottom of this file.
"""

from pathlib import Path
from tk_double_scale import DoubleScale
import tkinter as tk
import yamltk


class Root(tk.Tk):
    """This is the root branch.

    The name can be anything, but it must match the one inside the yaml file.
    
    yaml_file is the path to the layout file (yaml).
    It can be a relative path if you are sure from where the script will be 
    executed.
    """
    yaml_file = Path(__file__).parent / 'root.yaml'
    
    def post_build(self):
        """This method is always executed after the widget has been built."""
        self.button_add.configure(command=self.on_add_button)

    def on_add_button(self):
        """
        The method below adds a new branch ('Item') to the specified 
        parent frame (bottom_frame) in the user interface. 
        The branch is created without a specific name for the item.
        """
        self.builder.add_branch(branch_name='Item', name=None, 
                                parent=self.bottom_frame)

    def on_checkbutton_foobar(self):
        """
        This method must be defined, since it is referenced in the yaml file.
        You can see below how variables defined in the yaml file can be accessed.
        """
        foo = 'foo' if self.check_foo_var.get() else ''
        bar = 'bar' if self.check_bar_var.get() else ''
        self.check_foobar_var.set(f'{foo} {bar}')


class TitleFrame(tk.Frame):
    """Another branch example."""
    yaml_file = Path(__file__).parent / 'title_frame.yaml'
    
    def post_build(self, title, color, foo=None, quz=0):
        """Here we can find the arguments passed in the root.yaml file."""
        self.title_label.configure(
            text=title, fg=color
        )
        print(foo, quz)     # > bar 1
    
    def on_button_exit(self):
        quit()


class Item(tk.Frame):
    yaml_file = Path(__file__).parent / 'item.yaml'


if __name__ == '__main__':
    """
    A Root branch is required to build the application (name can be anything).
    Other branches are optional.
    """
    root = yamltk.build(Root, [TitleFrame, Item, DoubleScale])
    root.radio_var.set('tea')
    root.mainloop()