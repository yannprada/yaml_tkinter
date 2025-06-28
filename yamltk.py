import tkinter as tk
import yaml
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper


TK_VARIABLES = {
    'boolean': tk.BooleanVar, 
    'double': tk.DoubleVar, 
    'int': tk.IntVar, 
    'string': tk.StringVar
}


class Builder:
    tk_variables = {}
    tk_widgets = {}
    
    def __init__(self, filename, root_class):
        # build the widgets
        with open(filename) as f:
            data = yaml.load(f, Loader)
            self._create_widget(data, None, root_class)
        
        # keep a reference to widgets with ids and tk varables
        self.root.tk_widgets = self.tk_widgets
        self.root.tk_variables = self.tk_variables
    
    def _create_widget(self, data, parent=None, root_class=None):
        # the first key should be the name of the widget
        widget_name = next(iter(data.keys()))
        
        # instanciate the widget
        if parent is None:
            # widget is root
            self.root = root_class()
            widget = self.root
        else:
            widget_class = getattr(tk, widget_name)
            widget = widget_class(parent)
        
        self._build_widget(widget, data[widget_name])
    
    def _build_widget(self, widget, data):
        # run through the widgets options, commands, children and special keys
        for key, value in data.items():
            match key:
                case 'widget':
                    continue
                case 'children':
                    for child_data in value:
                        self._create_widget(child_data, widget)
                case 'id':
                    self.tk_widgets[value] = widget
                case 'variable':
                    widget.configure(variable=self._get_var(value))
                case 'text_variable':
                    widget.configure(textvariable=self._get_var(value))
                case 'app_command':
                    cmd = getattr(self.root, value)
                    widget.configure(command=cmd)
                case _:
                    if key in widget.configure():
                        widget.configure(**{key: value})
                    else:
                        method = getattr(widget, key)
                        method(value)
    
    def _get_var(self, data):
        # check if the variable has already been created
        if data['name'] in self.tk_variables:
            return self.tk_variables[data['name']]
        
        # otherwise, create the variable, using the appropriate type
        var_class = TK_VARIABLES.get(data['type'])
        if var_class is None:
            raise TypeError(f"Unexpected variable type: {data['type']}")
        
        # reference it for later lookup
        var_instance = var_class()
        self.tk_variables[data['name']] = var_instance
        return var_instance
