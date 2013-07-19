# Create your views here.
from qset.models import QuestionForm, Question, SetForm, Subject, Set, Set_questions, user_q_status, SubjectForm, SubTopicForm, SubTopic
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseRedirect
from django.utils import simplejson
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.core.exceptions import ObjectDoesNotExist
from django.utils.html import escape
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.template import RequestContext
from django.db.models import Q
from usermanage.models import Group
from django.contrib import messages


@login_required
def filterQuestions(request, group_id=None):
    if group_id:
        group = get_object_or_404(Group, uid=group_id)
        if request.user == group.creator or request.user in group.admins():
            return render_to_response('qset/question_list.html', {"subjects": Subject.objects.all(), "users": group.all_users(), "group": group, "path": "/ajax/" + group.uid + "/getq/"}, context_instance=RequestContext(request))
        else:
            return redirect('usermanage.views.viewGroup', group_id=group_id)
    else:
        # find a way to differentiate between the group question view and my questions view
        return render_to_response('qset/question_list.html', {"subjects": Subject.objects.all(), "groups": request.user.group_set.all(), "path": "/ajax/getq/"}, context_instance=RequestContext(request))


@login_required
def addQuestion(request, group_id=None):
    action = "/question/add/"
    group = None
    if group_id:
        group = get_object_or_404(Group, pk=group_id)
        action += "%s/" % group.pk
    if(request.method == "POST"):
        if group:
            form = QuestionForm(user=request.user, data=request.POST, s_group=group)
        else:
            form = QuestionForm(user=request.user, data=request.POST)
        if form.is_valid():
            q = form.save(commit=False)
            q.creator = request.user
            q.save()
            if(not request.session.get("written_questions", False)):
                request.session['written_questions'] = 0
            request.session['written_questions'] = int(request.session['written_questions']) + 1
            request.session['last_group'] = q.group.id if q.group is not None else None
            request.session['last_subject'] = q.subject.id
            if group:
                return redirect("qset.views.addQuestion", group_id=group.pk)
            else:
                return redirect("qset.views.addQuestion")
    else:
        form = QuestionForm(user=request.user, s_group=group if group else None, s_subject=request.session.get("last_subject", None))
    return render_to_response('qset/addquestion.html', {"form": form, "tot_written": request.session.get("written_questions", 0), "q_count": user_q_status(request.user), "action": action, "title": "Add Question", "success": request.GET.get("success", "false")})


@login_required
def addQuestionToGroup(request):
    if request.is_ajax and request.method == "POST":
        group = get_object_or_404(Group, uid=request.POST.get("g", 0))
        questions = simplejson.loads(request.POST.get("q", []))
        errors = []
        if request.user not in group.all_users():
            return HttpResponse(simplejson.dumps({"success": False, "error_code": 2}), mimetype='application/json')
        for q in questions:
            question = get_object_or_404(Question, uid=q)
            if question.is_used == 0 and request.user == question.creator:
                question.group = group
                question.save()
                errors.append({
                    "q": question.uid,
                    "error": None
                })
            elif question.is_used != 0:
                # Todo: require user to copy question
                errors.append({
                    "q": question.uid,
                    "error": 3
                })
        return HttpResponse(simplejson.dumps({"success": True, "error_code": 0, "errors": errors}), mimetype='application/json')
    # if request.is_ajax:
    #     question = get_object_or_404(Question, uid=request.GET.get("q", 0))
    #     group = get_object_or_404(Group, uid=request.GET.get("g", 0))
    #     if question.is_used == 0 and request.user == question.creator and request.user in group.all_users():
    #         question.group = group
    #         question.save()
    #         return HttpResponse(simplejson.dumps({"success": True, "error_code": 0}), mimetype='application/json')
    #     elif question.is_used != 0:
    #         return HttpResponse(simplejson.dumps({"success": False, "error_code": 3}), mimetype='application/json')
    #     return HttpResponse(simplejson.dumps({"success": False, "error_code": 2}), mimetype='application/json')
    # Error Codes:
    # 0: No error
    # 1: Not ajax
    # 2: Insufficient privileges
    # 3: Question used, need to copy question
    return HttpResponse(simplejson.dumps({"success": False, "error_code": 1}), mimetype='application/json')


