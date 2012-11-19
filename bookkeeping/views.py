from bookkeeping.models import Book, BookForm
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect


def addBook(request):
    action = "/book/add"
    if(request.method == "POST"):
        form = BookForm(data=request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/')
    else:
        form = BookForm()
    return render_to_response('bookkeeping/bookform.html', {"form": form, "type": 'Book', "action": action, "title": "Add Book"})


def editBook(request, book_id):
    action = "/book/edit/" + book_id
    book = get_object_or_404(Book, id=book_id)
    if request.method == "POST":
        form = BookForm(data=request.POST)
        if form.is_valid():
            b = form.save(commit=False)
            b.id = book_id
            b.save()
            b.subject.clear()
            for subject in form.cleaned_data['subject']:
                b.subject.add(subject)
            return HttpResponseRedirect('/')
    else:
        form = BookForm(instance=book)
    return render_to_response('bookkeeping/bookform.html', {"form": form, "action": action, "type": "book", "title": "Edit Book"})
