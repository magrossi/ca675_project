from django.shortcuts import render

context_dict = {'boldmessage': "I am bold font from the context"}


def index(request):
    return render(request, 'face_matcher/index.html', context_dict)


def about(request):
    return render(request, 'face_matcher/about.html', context_dict)
