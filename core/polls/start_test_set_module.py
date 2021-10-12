from django.urls import Resolver404

from .models import TestSet, Question, PassedTestSet, Choice, Answer
from django.http import HttpResponseRedirect, HttpResponseNotFound
from django.shortcuts import render


class StartTestSet:
    def __init__(self, request, test_set_id, question_index=None):
        self.request = request
        self.user = request.user
        self.test_set_id = test_set_id
        self.question_index = question_index if question_index and question_index > '0' else '0'
        self.questions_id = None
        self.test_set = None
        self.questions = None
        self.result = None

    def get_test_set(self):
        try:
            self.test_set = TestSet.objects.filter(pk=self.test_set_id)[0]
        except IndexError:
            self.result = HttpResponseNotFound('<h1>Test Set not found</h1>')
            raise TestSetError('Test Set not found')

    def prepare(self):
        self.questions = Question.objects.filter(test_set=self.test_set).all()
        last_test_set_answer = PassedTestSet.objects.filter(user=self.user, testset=self.test_set).all()
        if last_test_set_answer:
            self.result = HttpResponseNotFound('<h1>Test Set has answer</h1>')
            raise TestSetError('Test Set has answer')

    def has_answer(self, question_id):
        question = Question.objects.get(pk=question_id)
        has_answer = False
        for choice in self.request.POST.keys():
            if 'choice' in choice:
                has_answer = True
                choice_id = int(self.request.POST[choice].split('_')[-1])
                curr_choice = Choice.objects.get(pk=choice_id)
                new_answer = Answer.objects.create(user=self.user,
                                                   test_set=self.test_set,
                                                   question=question,
                                                   choice=curr_choice)
                new_answer.save()

        if not has_answer:
            if self.question_index:
                self.result = HttpResponseRedirect(f'/start_test_set/{self.test_set_id}/{self.question_index}')
                raise RedirectError
            else:
                self.result = HttpResponseRedirect(f'/start_test_set/{self.test_set_id}')
                raise RedirectError

    def http_post(self):

        question_id = self.request.POST['question_id']
        self.has_answer(question_id)

        if len(self.questions) > 1:
            next_question_index = sorted([question.pk for question in self.questions]).index(int(question_id)) + 1
            if next_question_index < len(self.questions):
                return HttpResponseRedirect(f'/start_test_set/{self.test_set_id}/{next_question_index}')
            else:
                new_passed_test_set = PassedTestSet.objects.create(user=self.user,
                                                                   testset=self.test_set
                                                                   )
                new_passed_test_set.save()
                return HttpResponseRedirect(f'/results/{self.test_set_id}')
        else:
            new_passed_test_set = PassedTestSet.objects.create(user=self.user,
                                                               testset=self.test_set
                                                               )
            new_passed_test_set.save()
            return HttpResponseRedirect(f'/results/{self.test_set_id}')

    def check_question(self):
        if not int(self.question_index) in range(len(self.questions_id)):
            self.result = HttpResponseNotFound('<h1>Question not found</h1>')
            raise QuestionError
        qq_pk = self.questions_id[int(self.question_index)]
        this_question = Question.objects.get(pk=qq_pk)
        answers_this_user = Answer.objects.filter(user=self.user, question=this_question,
                                                  test_set=self.test_set).all()
        if answers_this_user:
            self.result = HttpResponseRedirect(f'/start_test_set/{self.test_set_id}/{int(self.question_index) + 1}')
            raise QuestionError

    def http_get(self):
        self.questions_id = sorted([question.pk for question in self.questions])
        if self.question_index and self.question_index != '0':

            self.check_question()

            late_question = Question.objects.get(pk=self.questions_id[int(self.question_index) - 1])
            answers_late_question = Answer.objects.filter(user=self.user, question=late_question,
                                                          test_set=self.test_set).all()
            if answers_late_question:
                next_question = Question.objects.get(pk=self.questions_id[int(self.question_index)])
                context = {
                    'poll': next_question,
                    'choices': Choice.objects.filter(question=next_question).all(),
                    'user': self.user
                }

                return render(self.request, 'polls/vote.html', context)
            else:
                return HttpResponseRedirect(f'/start_test_set/{self.test_set_id}/{int(self.question_index) - 1}')


        else:

            last_question_id = None
            for q_id in self.questions_id:
                if Answer.objects.filter(user=self.user,
                                         test_set=self.test_set,
                                         question=q_id):
                    continue
                else:
                    last_question_id = q_id
                    break
            if last_question_id is not None:
                first_question = Question.objects.get(pk=last_question_id)
            else:
                new_passed_test_set = PassedTestSet.objects.create(user=self.user,
                                                                   testset=self.test_set
                                                                   )
                new_passed_test_set.save()
                return HttpResponseRedirect(f'/results/{self.test_set_id}')
            context = {
                'poll': first_question,
                'choices': Choice.objects.filter(question=first_question).all(),
                'user': self.user
            }

            return render(self.request, 'polls/vote.html', context)

    def get(self):
        try:
            self.get_test_set()
            self.prepare()

            if self.request.method == 'POST':
                return self.http_post()
            else:
                return self.http_get()
        except (TestSetError, RedirectError, QuestionError):
            return self.result
        except Exception as e:
            print(e)
            return Resolver404("Error 404")


class TestSetError(Exception):
    pass


class RedirectError(Exception):
    pass


class QuestionError(Exception):
    pass
