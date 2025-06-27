import tkinter as tk
import yaml
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper


class Builder:
    tk_widgets = {}
    tk_variables = {}
    
    def __init__(self, filename, application):
        self.application = application
        with open(filename) as f:
            data = yaml.load(f, Loader)
            self.root = self._build_widget(data)
    
    def _build_widget(self, data, parent=None):
        widget_name = next(iter(data.keys()))
        if not hasattr(tk, widget_name):
            raise TypeError(f'Invalid widget: {widget_name}')
        
        widget_class = getattr(tk, widget_name)
        widget = widget_class(parent)
        options = widget.configure()
        data = data[widget_name]
        
        for key, value in data.items():
            match key:
                case 'widget':
                    continue
                case 'children':
                    for child_data in value:
                        child_widget = self._build_widget(child_data, widget)
                    continue
                case 'id':
                    self.tk_widgets[value] = widget
                case 'var':
                    widget.configure(variable=self._get_string_var(value))
                case 'int_var':
                    widget.configure(textvariable=self._get_int_var(value))
                case 'text_var':
                    widget.configure(textvariable=self._get_string_var(value))
                case 'command':
                    cmd = getattr(self.application, value)
                    widget.configure(command=cmd)
                case _:
                    if hasattr(widget, key):
                        method = getattr(widget, key)
                        method(value)
                    elif key in options:
                        widget.configure(**{key: value})
                    else:
                        raise AttributeError(f'Invalid attribute "{key}" for widget "{widget_name}"')
        
        return widget
    
    def _get_var(self, name, var_class):
        var = self.tk_variables.get(name, var_class())
        self.tk_variables[name] = var
        return var
    
    def _get_int_var(self, name):
        return self._get_var(name, tk.IntVar)
    
    def _get_string_var(self, name):
        return self._get_var(name, tk.StringVar)
