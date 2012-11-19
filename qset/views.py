# Create your views here.
from qset.models import QuestionForm
from qset.models import Question
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.utils import simplejson
from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required


@login_required
def viewQuestions(request):
    return render_to_response('qset/questionlist.html', {"questions": Question.objects.filter(creator=request.user)})


@login_required
def addQuestion(request):
    action = "/question/add/"
    if(request.method == "POST"):
        form = QuestionForm(data=request.POST)
        if form.is_valid():
            q = form.save(commit=False)
            q.creator = request.user
            q.save()
            return HttpResponseRedirect('/')
    else:
        form = QuestionForm()
    return render_to_response('qset/addquestion.html', {"form": form, "action": action, "title": "Add Question"})


@login_required
def editQuestion(request, q_id):
    action = "/question/edit/" + q_id
    question = get_object_or_404(Question, id=q_id)
    if(request.user == question.creator or request.user.is_staff):
        if request.method == "POST":
            form = QuestionForm(data=request.POST, instance=question)
            if form.is_valid():
                form.save()
                return HttpResponseRedirect('/')
        else:
            form = QuestionForm(instance=question)
        return render_to_response('qset/addquestion.html', {"form": form, "action": action, "type": "question", "title": "Edit question"})
    else:
        # Is the user is not the creator of the question (or staff)
        return HttpResponseRedirect('/')


@login_required
def getQuestions(request):
    if request.method == "GET":
        qlist = []
        # Parse GET Parameters
        kwargs = {
            "creator": request.user,
            "pk": request.GET['id'] or None,
            # "subject": request.GET['subject'] or None,
            # "type": request.GET['type'] or None,
            # "creator": request.GET['creator'] or None,
            # "is_used": request.GET['used'] or None,
        }
        # Allows staff to access other user's questions (not allowed for regular users)
        if request.user.is_staff and request.GET['creator']:
            kwargs['creator'] = request.GET['creator']

        # Add questions to json object
        for q in Question.objects.filter(**kwargs):
            curr = {
                "type": q.type,
                "subject": q.subject.get_name_display(),
                "date": q.creation_date.date().__str__(),
                "text": q.text,
                "answer": q.answer,
            }
            qlist.append(curr)
        return HttpResponse(simplejson.dumps(qlist), mimetype='application/json')
