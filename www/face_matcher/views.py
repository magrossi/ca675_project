import uuid
from os.path import splitext

from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from face_matcher.forms import ImageUploadForm, RegistrationForm
from face_matcher.models import History, Face
from face_matcher.tasks import find_similars
from face_matcher.presenters.history import HistoryJson, HistoryIndex
from face_matcher.services.registration import RegistrationService
from face_matcher.services.matcher import FaceMatcherService
from lib.helpers import ImageLibrary


def index(request):
    return render(request, 'face_matcher/index.html', {'form': AuthenticationForm()})


def registration(request):
    form = None
    if request.method == 'POST':
        registration_serivce = RegistrationService(request)
        if registration_serivce.register():
            return redirect(settings.LOGIN_REDIRECT_URL)
        else:
            form = registration_serivce.form

    context_dict = {'form': form and form or RegistrationForm()}
    return render(request, 'face_matcher/registration.html', context_dict)


@login_required
def matcher(request):
    form = None
    if request.method == 'POST':
        matcher_service = FaceMatcherService(request)
        if matcher_service.match_upload():
            return redirect('/history/')
        else:
            form = matcher_service.form

    context_dict = {'form': form and form or ImageUploadForm()}
    return render(request, 'face_matcher/matcher.html', context_dict)


@login_required
def history(request):
    presenter = HistoryIndex(History.objects.filter(user=request.user),
                             request.GET.get('page'))
    return render(request, presenter.template, presenter.present())


@login_required
@csrf_exempt
def get_json_histroy(request, id):
    history = History.objects.get(user=request.user, pk=id)
    return JsonResponse(HistoryJson(history).present())
