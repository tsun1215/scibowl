# Create your views here.
from usermanage.models import UserCreateForm
from django.shortcuts import render_to_response, redirect
from django.contrib.auth import authenticate, login
from django.utils import simplejson
from django.http import HttpResponse


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