@login_required
def removeQuestion(request, q_id):
    try:
        question = Question.objects.get(uid=q_id)
    except ObjectDoesNotExist:
        return HttpResponse(simplejson.dumps({"success": False}))
    if question.creator == request.user and question.is_used == 0:
        question.delete()
        messages.info(request, "Question Deleted")
        return HttpResponse(simplejson.dumps({"success": True, "q_id": q_id}), mimetype='application/json')
    elif question.is_used != 0:
        # Prevent normal users from deleting
        return HttpResponseForbidden("Question already in set")
    else:
        return HttpResponseForbidden("Access Denied")


@login_required
def editQuestion(request, q_id):
    question = get_object_or_404(Question, uid=q_id)
    action = question.get_edit_url()
    if(question.is_used == 0 and (request.user == question.creator)) or (request.GET.get("f", False) == "1" and request.user == question.creator):
        if request.method == "POST":
            form = QuestionForm(user=request.user, data=request.POST, instance=question)
            if form.is_valid():
                form.save()
                messages.info(request, "Question saved.")
                return redirect("/close/")
        else:
            form = QuestionForm(user=request.user, instance=question)
        return render_to_response('qset/addquestion.html', {"form": form, "q_count": user_q_status(request.user), "action": action, "question": question, "ans": question.answer.strip().lower(), "type": "question", "title": "Edit question", "success": "false"})
    elif question.is_used != 0:
        message = "Sorry, this question is being used in a set. You may not edit it."
        if request.user == question.creator:
            message = "This set is already in a set, are you sure you want to edit it? <a href='/question/edit/" + question.uid + "/?f=1'>Continue</a>"
        return render_to_response('qset/question_view.html', {"question": question, "msg": message})
    else:
        # Is the user is not the creator of the question (or staff)
        return HttpResponseRedirect('/')


@login_required
def getSubtopics(request):
    if request.GET.get("subject", False) and request.GET.get("group", False):
        subtopics = SubTopic.objects.filter(
            parent_subject=Subject.objects.get(pk=request.GET.get("subject")),
            group=Group.objects.get(pk=request.GET.get("group"))
        )
        data = []
        for s in subtopics:
            data.append({
                "id": s.id,
                "subtopic": s.name,
            })
        return HttpResponse(simplejson.dumps({"success": True, "choices": data}), content_type="application/json")
    return HttpResponse(simplejson.dumps({"success": False}), content_type="application/json")


@login_required
def addSubject(request):
    if request.method == "POST":
        form = SubjectForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            messages.info(request, "Subject Saved")
            return redirect("/")
    else:
        form = SubjectForm(user=request.user)
    return render_to_response("form_base.html", {"form": form}, context_instance=RequestContext(request))


@login_required
def addSubTopic(request, group_id):
    group = get_object_or_404(Group, uid=group_id)
    if request.user not in group.admins() and request.user != group.creator:
        messages.info(request, "Access denied")
        return redirect("/")
    if request.method == "POST":
        form = SubTopicForm(group=group, data=request.POST)
        if form.is_valid():
            form.save()
            messages.info(request, "Subtopic Saved")
            return redirect("/")
    else:
        form = SubTopicForm(group=group)
    return render_to_response("form_base.html", {"form": form}, context_instance=RequestContext(request))


@login_required
def addSet(request):
    if(request.method == "POST"):
        data = simplejson.loads(request.POST['form_data'])
        if data['group'] != "":
            new_set = Set(name=data['name'], description=data['description'], creator=request.user, group=Group.objects.get(uid=data['group']))
        else:
            new_set = Set(name=data['name'], description=data['description'], creator=request.user)
        new_set.save()
        for s in data['subjects'].split(','):
            new_set.subjects.add(Subject.objects.get(pk=s))
        questions = simplejson.loads(request.POST['questions'])
        for q in questions:
            question = Question.objects.get(uid=q['id'])
            s = Set_questions(set=new_set, question=question, q_num=q["q_num"], q_type=q['type'])
            s.save()
            question.is_used = 1
            question.save()
        return redirect("qset.views.viewSet", set_id=new_set.uid)
    else:
        form = SetForm(user=request.user)
    return render_to_response('qset/set_creation.html', {"form": form}, context_instance=RequestContext(request))


