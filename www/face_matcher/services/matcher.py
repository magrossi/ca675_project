import uuid
from os.path import splitext
from django.contrib.auth import authenticate, login
from face_matcher.services import BaseService
from face_matcher.forms import ImageUploadForm
from face_matcher.models import History, Face
from face_matcher.tasks import find_similars
from lib.helpers import ImageLibrary


class FaceMatcherService(BaseService):
    def __init__(self, request):
        super(FaceMatcherService, self).__init__(request, ImageUploadForm(request.POST,
                                                                          request.FILES))
        self.user = request.user

    def _save_request_image(self):
        img_file = self.request.FILES['image']
        _, img_extension = splitext(img_file.name)
        rel_img_path = 'user/{}/{}{}'.format(self.user.id, uuid.uuid4().hex, img_extension)
        ImageLibrary.save_image(img_file.read(), rel_img_path)
        return img_file, rel_img_path

    def match_upload(self):
        is_valid_upload = self.form.is_valid()
        if is_valid_upload:
            _, img_path = self._save_request_image()

            face = Face.objects.create(
                user=self.user,
                url=ImageLibrary.get_image_url(img_path),
                face_bbox=self.form.cleaned_data['face_bbox'],
                face_img_path=img_path,
            )

            find_similars.delay(
                History.objects.create(user=self.user, in_face=face).id,
                face_source_filter=self.form.cleaned_data['face_source_filter'],
                max_results=self.form.cleaned_data['max_results'],
            )
        return is_valid_upload
