from django import forms


class ImageUploadForm(forms.Form):
    image = forms.ImageField()
    face_source_filter = forms.CharField()
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
