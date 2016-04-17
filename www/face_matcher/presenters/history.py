from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from face_matcher.models import Face
from face_matcher.presenters import BasePresenter
from face_matcher.templatetags.face_matcher_extras import (
    calc_time,
    multiply_100,
    status_label_class,
)


class HistoryIndex(BasePresenter):
    template = 'face_matcher/history.html'

    def __init__(self, histories, at_page):
        super(HistoryIndex, self).__init__(histories)
        self.at_page = at_page

    def _get_paged_data(self):
        paginator = Paginator(self.presentee, 10)
        try:
            histories = paginator.page(self.at_page)
        except PageNotAnInteger:
            histories = paginator.page(1)
        except EmptyPage:
            histories = paginator.page(paginator.num_pages)
        return {'history': histories}

    def present(self):
        return self._get_paged_data()


class HistoryJson(BasePresenter):
    def _get_base_data(self):
        return {
            'status': self.presentee.status,
            'status_label_class': status_label_class(self.presentee.status),
        }

    def _get_finished_data(self):
        top_matcher = self.presentee.historyitem_set.all()[0]
        top_matcher_face = top_matcher.face
        top_matcher_name = (top_matcher_face.face_source == Face.ACTOR_SOURCE and top_matcher_face.actor.name
                                                                or top_matcher_face.user.username)

        data = dict(
            generated=calc_time(self.presentee),
            status_string=self.presentee.get_status_display(),
            top_matcher_source=top_matcher_face.face_source,
            top_matcher_name=top_matcher_name,
            top_matcher_similarity_score=multiply_100(top_matcher.similarity_score),
            history_items=[],
        )
        for history_item in self.presentee.historyitem_set.all():
            data['history_items'].append({
                'similarity_score': multiply_100(history_item.similarity_score),
                'image': history_item.face.url,
            })
        return data

    def present(self):
        if not self.presentee.finished:
            return self._get_base_data()
        return dict(self._get_base_data(), **self._get_finished_data())
