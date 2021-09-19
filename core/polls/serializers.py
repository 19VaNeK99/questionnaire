from rest_framework import serializers
from .models import Question


class QuestionSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Question
        fields = ['pk', 'title', 'max_points', ]

