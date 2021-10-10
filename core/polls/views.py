from .start_test_set_module import StartTestSet
from .models import Question, TestSet, Answer, Choice, PassedTestSet
from django.http import HttpResponseRedirect, HttpResponseNotFound
from django.shortcuts import render, redirect
from .forms import CreateTestSetForm, CreateQuestionForm, UserRegistrationForm


def is_anonymous(view_func):
    def decorator(request, *args, **kwargs):
        if request.user.is_anonymous:
            return HttpResponseRedirect(f'/accounts/login')
        return view_func(request, *args, **kwargs)

    return decorator


@is_anonymous
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


@is_anonymous
def list_questions(request, test_set_id):
    try:
        test_set = TestSet.objects.filter(pk=test_set_id)[0]
    except IndexError:
        return HttpResponseNotFound('<h1>Test Set not found</h1>')

    questions = Question.objects.filter(test_set=test_set).all()
    user = request.user
    if not user.is_superuser:
        return HttpResponseNotFound('<h1>Url not found</h1>')

    context = {
        'test_set_id': test_set_id,
        'questions': questions,
        'user': request.user
    }
    return render(request, 'polls/questions.html', context)


@is_anonymous
def delete_question(request, test_set_id, question_id):
    user = request.user
    if user.is_superuser:
        Question.objects.filter(pk=question_id).delete()
        return HttpResponseRedirect(f'/list_questions/{test_set_id}')
    else:
        return HttpResponseNotFound('<h1>Url not found</h1>')


@is_anonymous
def delete_test_set(request, test_set_id):
    user = request.user
    if user.is_superuser:
        TestSet.objects.filter(pk=test_set_id).delete()
        return HttpResponseRedirect(f'/home')
    else:
        return HttpResponseNotFound('<h1>Url not found</h1>')


@is_anonymous
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


@is_anonymous
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


@is_anonymous
def create_question(request, test_set_id, text=''):
    if not request.user.is_superuser:
        return HttpResponseNotFound('<h1>Url not found</h1>')
    if request.method == 'POST':

        if form_create_question_is_valid(request):
            try:
                current_test_set = TestSet.objects.filter(pk=test_set_id)[0]
            except IndexError:
                return HttpResponseNotFound('<h1>Test Set not found</h1>')

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


@is_anonymous
def start_test_set(request, test_set_id, question_index=None):
    return StartTestSet(request, test_set_id, question_index).get()



def register(request):
    user = request.user
    if request.method == 'POST':
        if not user.is_anonymous:
            return HttpResponseRedirect(f'/home')
        user_form = UserRegistrationForm(request.POST)
        if user_form.is_valid():
            new_user = user_form.save(commit=False)
            new_user.set_password(user_form.cleaned_data['password'])
            new_user.save()
            return render(request, 'registration/register_done.html', {'new_user': new_user})
    else:
        if not user.is_anonymous:
            return HttpResponseRedirect(f'/home')
        user_form = UserRegistrationForm()
        return render(request, 'registration/register.html', {'user_form': user_form})


def solve_total_result(total_result):
    total = 0
    for result in total_result:
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
        total = (total / len(total_result)) * 100
    return total


@is_anonymous
def results(request, test_set_id):
    try:
        curr_test_set = TestSet.objects.filter(pk=test_set_id)[0]
    except IndexError:
        return HttpResponseNotFound('<h1>Test Set not found</h1>')
    curr_passed_test_set = PassedTestSet.objects.filter(user=request.user,
                                                        testset=curr_test_set)
    if not curr_passed_test_set:
        return HttpResponseNotFound('<h1>This test set is not pass</h1>')

    curr_user = request.user
    test_sets_questions = Question.objects.filter(test_set=curr_test_set)
    result = []
    for test_sets_question in test_sets_questions:
        item = dict()
        item['question_title'] = test_sets_question.title
        choices_question = Choice.objects.filter(question=test_sets_question).all()
        choices = []
        for choice in choices_question:
            choice_item = dict()
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
        'user': curr_user,
        'total': total
    }
    return render(request, 'polls/results.html', context)
