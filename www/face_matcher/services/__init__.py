class BaseService(object):
    def __init__(self, request, form):
        self.request = request
        self.form = form
