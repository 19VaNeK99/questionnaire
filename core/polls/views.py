from .serializers import QuestionSerializer
from .models import Question, TestSet, Answer, Choice, PassedTestSet
from rest_framework import viewsets
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotFound, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
# from .forms import AnswerFormSet
from .forms import CreateTestSetForm, CreateQuestionForm, CreateChoiceForm, UserRegistrationForm
from django.views.generic import View


class GetQuestion(viewsets.ModelViewSet):
    serializer_class = QuestionSerializer
    queryset = Question.objects.all()


def home(request):
    test_sets = list(TestSet.objects.all())
    user = request.user
    if not user.is_superuser:
        i = 0
        while i < len(test_sets):
            test_set_s_questions = Question.objects.filter(test_set=test_sets[i])
            passed_test_set = PassedTestSet.objects.filter(user=user,
                                                           testset=test_sets[i])
            if not test_set_s_questions or passed_test_set:
                del test_sets[i]
                i -= 1
            i += 1

    context = {
        'testsets': test_sets,
        'user': request.user
    }
    return render(request, 'polls/home.html', context)


def delete_test_set(request, test_set_id):
    user = request.user
    if user.is_superuser:
        TestSet.objects.filter(pk=test_set_id).delete()
        return HttpResponseRedirect(f'/home')
    else:
        return HttpResponseNotFound('<h1>Url not found</h1>')


def create_test_set(request):
    if request.method == 'POST':
        form = CreateTestSetForm(request.POST)

        if form.is_valid():
            form.save()

            return redirect('home')
    else:
        form = CreateTestSetForm()

    context = {
        'form': form,
        'user': request.user
    }
    return render(request, 'polls/create.html', context)


# def vote(request, question_id):
#     poll = Question.objects.get(pk=question_id)
#     if request.method == 'POST':
#
#         selected_option = request.POST['poll']
#         print(selected_option)
#         current_answer = Answer
#         return HttpResponse(400, 'Invalid form option')
#
#
#         poll.save()
#
#         return redirect('results', poll.id)
#
#     else:
#         form = AnswerPollForm()
#
#     context = {
#         'poll': poll,
#         'answers': Choice.objects.filter(question=poll).all()
#     }
#     # context = {
#     #     'form': form
#     # }
#     return render(request, 'polls/vote.html', context)


def test_set(request, test_set_id):

    current_test_set = TestSet.objects.get(pk=test_set_id)
    this_questions = Question.objects.filter(test_set=current_test_set).all()

    user = request.user
    if not this_questions and not user.is_superuser:
        return HttpResponseNotFound('<h1>Test Set not found</h1>')

    context = {
        'test_set': current_test_set,
        'questions': this_questions,
        'user': request.user
    }

    return render(request, 'polls/test_set.html', context)


def form_create_question_is_valid(request):
    has_is_right = False
    has_choice = False
    for i in request.POST.keys():
        if 'choice' in i:
            if request.POST[i] != '':
                has_choice = True
        if 'is_right' in i:
            has_is_right = True

    if has_choice and has_is_right:
        return True
    else:
        return False


def create_question(request, test_set_id, text=''):

    if request.method == 'POST':
        if form_create_question_is_valid(request):

            current_test_set = TestSet.objects.get(pk=test_set_id)
            new_question = Question.objects.create(title=request.POST['title'],
                                                   test_set=current_test_set)
            new_question.save()

            choices = []
            list_keys = [j for j in request.POST]
            for i in request.POST:
                if "choice" in i:
                    is_r = f"is_right{i[-1]}"
                    choices.append({
                        'choice': request.POST[i],
                        'question': new_question,
                        'is_right': True if is_r in list_keys else False

                    })

            for item in choices:
                new_choice = Choice.objects.create(**item)
                new_choice.save()

            return HttpResponseRedirect(f'/test_set/{test_set_id}')
        else:
            request.method = 'GET'
            return create_question(request, test_set_id, text='Проверьте заполненность полей в форме!')
    else:

        form = CreateQuestionForm()
        context = {
            'form': form,
            'user': request.user,
            'text': text
        }
        return render(request, 'polls/create_question.html', context)


