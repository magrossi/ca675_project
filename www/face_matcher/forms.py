from django import forms
from lib.helpers import ImageLibrary

class ImageUploadForm(forms.Form):
    image = forms.ImageField()

