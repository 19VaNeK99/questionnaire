from django.conf import settings
from django.db import models


class TestSet(models.Model):
    title = models.CharField(max_length=200)
    visible = models.BooleanField(default=False)

    def __str__(self):
        return self.title


class Question(models.Model):
    title = models.CharField(max_length=4096)
    questions = models.ManyToManyField(TestSet)

    def __str__(self):
        return self.title


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.DO_NOTHING)
    title = models.CharField(max_length=4096)
    is_right = models.BooleanField(default=False)

    def __str__(self):
        return self.title


class PassedTestSet(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING)
    testset = models.ForeignKey(TestSet, on_delete=models.DO_NOTHING)
    result = models.IntegerField()
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.testset.title