def start_test_set(request, test_set_id, question_index=None):
    user = request.user
    try:
        current_test_set = TestSet.objects.filter(pk=test_set_id)[0]
    except IndexError:
        return HttpResponseNotFound('<h1>Test Set not found</h1>')
    last_test_set_answer = PassedTestSet.objects.filter(user=user, testset=current_test_set).all()
    if last_test_set_answer:
        return HttpResponseNotFound('<h1>Test Set has answer</h1>')
    if request.method == 'POST':
        user = request.user
        if user.is_anonymous:
            return HttpResponseRedirect(f'/accounts/login')

        test_set = TestSet.objects.get(pk=test_set_id)
        question_id = request.POST['question_id']
        question = Question.objects.get(pk=question_id)
        has_answer = False
        for choice in request.POST.keys():
            if 'choice' in choice:
                has_answer = True
                choice_id = int(request.POST[choice].split('_')[-1])
                curr_choice = Choice.objects.get(pk=choice_id)
                new_answer = Answer.objects.create(user=user,
                                                   test_set=test_set,
                                                   question=question,
                                                   choice=curr_choice)
                new_answer.save()
        if not has_answer:
            if question_index:
                return HttpResponseRedirect(f'/start_test_set/{test_set_id}/{question_index}')
            else:
                return HttpResponseRedirect(f'/start_test_set/{test_set_id}')
        current_test_set = TestSet.objects.get(pk=test_set_id)
        questions = Question.objects.filter(test_set=current_test_set).all()
        if len(questions) > 1:
            qq = [question.pk for question in questions]
            ss = sorted(qq)
            iinn = ss.index(int(question_id))
            next_question_index = iinn + 1
            if next_question_index < len(questions):
                return HttpResponseRedirect(f'/start_test_set/{test_set_id}/{next_question_index}')
            else:
                new_passed_test_set = PassedTestSet.objects.create(user=user,
                                                                   testset=current_test_set
                                                                   )
                new_passed_test_set.save()
                return HttpResponseRedirect(f'/results/{test_set_id}')
        else:
            new_passed_test_set = PassedTestSet.objects.create(user=user,
                                                               testset=current_test_set
                                                               )
            new_passed_test_set.save()
            return HttpResponseRedirect(f'/results/{test_set_id}')

    else:
        if question_index:
            current_test_set = TestSet.objects.get(pk=test_set_id)
            questions = Question.objects.filter(test_set=current_test_set).all()
            questions_id = sorted([question.pk for question in questions])
            if not int(question_index) in range(len(questions_id)):
                return HttpResponseNotFound('<h1>Question not found</h1>')
            user = request.user
            qq_pk = questions_id[int(question_index)]
            this_question = Question.objects.get(pk=qq_pk)
            answers_this_user = Answer.objects.filter(user=user, question=this_question,
                                                      test_set=current_test_set).all()
            if answers_this_user:
                return HttpResponseNotFound('<h1>Question has answer</h1>')

            if question_index != 0:
                late_question = Question.objects.get(pk=questions_id[int(question_index) - 1])
                answers_late_question = Answer.objects.filter(user=user, question=late_question,
                                                              test_set=current_test_set).all()
                if answers_late_question:
                    next_question = Question.objects.get(pk=questions_id[int(question_index)])
                    context = {
                        'poll': next_question,
                        'choices': Choice.objects.filter(question=next_question).all(),
                        'user': request.user
                    }

                    return render(request, 'polls/vote.html', context)

        else:
            current_test_set = TestSet.objects.get(pk=test_set_id)
            questions = Question.objects.filter(test_set=current_test_set).all()
            questions_id = sorted([question.pk for question in questions])
            last_question_id = None
            for q_id in questions_id:
                if Answer.objects.filter(user=user,
                                         test_set=current_test_set,
                                         question=q_id):
                    continue
                else:
                    last_question_id = q_id
                    break
            if last_question_id != None:
                first_question = Question.objects.get(pk=last_question_id)
            else:
                new_passed_test_set = PassedTestSet.objects.create(user=user,
                                                                   testset=current_test_set
                                                                   )
                new_passed_test_set.save()
                return HttpResponseRedirect(f'/results/{test_set_id}')
            context = {
                'poll': first_question,
                'choices': Choice.objects.filter(question=first_question).all(),
                'user': request.user
            }

            return render(request, 'polls/vote.html', context)


def register(request):
    user = request.user
    if request.method == 'POST':
        if not user.is_anonymous:
            return HttpResponseRedirect(f'/home')
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
        if not user.is_anonymous:
            return HttpResponseRedirect(f'/home')
        user_form = UserRegistrationForm()
    return render(request, 'registration/register.html', {'user_form': user_form})


def solve_total_result(results):
    total = 0
    for result in results:
        count_right = 0
        count_answer = 0
        it_is_zero = False
        for choice in result['choices']:
            count_right += int(choice['is_right'])
            if choice['is_right']:
                count_answer += int(choice['user_answer'])
            if not choice['is_right'] and choice['user_answer']:
                it_is_zero = True
        if not it_is_zero:
            total += count_answer / count_right
    if total > 0:
        total = (total / len(results)) * 100
    return total


def results(request, test_set_id):
    curr_test_set = TestSet.objects.get(pk=test_set_id)
    curr_passed_test_set = PassedTestSet.objects.filter(user=request.user,
                                                        testset=curr_test_set)
    if not curr_passed_test_set:
        return HttpResponseNotFound('<h1>This test set is not pass</h1>')

    curr_user = request.user
    test_sets_questions = Question.objects.filter(test_set=curr_test_set)
    answers = Answer.objects.filter(test_set=test_set_id,
                                    user=curr_user).all()
    result = []
    for test_sets_question in test_sets_questions:
        item = {}
        item['question_title'] = test_sets_question.title
        choices_question = Choice.objects.filter(question=test_sets_question).all()
        choices = []
        for choice in choices_question:
            choice_item = {}
            choice_item['title'] = choice.choice
            choice_item['is_right'] = choice.is_right
            user_answer = Answer.objects.filter(
                test_set=test_set_id,
                user=curr_user,
                choice=choice
            ).all()
            choice_item['user_answer'] = bool(user_answer)
            choices.append(choice_item)
        item['choices'] = choices

        result.append(item)

    total = solve_total_result(result)

    context = {
        'results': result,
        'user': request.user,
        'total': total
    }
    return render(request, 'polls/results.html', context)
