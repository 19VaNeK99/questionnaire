from .serializers import QuestionSerializer
from .models import Question, TestSet, Answer, Choice
from rest_framework import viewsets
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotFound
from django.shortcuts import render, get_object_or_404, redirect
# from .forms import AnswerFormSet
from .forms import CreateTestSetForm, CreateQuestionForm, CreateChoiceForm, UserRegistrationForm
from django.views.generic import View
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


def create_test_set(request):
    if request.method == 'POST':
        form = CreateTestSetForm(request.POST)

        if form.is_valid():
            form.save()

            return redirect('home')
    else:
        form = CreateTestSetForm()

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




# class CreateQuestion(View):
#     def get(self, request):
#         form = CreateQuestionForm()
#         form_choice = CreateChoiceForm()
#         context = {
#             'form': form,
#             'form_choice': form_choice
#         }
#         return render(self.request, 'polls/create_question.html', context)
#
#     def post(self, request):
#         form = CreateQuestionForm(request.POST)
#         form_choice = CreateChoiceForm(request.POST)
#         if form.is_valid() and form_choice.is_valid():
#             current_test_set = TestSet.objects.get(pk=test_set_id)
#             new_question = Question.objects.create(title=request.POST['title'][0])
#             new_question.test_set.add(current_test_set)
#             new_question.save()
#             return redirect('test_set', test_set_id=test_set_id, permanent=False)

def create_question(request, test_set_id):
    if request.method == 'POST':

        form = CreateQuestionForm(request.POST)
        #form_choice = CreateChoiceForm(request.POST)
        if form.is_valid():
            current_test_set = TestSet.objects.get(pk=test_set_id)
            new_question = Question.objects.create(title=request.POST['title'])
            new_question.test_set.add(current_test_set)
            new_question.save()
            choices = []
            for i in request.POST:
                if "choice" in i:
                    l = [j for j in request.POST]
                    is_r = f"is_right{request.POST[i][-1]}"
                    choices.append({
                        'choice': request.POST[i],
                        'question': new_question,
                        'is_right': True if is_r in l else False

                    })

            for item in choices:
                new_choice = Choice.objects.create(**item)
                new_choice.save()

            return HttpResponseRedirect(f'/test_set/{test_set_id}')
    else:
        form = CreateQuestionForm()
        form_choice = CreateChoiceForm()
        context = {
            'form': form,
            'form_choice': form_choice
        }
        return render(request, 'polls/create_question.html', context)



def start_test_set(request, test_set_id, question_index=None):
    if request.method == 'POST':
        pass
    else:
        if question_index:
            current_test_set = TestSet.objects.get(pk=test_set_id)
            questions = current_test_set.question.all()
            questions_id = [question.pk for question in questions].sort()
            if not question_index in questions_id:
                return HttpResponseNotFound('<h1>Question not found</h1>')
            user = request.user.get_profile()
            this_question = Question.objects.get(pk=question_index)
            answers_this_user = Answer.objects.filter(user=user, question=this_question, test_set=current_test_set).all()
            if answers_this_user:
                return HttpResponseNotFound('<h1>Question has answer</h1>')
            if question_index in range(questions_id):
                if question_index != 0:
                    late_question = Question.objects.get(pk=questions_id[question_index - 1])
                    answers_late_question = Answer.objects.filter(user=user, question=late_question,
                                                              test_set=current_test_set).all()
                    if answers_late_question:
                        next_question = Question.objects.get(pk=question_index)
                        context = {
                            'poll': next_question,
                            'answers': Choice.objects.filter(question=next_question).all()
                        }

                        return render(request, 'polls/vote.html', context)

        else:
            current_test_set = TestSet.objects.get(pk=test_set_id)
            questions = current_test_set.question.all()
            questions_id = [question.pk for question in questions].sort()
            first_question = Question.objects.get(pk=questions_id[0])
            context = {
                'poll': first_question,
                'answers': Choice.objects.filter(question=first_question).all()
            }

            return render(request, 'polls/vote.html', context)




def register(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        if user_form.is_valid():
            # Create a new user object but avoid saving it yet
            new_user = user_form.save(commit=False)
            # Set the chosen password
            new_user.set_password(user_form.cleaned_data['password'])
            # Save the User object
            new_user.save()
            return render(request, 'registration/register_done.html', {'new_user': new_user})
    else:
        user_form = UserRegistrationForm()
    return render(request, 'registration/register.html', {'user_form': user_form})
