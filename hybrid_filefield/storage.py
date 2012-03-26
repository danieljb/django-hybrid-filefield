# -*- coding: utf-8 -*-

import os
from django.core.files import storage


class FileSelectOrUploadStorage(storage.FileSystemStorage):

    def copy(self, name, new_path, reset_path=True):
        _filename, _extension = os.path.splitext(os.path.basename(name))
        _file = self.open(self.path(name))
        _original_path = self.location

        self.location = os.path.realpath(os.path.abspath(new_path))
        _new_file = self.save(self.path(''.join([_filename, _extension])), _file)

        if reset_path is True:
            self.location = _original_path

        return _new_file

    def move(self, name, new_path, reset_path=True):
        _new_file = self.copy(name, new_path, reset_path=True)

        self.delete(name)
        if reset_path is False:
            self.location = os.path.realpath(os.path.abspath(new_path))

        return _new_file

