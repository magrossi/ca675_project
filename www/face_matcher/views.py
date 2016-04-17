import uuid
from os.path import splitext

from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from face_matcher.forms import ImageUploadForm, RegistrationForm
from face_matcher.models import History, Face
from face_matcher.tasks import find_similars
from face_matcher.presenters.history import HistoryJson
from lib.helpers import ImageLibrary


def index(request):
    context_dict = {
        'form': AuthenticationForm(),
    }
    return render(request, 'face_matcher/index.html', context_dict)


def registration(request):
    form = None
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            user = authenticate(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password1']
            )
            login(request, user)
            return redirect(settings.LOGIN_REDIRECT_URL)

    context_dict = {
        'form': form and form or RegistrationForm(),
    }
    return render(request, 'face_matcher/registration.html', context_dict)


@login_required
def matcher(request):
    form = None
    user = request.user

    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)

        if form.is_valid():
            img_file = request.FILES['image']
            _, img_extension = splitext(img_file.name)
            rel_img_path = 'user/{}/{}{}'.format(user.id, uuid.uuid4().hex, img_extension)
            ImageLibrary.save_image(img_file.read(), rel_img_path)
            face_bbox = form.cleaned_data['face_bbox']
            face = Face.objects.create(
                user=user,
                url=ImageLibrary.get_image_url(rel_img_path),
                face_bbox=face_bbox,
                face_img_path=rel_img_path,
            )
            history = History.objects.create(user=user, in_face=face)

            face_source_filter = form.cleaned_data['face_source_filter']
            max_results = form.cleaned_data['max_results']

            find_similars.delay(
                history.id,
                face_source_filter=face_source_filter,
                max_results=max_results,
            )

            return redirect('/history/')

    context_dict = {
        'form': form and form or ImageUploadForm()
    }
    return render(request, 'face_matcher/matcher.html', context_dict)


@login_required
def history(request):
    history_list = History.objects.filter(user=request.user)
    paginator = Paginator(history_list, 10)  # Show 10 items per page

    page = request.GET.get('page')

    try:
        history = paginator.page(page)
    except PageNotAnInteger:
        history = paginator.page(1)
    except EmptyPage:
        history = paginator.page(paginator.num_pages)

    context_dict = {
        'history': history
    }
    return render(request, 'face_matcher/history.html', context_dict)


@login_required
@csrf_exempt
def get_json_histroy(request, id):
    history = History.objects.get(user=request.user, pk=id)
    return JsonResponse(HistoryJson(history).present())
