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


# TODO: 

class Builder:
    tk_variables = {}
    tk_widgets = {}
    
    def __init__(self, root_class, branch_classes):
        # make a lookup by name
        self.branches = {cls.__name__: cls for cls in branch_classes}
        
        # create the root
        self.root = root_class()
        self.branch = self.root
        
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
        if widget_name in self.branches:
            # widget is one of branches
            widget = self.branches[widget_name]()
            previous_branch = self.branch
            self.branch = widget
            
            data = self._get_file_data(widget.yaml_file)
            self._build_widget(widget, data[widget_name])
            
            self.branch = previous_branch
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
                    cmd = getattr(self.branch, value)
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
