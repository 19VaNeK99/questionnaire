from django.contrib import admin
from .models import Question, TestSet, Choice, PassedTestSet

@admin.register(TestSet)
class TestSetAdmin(admin.ModelAdmin):
    raw_id_fields = ('questions',)


admin.site.register(Question)
# admin.site.register(TestSet)
admin.site.register(Choice)
admin.site.register(PassedTestSet)

