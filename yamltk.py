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


# TODO: find a less hacky way than self.previous_root and self.current_root
# to bind a widget to its intended object

# ALSO: try putting Addon's yaml filename in the parent's file
#   example: TitleFrame: title_frame.yaml

class Builder:
    tk_variables = {}
    tk_widgets = {}
    
    def __init__(self, root_class, addons_classes=[]):
        # make a lookup by name
        self.addons = {}
        for addon_class in addons_classes:
            self.addons[addon_class.__name__] = addon_class
        
        # create the root
        self.root = root_class()
        self.current_root = self.root
        
        # build the root
        data = self._get_file_data(self.root.yaml_file)
        data = data[root_class.__name__] # only need contents under the widget name
        self._build_widget(self.root, data)
        
        # keep a reference to widgets with ids and tk varables
        self.root.tk_widgets = self.tk_widgets
        self.root.tk_variables = self.tk_variables
    
    def _get_file_data(self, filename):
        with open(filename) as f:
            data = yaml.load(f, Loader)
        return data
    
    def _create_widget(self, data, parent=None):
        # the first key should be the name of the widget
        widget_name = next(iter(data.keys()))
        
        # instanciate the widget
        if widget_name in self.addons:
            # widget is one of addons
            widget = self.addons[widget_name]()
            self.previous_root = self.current_root
            self.current_root = widget
            data = self._get_file_data(widget.yaml_file)
            self._build_widget(widget, data[widget_name])
            self.current_root = self.previous_root
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
                    cmd = getattr(self.current_root, value)
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
