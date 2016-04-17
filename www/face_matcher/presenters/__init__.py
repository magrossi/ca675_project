class BasePresenter(object):
    template = None

    def __init__(self, presentee):
        self.presentee = presentee
