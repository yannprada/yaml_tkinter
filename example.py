import tkinter as tk
from yamltk import build


if __name__ == '__main__':
    root, widgets = build('./example.yaml')
    
    button = widgets['exit_button'] # retrieve the button by id
    button = root.nametowidget('!frame.!button') # or follow the hierarchy
    
    button.configure(command=quit)
    
    entry_var = tk.StringVar()
    widgets['entry'].configure(textvariable=entry_var)
    widgets['entry_label'].configure(textvariable=entry_var)
    
    radio_var = tk.StringVar()
    widgets['foo_radio'].configure(variable=radio_var)
    widgets['bar_radio'].configure(variable=radio_var)
    widgets['radio_label'].configure(textvariable=radio_var)
    
    # TODO: make a new version of yamltk.py that uses a Builder object
    # benefits:
    #   keep some references without having to pass them on the recursion chain
    # references to keep:
    #   marked widgets with 'id'
    #   tk variables (StringVar, ...)
    
    root.mainloop()