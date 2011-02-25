# Django Hybrid-FileField #

A combination of Django's FileField and FilePathField.

# Installation #

Using pip:

pip install -e git+http://github.com/danieljb/django-hybrid-filefield.git#egg=hybrid_filefield

# Example Usage #

Usage of Hybrid-FileField in an image Model:

    from django.db import models
    from django.utils.translation import ugettext_lazy as _
    from django.conf import settings
    
    from hybrid_filefield.fields import FileSelectOrUpload
    
    IMAGE_PATH          = getattr(settings, 'IMAGE_PATH', os.path.join(settings.MEDIA_ROOT, 'images'))
    IMAGE_SEARCH_PATH   = getattr(settings, 'IMAGE_SEARCH_PATH', os.path.join(IMAGE_PATH, 'ftp_uploads'))
    IMAGE_FILTER        = '.+\.jpg'
    
    class ImageModel(models.Model):
        image_file = FileSelectOrUpload(
            verbose_name=_('Image File'),
            path=IMAGE_SEARCH_PATH, 
            upload_to=IMAGE_PATH, 
            match=IMAGE_FILTER,
            help_text=_( 
                'Select an image file which was uploaded to %(search_path)s on the server or upload an image via http.' % 
                    {'search_path': os.path.relpath(os.path.realpath(IMAGE_SEARCH_PATH), settings.MEDIA_ROOT),}
            ),
        )

## Parameters ##

#### FileSelectOrUpload.upload_to ####

Path where files will be stored when uploaded via FileField or selected in the FilePathField.

#### FileSelectOrUpload.path ####

Path to search for files matching `FileSelectOrUpload.match`, matching files will be listed in FilePathField.

#### FileSelectOrUpload.match ####

Pattern defining which files will be listed in FilePathField.

#### FileSelectOrUpload.copy_file ####

If `True` file selected in FilePathField will be copied to `FileSelectOrUpload.upload_to` directory instead of being moved.

# Copyright #

Django Hybrid-FileField is distributed under GNU General Public License. 
You should have received a copy of the GNU General Public License along 
with Django Hybrid-FileField.  
If not, see <http://www.gnu.org/licenses/>.

Copyright (c) 2011, Daniel J. Becker
