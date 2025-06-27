import tkinter as tk
from yamltk import Builder


# this class is used to bind methods
# and maybe other things in the future? FIXME
class Application:
    # define this method, so that it is bound automatically
    # since it is referenced in the yaml file
    def on_button_exit(self):
        quit()
    
    # TODO: example with manual event binding (command)


if __name__ == '__main__':
    app = Application()
    builder = Builder('./example.yaml', app)
    builder.root.mainloop()