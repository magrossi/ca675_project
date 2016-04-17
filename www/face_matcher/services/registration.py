from django.contrib.auth import authenticate, login
from face_matcher.forms import RegistrationForm


class RegistrationService(object):
    def __init__(self, request):
        self.request = request
        self.form = RegistrationForm(self.request.POST)

    def register(self):
        is_registered = False
        if self.form.is_valid():
            self.form.save()
            user = authenticate(
                username=self.form.cleaned_data['username'],
                password=self.form.cleaned_data['password1']
            )
            login(self.request, user)
            is_registered = True
        return is_registered
