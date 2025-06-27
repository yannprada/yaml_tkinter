import tkinter as tk
import yaml
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper


def build(filename):
    with open(filename) as f:
        data = yaml.load(f, Loader)
        return _build_widget(data)


def _build_widget(data, marked_widgets={}, parent=None):
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
                    child_widget, marked_widgets = _build_widget(child_data, marked_widgets, widget)
                continue
            case 'id':
                marked_widgets[value] = widget
            case _:
                if hasattr(widget, key):
                    method = getattr(widget, key)
                    method(value)
                elif key in options:
                    widget.configure(**{key: value})
                else:
                    raise AttributeError(f'Invalid attribute "{key}" for widget "{widget_name}"')
    
    return widget, marked_widgets


if __name__ == '__main__':
    root, marked_widgets = build('./example.yaml')
    
    button = marked_widgets['click_me_button']
    # or
    button = root.nametowidget('!frame2.!button')
    
    button.configure(command=quit)
    root.mainloop()