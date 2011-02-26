# -*- coding: utf-8 -*-

import os
import re

from django.conf import settings
from django.core import validators
from django.core.exceptions import ValidationError
from django.forms.util import ErrorList
from django.forms.fields import MultiValueField, FilePathField, FileField, CharField
from django.utils.translation import ugettext as _

from hybrid_filefield.widgets import FileSelectOrUploadWidget


class FileSelectOrUploadField(MultiValueField):
    widget = FileSelectOrUploadWidget
    default_error_messages = {
        'optional_required': _('At least one value is required.'),
    }
    
    def __init__(self, upload_to='', path='', match='', 
        recursive=False, widget=None, initial=None, 
        optional=False, *args, **kwargs): 

        self.upload_to, self.path, self.match, self.recursive, self.initial, self.optional = \
            upload_to, path, match, recursive, initial, optional
        
        self.max_length = kwargs.pop('max_length', None)
        self.required = getattr(kwargs, 'required', True)

        fields = (
            FilePathField(
                path=self.path, 
                match=self.match, 
                recursive=self.recursive, 
                initial=self.initial, 
                required=self.required,
            ),
            FileField(
                max_length=self.max_length, 
                initial=self.initial, 
                required=self.required,
            ),
        )
        
        widget = widget or self.widget
        if isinstance(widget, type):
            widget = widget()
        self.widget = widget
        
        super(FileSelectOrUploadField, self).__init__(
            fields, 
            widget=self.widget, 
            *args, **kwargs
        )
        
        self.choices = [('', 'Use upload')] + fields[0].choices
        self.widget.is_required = self.required
    
    def _get_choices(self):
        return self._choices

    def _set_choices(self, value):
        self._choices = self.widget.choices = list(value)
    
    choices = property(_get_choices, _set_choices)
    
    def clean(self, value):
        clean_data = []
        errors = ErrorList()
        
        if value in validators.EMPTY_VALUES and self.required:
            raise ValidationError(self.error_messages['required'])
        
        for i, field in enumerate(self.fields):
            try:
                field_value = value[i]
            except IndexError:
                field_value = None
            
            if field_value in validators.EMPTY_VALUES:
                if (self.required and not self.optional):
                    raise ValidationError(self.error_messages['required'])
            else:
                field_value = os.path.normpath(field_value)
                try:
                    clean_data.append(field.clean(field_value))
                except ValidationError, e:
                    errors.extend(e.messages)
            
            if i == len(self.fields) and len(clean_data) == 0:
                raise ValidationError(self.error_messages['optional_required'])
        
        if errors:
            raise ValidationError(errors)
        
        return self.compress(clean_data)
    
    def compress(self, data_list):
        if len(data_list) > 1 and data_list[1] not in validators.EMPTY_VALUES:
            return data_list[1]
        elif len(data_list) > 0 and data_list[0] not in validators.EMPTY_VALUES:
            return data_list[0]
        return None
    
