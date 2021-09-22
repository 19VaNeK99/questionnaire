from django.forms import ModelForm
from .models import TestSet, Question

class CreatePollForm(ModelForm):
    class Meta:
        model = TestSet
        fields = ['title']

class AnswerPollForm(ModelForm):
    class Meta:
        model = Question
        fields = ['title']