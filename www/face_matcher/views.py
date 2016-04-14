import uuid
from os.path import splitext

from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .forms import ImageUploadForm
from .models import History, Face
from .tasks import find_similars
from lib.helpers import ImageLibrary
from django.contrib.auth.decorators import login_required


def index(request):
    context_dict = {
        'form': AuthenticationForm(),
    }
    return render(request, 'face_matcher/index.html', context_dict)


def registration(request):
    form = None
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/')

    context_dict = {
        'form': form and form or UserCreationForm(),
    }
    return render(request, 'face_matcher/registration.html', context_dict)


@login_required
def faces(request):
    form = None
    user = request.user

    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)

        if form.is_valid():
            img_file = request.FILES['image']
            _, img_extension = splitext(img_file.name)
            img_path = 'user/{}/{}{}'.format(user.id, uuid.uuid1().hex, img_extension)
            ImageLibrary.save_image(img_file.read(), img_path)
            face_bbox = form.cleaned_data['face_bbox']
            face = Face.objects.create(
                url=ImageLibrary.get_image_url(img_path),
                user=request.user,
                face_bbox=face_bbox,
                face_img_path=img_path,
            )
            history = History.objects.create(user=request.user, in_face=face)

            face_source_filter = form.cleaned_data['face_source_filter']
            find_similars.delay(history.id, face_source_filter=face_source_filter)

    context_dict = {
        'form': form and form or ImageUploadForm(),
        'history': History.objects.filter(user=request.user)
    }
    return render(request, 'face_matcher/faces.html', context_dict)
