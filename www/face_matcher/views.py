from django.shortcuts import render
from face_matcher.models import Upload


def index(request):
    uploads = Upload.objects.all()[:10]
    context_dict = {'uploads': uploads}
    return render(request, 'face_matcher/index.html', context_dict)


def about(request):
    context_dict = {'boldmessage': "I am bold font from the context"}
    return render(request, 'face_matcher/about.html', context_dict)
