import tkinter as tk
import yaml
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper


WIDGETS = ['Canvas', 'Listbox', 'Menu', 'Text', 'Toplevel', 'Button', 'Checkbutton', 
    'Entry', 'Frame', 'Label', 'LabelFrame', 'Menubutton', 'Message', 'OptionMenu', 
    'PanedWindow', 'Radiobutton', 'Scale', 'Scrollbar', 'Spinbox', 'Tk']


class Builder:
    tk_variables = {}
    tk_widgets = {}
    
    def __init__(self, filename, application):
        self.application = application
        with open(filename) as f:
            data = yaml.load(f, Loader)
            self.root = self._build_widget(data)
    
    def _build_widget(self, data, parent=None):
        # the first key should be the name of the widget
        widget_name = next(iter(data.keys()))
        if not widget_name in WIDGETS:
            raise TypeError(f'Invalid widget: {widget_name}')
        
        # instanciate the widget
        widget_class = getattr(tk, widget_name)
        widget = widget_class(parent)
        data = data[widget_name]
        
        # run through the widgets options, commands, children and special keys
        for key, value in data.items():
            match key:
                case 'widget':
                    continue
                case 'children':
                    for child_data in value:
                        self._build_widget(child_data, widget)
                case 'id':
                    self.tk_widgets[value] = widget
                    self.application.tk_widgets[value] = widget
                case 'variable':
                    widget.configure(variable=self._get_var(value))
                case 'text_variable':
                    widget.configure(textvariable=self._get_var(value))
                case 'app_command':
                    cmd = getattr(self.application, value)
                    widget.configure(command=cmd)
                case _:
                    self._case_other(widget, key, value)
        
        return widget
    
    def _case_other(self, widget, key, value):
        if key in widget.configure():
            widget.configure(**{key: value})
        elif hasattr(widget, key):
            method = getattr(widget, key)
            method(value)
        else:
            msg = f'Invalid attribute "{key}" for widget "{widget_name}"'
            raise AttributeError(msg)
    
    def _get_var(self, data):
        # check if the variable has already been created
        if data['name'] in self.tk_variables:
            return self.tk_variables[data['name']]
        
        # otherwise, create the variable, using the appropriate type
        var = None
        match data['type']:
            case 'int':
                var = tk.IntVar()
            case 'string':
                var = tk.StringVar()
            case _:
                raise TypeError(f"Unexpected variable type: {data['type']}")
        
        # reference it for later lookup
        self.tk_variables[data['name']] = var
        self.application.tk_variables[data['name']] = var
        return var


class Application:
    tk_variables = {}
    tk_widgets = {}
    