# -*- coding: utf-8 -*-

from django.conf import settings
from django.forms.widgets import MultiWidget, Select
from django.contrib.admin.widgets import AdminFileWidget


class FileSelectOrUploadWidget(MultiWidget):
    
    def __init__(self, attrs=None):
        
        widgets = (
            Select(),
            AdminFileWidget(),
        )
        super(FileSelectOrUploadWidget, self).__init__(
            widgets,
            attrs
        )
    
    def _get_choices(self):
        return self.widgets[0].choices
    
    def _set_choices(self, value):
        self.widgets[0].choices = list(value)
    
    choices = property(_get_choices, _set_choices)
    
    def _get_required(self):
        return self.widgets[1].is_required
    
    def _set_required(self, value):
        self.widgets[1].is_required = value
    
    is_required = property(_get_required, _set_required)
    
    # def value_from_datadict(self, data, files, name):
    #     return [widget.value_from_datadict(data, files, name + '_%s' % i) for i, widget in enumerate(self.widgets)]
    
    def decompress(self, value):
        if value:
            return [value, value]
        return [None, None]
    
    def format_output(self, rendered_widgets):
        widgets = ['<p>%s</p>' % w for w in rendered_widgets]
        return '\n'.join(widgets)
    
