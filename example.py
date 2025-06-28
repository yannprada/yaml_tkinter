import tkinter as tk
from yamltk import Builder


# inherit Tk or Frame
class ExampleApp(tk.Tk):
    # define this method, so that it is bound automatically
    # since it is referenced in the example.yaml file
    def on_button_exit(self):
        quit()
    
    # same as above
    def on_checkbutton_foobar(self):
        # here is how to access tk variables
        foo = self.tk_variables['check_foo_var'].get()
        bar = self.tk_variables['check_bar_var'].get()
        foo = 'foo' if foo else ''
        bar = 'bar' if bar else ''
        self.tk_variables['check_foobar_var'].set(f'{foo} {bar}')
    
    # TODO: example with manual event binding (command)


if __name__ == '__main__':
    builder = Builder('./example.yaml', ExampleApp)
    builder.root.mainloop()