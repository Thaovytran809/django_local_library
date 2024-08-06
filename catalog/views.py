from typing import Any
from django.db.models.query import QuerySet
from django.shortcuts import render
from .models import Book, BookInstance, Author, Genre, Language
from django.views import generic
from django.shortcuts import get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views import View
import datetime
from django.http import HttpResponseRedirect
from django.urls import reverse
from catalog.forms import RenewBookForm
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy

# Create your views here.
def index(request):
    num_book = Book.objects.all().count()
    num_instance = BookInstance.objects.all().count()

    num_instance_available = BookInstance.objects.filter(status__exact = "a").count()

    num_author = Author.objects.count()

    num_book_contain_a = Book.objects.filter(title__icontains = "a").count()
    num_genere_contain_a = Genre.objects.filter(name__icontains = "a").count()

    num_visit = request.session.get('num_visit',0)
    request.session['num_visit'] = num_visit + 1


    context = {
        'num_book': num_book,
        'num_instance': num_instance,
        'num_instance_available': num_instance_available,
        'num_author': num_author,
        'num_book_contain_a': num_book_contain_a,
        'num_genre_contain_a': num_genere_contain_a,
        'num_visit': num_visit
    }

    return render(request, 'index.html', context=context)

class BookListView(generic.ListView):
    model = Book
    context_object_name = 'book_list'
    paginate_by = 10

class BookDetailView(generic.DetailView):
    model = Book

def book_detail_view(request, key_primary):
    book = get_object_or_404(Book, pk=key_primary)
    return render(request, 'catalog/book_detail.html', context={'book':book})

class AuthorListView(generic.ListView):
    model = Author
    context_object_name = 'author_list'
    paginate_by = 10

class AuthorDetailView(generic.DetailView):
    model = Author

def author_detail_view(request, key_primary):
    author = get_object_or_404(Author, pk=key_primary)
    return render(request, 'catalog/author_detail.html', context={"author":author})

class LoanedBooksByUserListView(LoginRequiredMixin, generic.ListView):
    model = BookInstance
    template_name = 'catalog/bookinstance_list_borrowed_user.html'
    paginate_by = 10

    def get_queryset(self):
        return (
            BookInstance.objects.filter(borrower = self.request.user)
                                .filter(status__exact="o")
                                .order_by('due_back')
        )
class LoanedBooksByStaffListView(LoginRequiredMixin, PermissionRequiredMixin, generic.ListView):
    model = BookInstance
    template_name = 'catalog/bookinstance_list_borrowed_staff.html'
    paginate_by =10
    permission_required = 'catalog.can_marked_returned'
    def get_queryset(self):
        return (
            BookInstance.objects.filter(status__exact = "o").order_by('due_back')
        )
class MyView(PermissionRequiredMixin, View):
    permission_required = 'catalog.can_mark_returned'
    # Or multiple permissions
    permission_required = ('catalog.can_mark_returned', 'catalog.change_book')
    # Note that 'catalog.change_book' is permission
    # Is created automatically for the book model, along with add_book, and delete_book

def renew_book_librarian(request, pk):
    book_instance = get_object_or_404(BookInstance, pk=pk)

    if request.method == 'POST':
        form = RenewBookForm(request.POST)
        if form.is_valid():
            book_instance.due_back = form.cleaned_data['renewal_date']
            book_instance.save()
            return HttpResponseRedirect(reverse('all-borrowed'))
    else:
        proposed_renewal_date = datetime.date.today()+datetime.timedelta(weeks=3)
        form = RenewBookForm(initial={'renew_date': proposed_renewal_date})

        context = {
            'form':form,
            'book_instance': book_instance
        }
    return render(request, 'catalog/book_renew_librarian.html', context=context)

class AuthorCreate(PermissionRequiredMixin, CreateView):
    model = Author
    fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death']
    initial = {'date_of_death': '11/11/2023'}
    permission_required = 'catalog.add_author'

class AuthorUpdate(PermissionRequiredMixin, UpdateView):
    model=Author
    fields = '__all__'
    permission_required = 'catalog.change_author'

class AuthorDelete(PermissionRequiredMixin, DeleteView):
    model = Author
    success_url = reverse_lazy('authors')
    permission_required = 'catalog.delete_author'

    def form_valid(self, form):
        try:
            self.object.delete()
            return HttpResponseRedirect(self.success_url)
        except Exception as e:
            return HttpResponseRedirect(
                reverse("author-delete", kwargs={"pk": self.object.pk})
            )
        
class BookCreate(PermissionRequiredMixin, CreateView):
    model = Book
    fields = '__all__'
    permission_required = 'catalog.create_book'
class BookUpdate(PermissionRequiredMixin, UpdateView):
    model = Book
    fields = '__all__'
    permission_required = 'catalog.update_book'
class BookDelete(PermissionRequiredMixin, DeleteView):
    model = Book
    success_url = reverse_lazy("books")
    permission_required = 'catalog.delete_book'

    def form_valid(self, form):
        try:
            self.object.delete()
            return HttpResponseRedirect(self.success_url)
        except Exception as e:
            return HttpResponseRedirect(reverse('book-delete'), kwargs={"pk":self.object.pk})
        
    



