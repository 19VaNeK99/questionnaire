from django.forms import ModelForm
from .models import TestSet, Question, Choice


class CreateTestSetForm(ModelForm):
    class Meta:
        model = TestSet
        fields = ['title']


class CreateQuestionForm(ModelForm):
    class Meta:
        model = Question
        fields = ['title']


class CreateChoiceForm(ModelForm):
    class Meta:
        model = Choice
        fields = ['title', 'is_right']