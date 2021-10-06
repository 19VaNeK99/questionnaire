from django.contrib import admin
from .models import Question, TestSet, Choice, PassedTestSet


admin.site.register(Question)
admin.site.register(TestSet)
admin.site.register(Choice)
admin.site.register(PassedTestSet)

