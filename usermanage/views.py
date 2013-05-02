# Create your views here.
from usermanage.models import UserCreateForm, Group, GroupCreateForm, Membership
from django.template import RequestContext
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.utils import simplejson
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.contrib import messages


@login_required
def createGroup(request):
    if(request.method == "POST"):
        form = GroupCreateForm(data=request.POST)
        if form.is_valid():
            group = form.save(commit=False)
            group.creator = request.user
            group.save()
            m = Membership(user=request.user, group=group, status=1)
            m.save()
            messages.info(request, "Group \"" + group.name + "\" created.")
            return redirect('/')
    else:
        form = GroupCreateForm()
    return render_to_response('form_base.html', {"form": form, "heading": "Group Creation"}, context_instance=RequestContext(request))


@login_required
def listGroups(request):
    groups = request.user.group_set.all()
    return render_to_response('usermanage/group_list.html', {"groups": groups}, context_instance=RequestContext(request))


@login_required
def viewGroup(request, group_id):
    group = get_object_or_404(Group, uid=group_id)
    if request.user in group.all_users():
        return render_to_response('usermanage/group_details.html', {"group": group}, context_instance=RequestContext(request))
    else:
        return render_to_response('usermanage/join_group.html', {"group": group}, context_instance=RequestContext(request))
    # else msg user and redirect


@login_required
def editGroup(request, group_id):
    group = get_object_or_404(Group, uid=group_id)
    if request.user != group.creator and request.user not in group.admins():
        # message about authentication
        return redirect("/account/group/")
    try:
        membership = Membership.objects.get(group=group, user=request.user)
        if membership.is_staff():
            if request.method == "POST":
                form = GroupCreateForm(data=request.POST, instance=group)
                if form.is_valid():
                    group = form.save()
                    # need to check if permissions change
                    return redirect('/account/group')
            else:
                form = GroupCreateForm(instance=group)
            return render_to_response('form_base.html', {"form": form, "heading": "Edit Group"}, context_instance=RequestContext(request))
    except ObjectDoesNotExist or MultipleObjectsReturned:
        return redirect("/account/group/")


@login_required
def deleteGroup(request, group_id):
    group = get_object_or_404(Group, uid=group_id)
    if request.user != group.creator:
        # message about authentication
        return redirect("/account/group/")
    # Do some "are you sure you want to delete this group"
    # you are removing x questions etc..
    group.delete()
    # message about group deletion
    return redirect("/account/group")


@login_required
def editGroupPerms(request, group_id):
    group = get_object_or_404(Group, uid=group_id)
    memberships = Membership.objects.filter(group=group).exclude(user=group.creator)
    if request.user != group.creator and request.user not in group.admins():
        # message about authentication
        return redirect("/account/group/")
    if request.method == "POST":
        user_perms = simplejson.loads(request.POST.get("user_arr"))
        for u in user_perms:
            user = User.objects.get(pk=u['id'])
            if user != group.creator and user in group.users.all():
                member = memberships.get(user=user)
                member.status = int(u['status'])
                member.save()
    return render_to_response('usermanage/group_perms.html', {"memberships": memberships, "group": group}, context_instance=RequestContext(request))


@login_required
def addUserToGroup(request, group_id, user_id):
    group = get_object_or_404(Group, uid=group_id)
    user = get_object_or_404(User, pk=user_id)
    if user not in group.users.all():
        membership = Membership(group=group, user=user)
        membership.save()
        return HttpResponse(simplejson.dumps({"success": True, "error_code": 0}), mimetype='application/json')
    else:
        return HttpResponse(simplejson.dumps({"success": False, "error_code": 1}), mimetype='application/json')
    # Error Codes:
    # 0: No error
    # 1: User already exists in group


@login_required
def removeUserFromGroup(request, group_id, user_id):
    group = get_object_or_404(Group, uid=group_id)
    user = get_object_or_404(User, pk=user_id)
    if user is request.user or request.user in group.admins() or request.user == group.creator:
        if user is group.creator:
            return HttpResponse(simplejson.dumps({"success": False, "error_code": 2}), mimetype='application/json')
        else:
            Membership.objects.filter(user=user, group=group).delete()
        return HttpResponse(simplejson.dumps({"success": True, "error_code": 0}), mimetype='application/json')
    # Error Codes:
    # 0: No error
    # 1: Insufficient privileges
    # 2: Tried to delete admin
    return HttpResponse(simplejson.dumps({"success": False, "error_code": 1}), mimetype='application/json')


def registerUser(request):
    if request.method == 'POST':
        form = UserCreateForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/')
    else:
        form = UserCreateForm()
    return render_to_response("form_base.html", {'form': form})


def ajaxLogin(request):
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(username=username, password=password)
    if user is not None:
        if user.is_active:
            login(request, user)
            return HttpResponse(simplejson.dumps({"success": True, "error_code": 0}), mimetype='application/json')
        else:
            # Error codes:
            # 0 = No Error
            # 1 = Auth Error
            # 2 = Inactive User Error
            return HttpResponse(simplejson.dumps({"success": False, "error_code": 2, "error_msg": "Sorry, that user is inactive."}), mimetype='application/json')
    else:
        return HttpResponse(simplejson.dumps({"success": False, "error_code": 1, "error_msg": "Invalid login. The username and password did not match."}), mimetype='application/json')
