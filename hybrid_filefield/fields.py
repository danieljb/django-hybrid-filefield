# -*- coding: utf-8 -*-

import os

from django.conf import settings
from django.db import models
from django.utils.translation import ugettext as _
from django.db.models.fields.files import FieldFile

from hybrid_filefield.forms import FileSelectOrUploadField
from hybrid_filefield.storage import FileSelectOrUploadStorage


def set_dynamic_attrs(self, instance=None):
    for key in self.callable_parameters:
        if hasattr(self, key):
            setattr(self, key, self.original_callables[key](self, instance))


class FileSelectOrUpload(models.FileField):

    description = _('Select a file from path or upload a file')
    storage = FileSelectOrUploadStorage()

    def __init__(self, verbose_name=None, name=None,
        upload_to='', path='', match=None, recursive=False,
        copy_file=False, **kwargs):

        self.original_callables = {
            'upload_to': upload_to,
            'path': path,
            'help_text': kwargs.get('help_text'),
            'copy_file': copy_file,
        }
        self.update_dynamic_attrs()

        self.upload_to, self.path, self.match, \
        self.recursive, self.copy_file, self.name = \
            upload_to, path, match, recursive, copy_file, name

        models.FileField.__init__(
            self,
            verbose_name,
            name,
            upload_to=upload_to,
            storage=kwargs.pop('storage', self.storage),
            max_length=kwargs.pop('max_length', 200),
            **kwargs
        )

    def store_data(self, data, instance=None):
        if not data:
            return None
        set_dynamic_attrs(self, instance)

        destination = os.path.normpath(os.path.join(
            settings.MEDIA_ROOT,
            self.upload_to))
        if data._committed and (os.path.dirname(data.path) != destination):
            if self.copy_file:
                data = self.storage.copy(data.name, destination)
            else:
                data = self.storage.move(data.name, destination)
        if instance:
            super(FileSelectOrUpload, self).save_form_data(instance, data)
        return data

    def update_dynamic_attrs(self):
        self.callable_parameters = []
        for key in self.original_callables:
            if callable(self.original_callables.get(key)):
                self.callable_parameters.append(key)

    def contribute_to_class(self, cls, name):
        super(FileSelectOrUpload, self).contribute_to_class(cls, name)
        models.signals.post_init.connect(self._update_attrs, sender=cls)
        models.signals.pre_save.connect(self._update_attrs, sender=cls)

    def _update_attrs(self, instance=None, **kwargs):
        setattr(
            instance,
            'store_{0}'.format(self.name),
            lambda: self.store_data(
                getattr(instance, self.name, None), instance=instance))
        set_dynamic_attrs(self, instance)

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

    def to_python(self, data):
        data = super(FileSelectOrUpload, self).to_python(data)
        if data is None:
            return None

        return self.store_data(data)

    def get_prep_value(self, value):
        if value and isinstance(value, FieldFile):
            return os.path.relpath(
                os.path.normpath(value.path), settings.MEDIA_ROOT)
        return super(FileSelectOrUpload, self).get_prep_value(value)

    def save_form_data(self, instance, data):
        set_dynamic_attrs(self, instance)
        if data is not None:
            file = self.storage.save(data._get_name(), data)
            file = self.storage.move(
                file,
                os.path.realpath(os.path.join(
                    settings.MEDIA_ROOT,
                    self.upload_to)))
            data = os.path.relpath(file, settings.MEDIA_ROOT)
        super(FileSelectOrUpload, self).save_form_data(instance, data)


try:
    from south.modelsinspector import add_introspection_rules

    rules = [
      (
        (FileSelectOrUpload,),
        [],
        {
            'upload_to': ['upload_to', {'default': '', 'ignore_if': 'upload_to'}],
            'path': ['path', {'ignore_if': 'path'}],
            'match': ['match', {'default': None,}],
            'recursive': ['recursive', {'default': False,}],
            'copy_file': ['copy_file', {'default': False,}],
        },
      )
    ]
    add_introspection_rules(rules, ["^hybrid_filefield\.fields"])
except ImportError:
    pass

