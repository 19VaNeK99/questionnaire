from django.conf import settings
from django.db import models


class TestSet(models.Model):
    title = models.CharField(max_length=200)
    visible = models.BooleanField(default=False)
    questions = models.ManyToManyField('Question', blank=True)

    def __str__(self):
        return self.title


class Question(models.Model):
    title = models.CharField(max_length=4096)
    test_set = models.ManyToManyField('TestSet', through=TestSet.questions.through, blank=True)
    # testset = models.ManyToManyField(TestSet)

    def __str__(self):
        return self.title


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.DO_NOTHING)
    choice = models.CharField(max_length=4096)
    is_right = models.BooleanField(default=False)

    def __str__(self):
        return self.choice


class PassedTestSet(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING)
    testset = models.ForeignKey(TestSet, on_delete=models.DO_NOTHING)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.testset.title


class Answer(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING)
    question = models.ForeignKey(PassedTestSet, on_delete=models.DO_NOTHING)
    answer = models.ForeignKey(Choice, on_delete=models.DO_NOTHING)
