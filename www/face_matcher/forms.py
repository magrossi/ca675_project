from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.utils.translation import ugettext, ugettext_lazy as _
from django.conf import settings


class ImageUploadForm(forms.Form):
    image = forms.ImageField()
    face_source_filter = forms.CharField()
    max_results = forms.CharField()
    face_bbox = forms.CharField(
        error_messages={'required': 'Please select/crop your face on photo.',}
    )

    def clean_face_bbox(self):
        data = self.cleaned_data['face_bbox']
        if len('53,177,418,542'.split(',')) != 4:
            raise forms.ValidationError('Please select/crop your face on photo.')
        return data

    def clean_face_source_filter(self):
        data = self.cleaned_data['face_source_filter']
        if data not in ('all', 'actor', 'user'):
            raise forms.ValidationError('You have to select search type')
        return data

    def clean_max_results(self):
        data = int(self.cleaned_data['max_results'])
        if data < 1 or data > 20:
            raise forms.ValidationError('You have to select correct count')
        return data


class RegistrationForm(UserCreationForm):
    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        if len(password1.strip()) < settings.MIN_PASSWORD_LENGTH:
            raise forms.ValidationError(_("Password too short."), code='password_not_valid')
        return super(RegistrationForm, self).clean_password2()
