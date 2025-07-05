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


def _check_param(param, msg):
    if param is None:
        raise AttributeError(msg)


# TODO: add support for branches with extra data that would go 
# inside an inner container
# this is different than branches with arguments


class Builder:
    tk_widgets = {}
    
    def __init__(self, root_class, branch_classes):
        # make a lookup by name
        self.branches = {cls.__name__: cls for cls in branch_classes}
        
        # create the root
        self.root = root_class()
        self.root.builder = self
        self.root.tk_variables = {}
        self.current_branch = self.root
        
        # build the root
        data = self._get_file_data(self.root.yaml_file)
        data = data[root_class.__name__] # only need contents under the widget name
        self._build_widget(self.root, data)
        
        # keep a reference to widgets with ids and tk varables
        self.root.tk_widgets = self.tk_widgets
    
    def _get_file_data(self, filename):
        with open(filename) as f:
            data = yaml.load(f, Loader)
        return data
    
    def add_branch(self, branch_name, parent, data=None):
        # instanciate a known Branch and add it to the tree
        if isinstance(parent, str):
            parent_id = parent
            parent = self.tk_widgets.get(parent_id)
            msg = f'add_branch: parent id does not exist: {parent_id}'
            _check_param(parent, msg)
        
        widget_class = self.branches.get(branch_name)
        msg = f'add_branch: branch does not exist: {branch_name}'
        _check_param(branch_name, msg)
        
        widget = widget_class(parent)
        widget.parent = parent
        widget.builder = self
        widget.tk_variables = {}
        if isinstance(data, dict):
            self._build_widget(widget, data)
        
        if hasattr(widget, 'yaml_file'):
            previous_branch = self.current_branch
            self.current_branch = widget
            file_data = self._get_file_data(widget.yaml_file)
            self._build_widget(widget, file_data[branch_name])
            self.current_branch = previous_branch
        
        if hasattr(widget, 'init'):
            if isinstance(data, list):
                widget.init(*data)
            else:
                widget.init()
        
        parent.event_generate('<<on_add_branch>>')
    
    def _create_widget(self, data, parent=None):
        # the first key should be the name of the widget
        widget_name = next(iter(data.keys()))
        
        # instanciate the widget
        if widget_name in self.branches:
            self.add_branch(widget_name, parent, data[widget_name])
        else:
            widget_class = getattr(tk, widget_name)
            widget = widget_class(parent)
            widget.parent = parent
            self._build_widget(widget, data[widget_name])
    
    def _build_widget(self, widget, data):
        options = widget.configure()
        actions = {
            'children': self._handle_children,
            'id': self._handle_id,
            'variable': self._handle_variable,
            'text_variable': self._handle_text_variable,
            'app_command': self._handle_app_command,
            'add_branch': self._handle_add_branch,
            'pack': self._handle_pack,
            'grid': self._handle_grid,
            'font_size': self._handle_font_size,
            'minsize': self._handle_minsize
        }
        
        for key, value in data.items():
            action = actions.get(key, self._handle_default)
            action(widget, key, value, options)
    
    def _handle_children(self, widget, key, value, options):
        for child_data in value:
            self._create_widget(child_data, widget)
    
    def _handle_id(self, widget, key, value, options):
        self.tk_widgets[value] = widget
    
    def _handle_variable(self, widget, key, value, options):
        widget.configure(variable=self._get_variable(widget, value))
    
    def _handle_text_variable(self, widget, key, value, options):
        widget.configure(textvariable=self._get_variable(widget, value))
    
    def _handle_app_command(self, widget, key, value, options):
        cmd = getattr(self.current_branch, value)
        widget.configure(command=cmd)
    
    def _handle_add_branch(self, widget, key, value, options):
        branch_name = value.get('name')
        _check_param(branch_name, 'add_branch: missing parameter: name')
        
        parent_id = value.get('parent_id')
        _check_param(parent_id, 'add_branch: missing parameter: parent_id')
        
        widget.configure(command=lambda: self.add_branch(branch_name, parent_id))
    
    def _handle_pack(self, widget, key, value, options):
        if isinstance(value, list) or isinstance(value, bool):
            widget.pack()
        elif isinstance(value, str):
            if value in ('x', 'y', 'both'):
                widget.pack(fill=value)
            elif value in ('left', 'right', 'top', 'down'):
                widget.pack(side=value)
        else:
            widget.pack(value)
    
    def _handle_grid(self, widget, key, value, options):
        if isinstance(value, list):
            widget.grid(row=value[0], column=value[1])
        else:
            widget.grid(value)
    
    def _handle_font_size(self, widget, key, value, options):
        if isinstance(value, int):
            widget.configure(font=('', value))
        else:
            raise TypeError
    
    def _handle_minsize(self, widget, key, value, options):
        if isinstance(value, list) or isinstance(value, tuple):
            widget.minsize(*value)
    
    def _handle_default(self, widget, key, value, options):
        if key in options:
            widget.configure(**{key: value})
        else:
            method = getattr(widget, key)
            method(value)
    
    def _get_variable(self, widget, data):
        name = data['name']
        
        # check if the variable has already been created
        if name in self.current_branch.tk_variables:
            return self.current_branch.tk_variables[name]
        
        # otherwise, create the variable, using the appropriate type
        var_class = TK_VARIABLES.get(data['type'])
        if var_class is None:
            raise TypeError(f"Unexpected variable type: {data['type']}")
        
        # reference it for later lookup
        var_instance = var_class()
        self.current_branch.tk_variables[name] = var_instance
        return var_instance