@login_required
def listSets(request):
    sets = Set.objects.filter(creator=request.user).order_by('-creation_date')
    return render_to_response('qset/set_list.html', {"sets": sets}, context_instance=RequestContext(request))


@login_required
def viewSet(request, set_id):
    qlist = []
    curr_set = get_object_or_404(Set, uid=set_id)
    for sq in Set_questions.objects.filter(set=curr_set).order_by("q_num"):
        q = sq.question
        curr = {
            "subtype": escape(q.get_type_display()),
            "subtypenum": q.type,
            "type": sq.get_q_type_display(),
            "num": sq.q_num,
            "subject": q.subject.name,
            "text": escape(q.text),
            "answer": escape(q.ans()),
            "id": q.uid,
        }
        if q.type == 0:
            curr["w"] = escape(q.choice_w)
            curr["x"] = escape(q.choice_x)
            curr["y"] = escape(q.choice_y)
            curr["z"] = escape(q.choice_z)
        qlist.append(curr)
    return render_to_response('qset/set_view.html', {"questions": qlist, "set": curr_set}, context_instance=RequestContext(request))


def setToPDF(request, set_id):
    curr_set = get_object_or_404(Set, uid=set_id)

    set_data = {
        "name": curr_set.name,
        "group": curr_set.creator.get_full_name(),
        "creation_date": curr_set.creation_date.isoformat(),
        "questions": []
    }

    for sq in Set_questions.objects.filter(set=curr_set).order_by("q_num"):
        q = sq.question
        set_data['questions'].append({
            "text": q.text,
            "q_num": sq.q_num.__str__(),
            "type": sq.get_q_type_display(),
            "sub_type_num": q.type,
            "sub_type": q.get_type_display(),
            "subject": q.subject.name,
            "choice_w": q.choice_w,
            "choice_x": q.choice_x,
            "choice_y": q.choice_y,
            "choice_z": q.choice_z,
            "ans": q.ans(),
        })
    import urllib
    params = urllib.urlencode({"set": set_data})
    f = urllib.urlopen("http://ancient-reef-6651.herokuapp.com/pdf/", params)
    return HttpResponse(f, content_type="application/pdf")


@login_required
def editSet(request, set_id):
    curr_set = get_object_or_404(Set, uid=set_id)
    if request.method == "POST":
        data = simplejson.loads(request.POST['form_data'])
        curr_set.name = data['name']
        curr_set.description = data['description']
        curr_set.save()
        for s in data['subjects'].split(','):
            curr_set.subjects.add(Subject.objects.get(pk=s))
        # Set original question to unused
        for q in curr_set.questions.all():
            q.is_used = 0
            q.save()
        curr_set.questions.clear()
        # Add questions from the form
        questions = simplejson.loads(request.POST['questions'])
        for q in questions:
            question = Question.objects.get(uid=q['id'])
            s = Set_questions(set=curr_set, question=question, q_num=q["q_num"], q_type=q['type'])
            s.save()
            question.is_used = 1
            question.save()
        return HttpResponseRedirect("/set/" + str(curr_set.uid) + "/")
    else:
        form = SetForm(user=request.user, instance=curr_set)
        questions = sorted(curr_set.questions.all(), key=lambda q: q.set_questions_set.all()[0].q_num)
        qlist = []
        for q in questions:
            curr = {
                "type": escape(q.type),
                "subject": q.subject.name,
                "date": q.creation_date.date().__str__(),
                "text": escape(q.text),
                "answer": escape(q.ans()),
                "id": q.uid,
                "user": q.creator.get_full_name(),
                "used": q.is_used,
            }
            if q.type == 0:
                curr["w"] = escape(q.choice_w)
                curr["x"] = escape(q.choice_x)
                curr["y"] = escape(q.choice_y)
                curr["z"] = escape(q.choice_z)
            qlist.append(curr)
        qlist = simplejson.dumps(qlist)
        return render_to_response('qset/set_creation.html', {"form": form, "set": curr_set, "set_questions": qlist}, context_instance=RequestContext(request))


