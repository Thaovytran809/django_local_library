from django.contrib import admin
from catalog.models import Book, Genre, BookInstance, Language, Author

# Register your models here.
class BookInstanceInline(admin.TabularInline):
    model = BookInstance
@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'display_genre')
    inlines = [BookInstanceInline]

@admin.register(BookInstance)
class BookInstanceAdmin(admin.ModelAdmin):
    list_display = ('id', 'book', 'status', 'due_back')
    list_filter = ('status', 'due_back')
    fieldsets = (
        (None, {'fields' : ('id', 'book', 'imprint')}),
        ('Availability', {'fields':('status', 'due_back', 'borrower')})
    )
@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    pass

class BookInlines(admin.TabularInline):
    model = Book
@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'date_of_birth', 'date_of_death')
    fields = ['first_name', 'last_name', ('date_of_birth', 'date_of_death')]
    inlines = [BookInlines]
@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    pass

