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
    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)

        if form.is_valid():
            img_file = request.FILES['image']
            # todo: set filename from settings
            img_path = 'test/{}'.format(img_file.name)
            try:
                ImageLibrary.save_image(img_file.read(), img_path)
            except:
                raise  # todo: handle save exception

            face = Face.objects.create(
                user=request.user,
                url='http://google.com/',  # todo: fixme
                face_bbox='fixme',  # fixme
                face_img_path=img_path,
            )
            history = History.objects.create(user=request.user, in_face=face)
            find_similars.delay(history.id)

    context_dict = {
        'form': form and form or ImageUploadForm(),
        'history': History.objects.all()
    }
    return render(request, 'face_matcher/faces.html', context_dict)
