import uuid
from os.path import splitext

from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from .forms import ImageUploadForm, RegistrationForm
from .models import History, Face
from .tasks import find_similars
from .templatetags.face_matcher_extras import calc_time, multiply_100, status_label_class
from lib.helpers import ImageLibrary
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.conf import settings
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse


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
            rel_img_path = 'user/{}/{}{}'.format(user.id, uuid.uuid1().hex, img_extension)
            try:
                ImageLibrary.save_image(img_file.read(), rel_img_path)
            except:
                raise  # todo: handle save exception
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

    result_dict = {
        'status': history.status,
        'status_label_class': status_label_class(history.status),
    }

    if history.status not in 'FE':
        return JsonResponse(result_dict)

    top_matcher = (history.historyitem_set.all() or [None,])[0]

    if top_matcher:
        top_matcher_face = top_matcher.face
        top_matcher_name = top_matcher_face.face_source == 'A' and top_matcher_face.actor.name \
                       or top_matcher_face.user.username
        result_dict['top_matcher_similarity_score'] = multiply_100(top_matcher.similarity_score)
        result_dict['top_matcher_name'] = top_matcher_name
        result_dict['top_matcher_source'] = top_matcher_face.face_source

    result_dict['generated'] = calc_time(history)
    result_dict['status_string'] = history.get_status_display()
   
    result_dict['history_items'] = []

    for history_item in history.historyitem_set.all():
        result_dict['history_items'].append(
            {
                'similarity_score': multiply_100(history_item.similarity_score),
                'image': history_item.face.face_img_path,
            }
        )
    return JsonResponse(result_dict)
