# Create your views here.
from usermanage.models import UserCreateForm
from django.shortcuts import render_to_response, redirect


def registerUser(request):
    if request.method == 'POST':
        form = UserCreateForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/')
    else:
        form = UserCreateForm()
    return render_to_response("form_base.html", {'form': form})
