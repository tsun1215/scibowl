# Create your views here.
from qset.models import QuestionForm, Question, SetForm, Subject, Set, Set_questions
from django.http import HttpResponseRedirect
from django.http import HttpResponse, HttpResponseForbidden
from django.utils import simplejson
from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.utils.html import escape
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.template import RequestContext
from django.db.models import Q


@login_required
def filterQuestions(request):
    return render_to_response('qset/question_list.html', {"subjects": Subject.objects.all(), "users": User.objects.all()}, context_instance=RequestContext(request))


@login_required
def addQuestion(request):
    action = "/question/add/"
    if(request.method == "POST"):
        form = QuestionForm(data=request.POST)
        if form.is_valid():
            q = form.save(commit=False)
            q.creator = request.user
            q.save()
            return HttpResponseRedirect('/question/add/?success=true')
    else:
        form = QuestionForm()
    return render_to_response('qset/addquestion.html', {"form": form, "action": action, "title": "Add Question", "success": request.GET.get("success", "false")})


@login_required
def removeQuestion(request, q_id):
    try:
        question = Question.objects.get(pk=q_id)
    except ObjectDoesNotExist:
        return HttpResponse(simplejson.dumps({"success": False}))
    if question.creator == request.user:
        question.delete()
        return HttpResponse(simplejson.dumps({"success": True, "q_id": q_id}))
    else:
        return HttpResponseForbidden("Access Denied")


@login_required
def editQuestion(request, q_id):
    action = "/question/edit/" + q_id
    question = get_object_or_404(Question, id=q_id)
    if(request.user == question.creator or request.user.is_staff):
        if request.method == "POST":
            form = QuestionForm(data=request.POST, instance=question)
            if form.is_valid():
                form.save()
                return HttpResponseRedirect('/home/')
        else:
            form = QuestionForm(instance=question)
        return render_to_response('qset/addquestion.html', {"form": form, "action": action, "type": "question", "title": "Edit question", "success": "false"})
    else:
        # Is the user is not the creator of the question (or staff)
        return HttpResponseRedirect('/')


@login_required
def addSet(request):
    action = "/set/add/"
    if(request.method == "POST"):
        data = simplejson.loads(request.POST['form_data'])
        new_set = Set(name=data['name'], description=data['description'], creator=request.user)
        new_set.save()
        for s in data['subjects'].split(','):
            new_set.subjects.add(Subject.objects.get(pk=s))
        questions = simplejson.loads(request.POST['questions'])
        for q in questions:
            question = Question.objects.get(pk=q['id'])
            s = Set_questions(set=new_set, question=question, q_num=q["q_num"], q_type=q['type'])
            s.save()
            question.is_used = 1
            question.save()
        return HttpResponseRedirect("/set/" + str(new_set.id) + "/")
    else:
        form = SetForm()
    return render_to_response('qset/set_creation.html', {"form": form, "action": action, "title": "Add Question"}, context_instance=RequestContext(request))


@login_required
def viewSet(request, set_id):
    qlist = []
    for sq in Set_questions.objects.filter(set=Set.objects.get(pk=set_id)).order_by("q_num"):
        q = sq.question
        curr = {
            "subtype": escape(q.get_type_display()),
            "subtypenum": q.type,
            "type": Set_questions.objects.get(set=set_id, question=q).get_q_type_display(),
            "num": Set_questions.objects.get(set=set_id, question=q).q_num,
            "subject": q.subject.get_name_display(),
            "text": escape(q.text),
            "answer": escape(q.ans()),
            "id": q.id,
        }
        if q.type == 0:
            curr["w"] = escape(q.choice_w)
            curr["x"] = escape(q.choice_x)
            curr["y"] = escape(q.choice_y)
            curr["z"] = escape(q.choice_z)
        qlist.append(curr)
    return render_to_response('qset/set_view.html', {"questions": qlist}, context_instance=RequestContext(request))


@login_required
def getQuestions(request):
    if request.method == "GET":
        qlist = []
        # Parse GET Parameters
        kwargs = {
            "creator": request.user,
        }
        s_query = Q()
        if request.GET.get('id', False):
            kwargs['pk'] = request.GET.get('id')
        if request.GET.get('subject', False) and request.GET.get('subject') != "":
            subjects = request.GET.get('subject').split(',')
            for s in subjects:
                s_query = s_query | Q(subject=Subject.objects.get(pk=s))
            # kwargs['subject'] = Subject.objects.filter(name=request.GET.get('subject'))
        if request.GET.get('type', False) and request.GET.get('type') != "":
            kwargs['type'] = request.GET.get('type')
        if request.GET.get('used', False):
            kwargs['is_used'] = request.GET.get('used')

        # Allows staff to access other user's questions (not allowed for regular users)
        if request.user.is_staff and request.GET.get('creator', False) and request.GET.get('creator') != "":
            kwargs['creator'] = User.objects.get(pk=request.GET['creator'])
        elif request.user.is_staff and request.GET.get('all', False):
            del kwargs['creator']

        if request.GET.get("random", False):
            querydict = Question.objects.filter(s_query, **kwargs).order_by("?")
        else:
            if request.GET.get('order', False) and request.GET.get('order') != "":
                querydict = Question.objects.filter(s_query, **kwargs).order_by(request.GET.get('order'))
            else:
                querydict = Question.objects.filter(s_query, **kwargs).order_by("-creation_date")

        if request.GET.get("num", False):
            querydict = querydict[:request.GET.get('num')]

        # Add questions to json object
        for q in querydict:
            curr = {
                "type": escape(q.type),
                "subject": q.subject.get_name_display(),
                "date": q.creation_date.date().__str__(),
                "text": escape(q.text),
                "answer": escape(q.ans()),
                "id": q.id,
                "user": q.creator.get_full_name(),
                "used": q.is_used,
            }
            if q.type == 0:
                curr["w"] = escape(q.choice_w)
                curr["x"] = escape(q.choice_x)
                curr["y"] = escape(q.choice_y)
                curr["z"] = escape(q.choice_z)
            qlist.append(curr)
        return HttpResponse(simplejson.dumps(qlist), mimetype='application/json')


# Get random questions method, takes
