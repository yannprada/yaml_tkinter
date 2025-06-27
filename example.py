import tkinter as tk
from yamltk import Builder


# this class is used to bind methods
# and maybe other things in the future? FIXME
class Application:
    # required for variables and widgets access
    tk_variables = {}
    tk_widgets = {}
    
    # define this method, so that it is bound automatically
    # since it is referenced in the example.yaml file
    def on_button_exit(self):
        quit()
    
    # same as above
    def on_checkbutton_foobar(self):
        # here is how to access tk variables
        foo = self.tk_variables['check_foo_var'].get()
        bar = self.tk_variables['check_bar_var'].get()
        foo = 'foo' if foo == 1 else ''
        bar = 'bar' if bar == 1 else ''
        self.tk_variables['check_foobar_var'].set(f'{foo} {bar}')
    
    # TODO: example with manual event binding (command)


if __name__ == '__main__':
    app = Application()
    builder = Builder('./example.yaml', app)
    builder.root.mainloop()