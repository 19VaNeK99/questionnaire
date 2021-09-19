from django.forms import ModelForm
from .models import TestSet

class CreatePollForm(ModelForm):
    class Meta:
        model = TestSet
        fields = ['title']