@login_required
def getQuestions(request, group_id=None):
    qlist = []
    # Parse GET Parameters
    kwargs = {
        "creator": request.user,
    }
    s_query = Q()
    u_query = Q()
    g_query = Q()

    if group_id:
        group = get_object_or_404(Group, uid=group_id)
    if request.GET.get('uid', False):
        kwargs['uid'] = request.GET.get('uid')

    # Generates query object for subjects
    if request.GET.get('subject', False) and request.GET.get('subject') != "":
        subjects = request.GET.get('subject').split(',')
        for s in subjects:
            s_query = s_query | Q(subject=Subject.objects.get(pk=s))

    if request.GET.get('type', False) and request.GET.get('type') != "":
        kwargs['type'] = request.GET.get('type')

    # Generates query object for groups
    if request.GET.get('group', False) and request.GET.get('group') != "":
        groups = request.GET.get('group').split(',')
        for g in groups:
            g_obj = Group.objects.get(uid=g)
            if request.user in g_obj.all_users():
                g_query = g_query | Q(group=g_obj)
    if request.GET.get('used', False) and request.GET.get('used') != "1":
        kwargs['is_used'] = request.GET.get('used')

    # Allows staff to access other user's questions (not allowed for regular users)
    if group_id and (request.user in group.admins() or request.user == group.creator) and request.GET.get('creator', False) and request.GET.get('creator') != "":
        del kwargs['creator']
        kwargs['group'] = group
        users = request.GET.get('creator').split(',')
        for u in users:
            u_query = u_query | Q(creator=User.objects.get(pk=u))
        # kwargs['creator'] = User.objects.get(pk=request.GET['creator'])
    elif group_id and (request.user in group.admins() or request.user == group.creator):
        del kwargs['creator']
        kwargs['group'] = group

    if request.GET.get("random", False):
        querydict = Question.objects.filter(s_query, **kwargs).order_by("?")
    else:
        if request.GET.get('order', False) and request.GET.get('order') != "":
            querydict = Question.objects.filter(g_query, u_query, s_query, **kwargs).order_by(request.GET.get('order'))
        else:
            querydict = Question.objects.filter(g_query, u_query, s_query, **kwargs).order_by("-creation_date")

    if request.POST.get("questions", False):
        exclude = simplejson.loads(request.POST.get("questions"))
        querydict = querydict.exclude(uid__in=exclude)
        if querydict.count() == 0:
            return HttpResponse(simplejson.dumps({"success": False, "msg": "No questions remain"}), mimetype='application/json')

    if request.GET.get("num", False):
        querydict = querydict[:request.GET.get('num')]

    # Add questions to json object
    for q in querydict:
        curr = {
            "type": escape(q.type),
            "subject": q.subject.__unicode__(),
            "subject-id": q.subject.id,
            "group": q.group.name if q.group else None,
            "group-id": q.group.uid if q.group else None,
            "date": q.creation_date.date().__str__(),
            "text": escape(q.text),
            "answer": escape(q.ans()),
            "id": q.uid,
            "user": q.creator.get_full_name(),
            "user-short": q.creator.first_name[0] + q.creator.last_name[:6] + ("..." if len(q.creator.last_name) > 6 else ""),
            "user-id": q.creator.id,
            "used": q.is_used,
        }
        if q.type == 0:
            curr["w"] = escape(q.choice_w)
            curr["x"] = escape(q.choice_x)
            curr["y"] = escape(q.choice_y)
            curr["z"] = escape(q.choice_z)
        qlist.append(curr)
    return HttpResponse(simplejson.dumps(qlist), mimetype='application/json')
