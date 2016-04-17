from face_matcher.models import Face
from face_matcher.templatetags.face_matcher_extras import (
    calc_time,
    multiply_100,
    status_label_class,
)


class HistoryJson(object):
    def __init__(self, history):
        self.history = history

    def _get_base_data(self):
        return {
            'status': self.history.status,
            'status_label_class': status_label_class(self.history.status),
        }

    def _get_finished_data(self):
        top_matcher = self.history.historyitem_set.all()[0]
        top_matcher_face = top_matcher.face
        top_matcher_name = (top_matcher_face.face_source == Face.ACTOR_SOURCE and top_matcher_face.actor.name
                                                                or top_matcher_face.user.username)

        data = dict(
            generated=calc_time(self.history),
            status_string=self.history.get_status_display(),
            top_matcher_source=top_matcher_face.face_source,
            top_matcher_name=top_matcher_name,
            top_matcher_similarity_score=multiply_100(top_matcher.similarity_score),
            history_items=[],
        )
        for history_item in self.history.historyitem_set.all():
            data['history_items'].append({
                'similarity_score': multiply_100(history_item.similarity_score),
                'image': history_item.face.url,
            })
        return data

    def present(self):
        if not self.history.finished:
            return self._get_base_data()
        return dict(self._get_base_data(), **self._get_finished_data())
