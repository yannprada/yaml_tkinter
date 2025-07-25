"""
yamltk.py

A utility for building Tkinter GUI widget trees from YAML configuration files.

This module provides the `Builder` class, which reads a YAML file describing the 
widget hierarchy and properties, then instantiates and configures Tkinter widgets 
accordingly. It supports custom branch classes, variable binding, and flexible 
widget configuration, making it easy to define complex GUIs declaratively.

Typical usage:
    import yamltk

    root = yamltk.build(MyRootWidget, [MyBranchWidget, ...])
    root.mainloop()

YAML files should specify the widget structure, options, and variables. See the 
example YAML and widget classes for details.

Author: Yannick Pradayrol (2025)
"""

import tkinter as tk
import yaml
try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader


def build(root_class, branch_classes=None):
    """Build the branches and returns the root."""
    builder = Builder(root_class, branch_classes)
    return builder.root


TK_VARIABLES = {
    'boolean': tk.BooleanVar, 
    'double': tk.DoubleVar, 
    'int': tk.IntVar, 
    'string': tk.StringVar
}


def _check_param(param, msg):
    """Raises an AttributeError with the given message if `param` is None."""
    if param is None:
        raise AttributeError(msg)


class Builder:
    def __init__(self, root_class, branch_classes=None):
        """
        Initializes the Builder with a root widget class and a list of branch 
        (child) widget classes.

        Args:
            root_class (type): The class of the root Tkinter widget 
                               (must have a `yaml_file` attribute).
            branch_classes (list[type]): List of branch widget classes to support 
                                         as children.

        Side Effects:
            - Instantiates the root widget.
            - Loads the YAML file specified by the root widget.
            - Builds the widget tree according to the YAML structure.
            - Calls the root's `post_build()` method if it exists.
        """
        # make a lookup by name
        if branch_classes is None:
            branch_classes = []
        self.branches = {cls.__name__: cls for cls in branch_classes}
        
        # create the root
        self.root = root_class()
        self.root.builder = self
        self.current_branch = self.root
        
        # build the root
        data = self._get_file_data(self.root.yaml_file)
        data = data[root_class.__name__] # only need contents under the widget name
        self._build_widget(self.root, data)
        
        if hasattr(self.root, 'post_build'):
            self.root.post_build(*data.get('post_build_args', []),
                                 **data.get('post_build_kwargs', {}))
    
    def _get_file_data(self, filename):
        # Loads and parses YAML data from the specified file.
        with open(filename) as f:
            data = yaml.load(f, Loader)
        return data
    
    def add_branch(self, branch_name, name, parent, data=None):
        """
        Instantiates a known branch widget and adds it to the widget tree.

        Args:
            branch_name (str): The name of the branch class to instantiate.
            name (str or None): The name to assign to the new widget 
                                (used as an attribute on the parent).
            parent (tk.Widget): The parent widget to attach the new branch to.
            data (dict, optional): Additional YAML data for the branch. 
                                   If None, loads from the branch's YAML file.

        Returns:
            tk.Widget: The newly created branch widget.

        Raises:
            AttributeError: If the branch_name is not found in the registered 
                            branches.
        """
        widget_class = self.branches.get(branch_name)
        msg = f'add_branch: branch does not exist: {branch_name}'
        _check_param(branch_name, msg)
        
        # gather data from class yaml file
        file_data = {}
        if hasattr(widget_class, 'yaml_file'):
            file_data = self._get_file_data(widget_class.yaml_file)
            file_data = file_data[branch_name]
        
        # if name is not provided, try to get it from file data
        if name is None:
            name = file_data.pop('name', name)
        
        # create the widget
        widget = self._create(widget_class, parent, name)
        widget.builder = self
        
        previous_branch = self.current_branch
        self.current_branch = widget
        
        if isinstance(data, dict):
            self._build_widget(widget, data)
        
        if len(file_data) > 0:
            self._build_widget(widget, file_data)
        
        if hasattr(widget, 'post_build'):
            widget.post_build(*data.get('post_build_args', []),
                              **data.get('post_build_kwargs', {}))
        
        self.current_branch = previous_branch
        return widget
    
    def _create(self, widget_class, parent, name=None):
        # Instantiates a widget of the given class, attaches it to the parent, 
        # and assigns it as an attribute if named.
        widget = widget_class(parent, name=name)
        widget.parent = parent
        if name is not None:
            setattr(self.current_branch, name, widget)
        return widget
    
    def _create_widget(self, data, parent=None):
        # the first key should be the name of the widget
        widget_name = next(iter(data.keys()))
        data = data[widget_name]
        
        name = None
        if isinstance(data, dict) and data.get('name'):
            name = data.pop('name')
        
        # instanciate the widget
        if widget_name in self.branches:
            self.add_branch(widget_name, name, parent, data)
        else:
            widget_class = getattr(tk, widget_name)
            widget = self._create(widget_class, parent, name)
            self._build_widget(widget, data)
    
    def _build_widget(self, widget, data):
        # Recursively configures a widget and its children.
        def dummy(*args):
            pass

        options = widget.configure()

        actions = {
            'children': self._handle_children,
            'variable': self._handle_variable,
            'list_variable': self._handle_list_variable,
            'text_variable': self._handle_text_variable,
            'app_command': self._handle_app_command,
            'app_command_event': self._handle_app_command_event,
            'pack': self._handle_pack,
            'grid': self._handle_grid,
            'font_size': self._handle_font_size,
            'minsize': self._handle_minsize,
            'post_build_args': dummy,
            'post_build_kwargs': dummy
        }
        
        for key, value in data.items():
            action = actions.get(key, self._handle_default)
            action(widget, key, value, options)
    
    def _handle_children(self, widget, key, value, options):
        for child_data in value:
            self._create_widget(child_data, widget)
    
    def _handle_variable(self, widget, key, value, options):
        widget.configure(variable=self._get_variable(widget, value))
    
    def _handle_list_variable(self, widget, key, value, options):
        widget.configure(listvariable=self._get_variable(widget, value))
    
    def _handle_text_variable(self, widget, key, value, options):
        widget.configure(textvariable=self._get_variable(widget, value))
    
    def _handle_app_command(self, widget, key, value, options):
        cmd = getattr(self.current_branch, value)
        widget.configure(command=cmd)
    
    def _handle_app_command_event(self, widget, key, value, options):
        cmd = lambda branch=self.current_branch: branch.event_generate(f'<<{value}>>')
        widget.configure(command=cmd)

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
        if isinstance(value, list):
            widget.minsize(*value)
    
    def _handle_default(self, widget, key, value, options):
        if key in options:
            widget.configure(**{key: value})
        else:
            method = getattr(widget, key)
            # for methods that take more than one argument, 
            # specify them as a list in the yaml file
            if type(value) is list and method.__code__.co_argcount > 1:
                method(*value)
            else:
                method(value)
    
    def _get_variable(self, widget, data):
        # Retrieves or creates a Tkinter variable for the given widget.
        name = data['name']
        
        # check if the variable has already been created
        if hasattr(self.current_branch, name):
            return getattr(self.current_branch, name)
        
        # otherwise, create the variable, using the appropriate type
        var_class = TK_VARIABLES.get(data['type'])
        if var_class is None:
            raise TypeError(f"Unexpected variable type: {data['type']}")
        
        # instantiate with default value if any
        var_instance = var_class(value=data.get('default'))
        
        # assign it as a member of current branch
        setattr(self.current_branch, name, var_instance)
        
        return var_instance
