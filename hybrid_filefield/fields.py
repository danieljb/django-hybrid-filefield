# -*- coding: utf-8 -*-

import os

from django.conf import settings
from django.db import models
from django.utils.translation import ugettext as _

from hybrid_filefield.forms import FileSelectOrUploadField
from hybrid_filefield.storage import FileSelectOrUploadStorage

def init_dynamic_attrs(self, callables):
    
    self.callable_parameters = []
    
    for key in callables:
        if callable(callables.get(key)):
            self.callable_parameters.append(key)
    

def set_dynamic_attrs(self, instance=None):
    
    if not instance:
        for key in self.callable_parameters:
            if hasattr(self, key):
                setattr(self, key, getattr(self, key)(self, instance))
    

class FileSelectOrUpload(models.FileField):
    
    description = _('Select a file from path or upload a file')
    storage = FileSelectOrUploadStorage()
    
    def __init__(self, verbose_name=None, name=None, 
        upload_to='', path='', match=None, recursive=False, 
        copy_file=False, **kwargs):
        
        init_dynamic_attrs(self, {
            'upload_to': upload_to,
            'path': path,
            'help_text': kwargs.get('help_text'),
            'copy_file': copy_file,
        })
        
        self.upload_to, self.path, self.match, self.recursive, self.copy_file = \
            upload_to, path, match, recursive, copy_file
        
        models.FileField.__init__(
            self, 
            verbose_name, 
            name, 
            upload_to=upload_to,
            storage=kwargs.pop('storage', self.storage), 
            max_length=kwargs.pop('max_length', 200),
            **kwargs
        )
    
    def copy(self, file, new_path):
        return self.storage.copy(file, new_path)
    
    def move(self, file, new_path):
        return self.storage.move(file, new_path)
    
    def contribute_to_class(self, cls, name):
        super(FileSelectOrUpload, self).contribute_to_class(cls, name)
        models.signals.post_init.connect(self._post_init, sender=cls)
        
    def _post_init(self, instance=None, **kwargs):
        set_dynamic_attrs(self, instance)
        self.path = os.path.realpath(self.path)
    
    def formfield(self, **kwargs):
        defaults = {
            'form_class': FileSelectOrUploadField,
            'upload_to': self.upload_to,
            'path': self.path,
            'match': self.match,
            'recursive': self.recursive,
            'optional': True,
        }
        defaults.update(kwargs)
        
        w = defaults.get('widget')
        if w and w is not None:
            del defaults['widget']
        
        return super(FileSelectOrUpload, self).formfield(**defaults)
    
    def pre_save(self, instance, add):
        file = super(FileSelectOrUpload, self).pre_save(instance, add)
        
        if file:
            if self.copy_file:
                _new_file = self.copy(file.name, os.path.realpath(os.path.join(settings.MEDIA_ROOT, self.upload_to)))
            else:
                _new_file = self.move(file.name, os.path.realpath(os.path.join(settings.MEDIA_ROOT, self.upload_to)))
            file = self.storage.open(_new_file)
            return os.path.relpath(file.name, settings.MEDIA_ROOT)
        return None
    
    def save_form_data(self, instance, data):
        if data is not None and not False: 
            super(FileSelectOrUpload, self).save_form_data(instance, data)
    

try:
    from south.modelsinspector import add_introspection_rules
    
    rules = [
      (
        (FileSelectOrUpload,),
        [],
        {
            'upload_to': ['upload_to', {'default': '',}],
            'path': ['path', {'default': '',}],
            'match': ['match', {'default': None,}],
            'recursive': ['recursive', {'default': False,}],
            'copy_file': ['copy_file', {'default': False,}],
        },
      )
    ]
    add_introspection_rules(rules, ["^hybrid_filefield\.fields"])
except ImportError:
    pass

