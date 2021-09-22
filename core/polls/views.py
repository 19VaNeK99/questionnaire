from .serializers import QuestionSerializer
from .models import Question, TestSet, Answer, Choice
from rest_framework import viewsets
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
# from .forms import AnswerFormSet
from .forms import CreatePollForm, AnswerPollForm

class GetQuestion(viewsets.ModelViewSet):
    serializer_class = QuestionSerializer
    queryset = Question.objects.all()


# def prepare_blank_answers(evaluation):
#     for question in evaluation.scheme.evaluationquestion_set.all():
#         answer = Answer(evaluation=evaluation,
#                                question=question)
#         answer.save()

# def answer_form(request, id):
#     evaluation = get_object_or_404(TestSet, id=id)
#     if len(evaluation.objects.all()) == 0:
#         prepare_blank_answers(evaluation)
#     if request.method == 'POST':
#         formset = AnswerFormSet(request.POST, instance=evaluation)
#         if formset.is_valid():
#             formset.save()
#             return HttpResponse('Thank you!')
#     else:
#         formset = AnswerFormSet(instance=evaluation)
#     return render('answer_form.html',
#             {'formset':formset, 'evaluation':evaluation})


def home(request):
    test_sets = TestSet.objects.all()

    context = {
        'testsets': test_sets
    }
    return render(request, 'polls/home.html', context)


def create(request):
    if request.method == 'POST':
        form = CreatePollForm(request.POST)

        if form.is_valid():
            form.save()

            return redirect('home')
    else:
        form = CreatePollForm()

    context = {'form': form}
    return render(request, 'polls/create.html', context)


def results(request, poll_id):
    poll = Answer.objects.get(pk=poll_id)

    context = {
        'poll': poll
    }
    return render(request, 'polls/results.html', context)


def vote(request, question_id):
    poll = Question.objects.get(pk=question_id)
    if request.method == 'POST':

        selected_option = request.POST['poll']
        print(selected_option)
        current_answer = Answer
        return HttpResponse(400, 'Invalid form option')


        poll.save()

        return redirect('results', poll.id)

    else:
        form = AnswerPollForm()

    context = {
        'poll': poll,
        'answers': Choice.objects.filter(question=poll).all()
    }
    # context = {
    #     'form': form
    # }
    return render(request, 'polls/vote.html', context)


def test_set(request, test_set_id):
    current_test_set = TestSet.objects.get(pk=test_set_id)

    context = {
        'test_set': current_test_set,
        'questions': current_test_set.questions.all()
    }
    # print(current_test_set.questions.all())
    return render(request, 'polls/test_set.html', context)
