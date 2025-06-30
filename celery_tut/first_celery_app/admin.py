
from django.contrib import admin
from .models import Book
from django.contrib.admin import SimpleListFilter
from django.contrib.admin.models import LogEntry, CHANGE
from django.contrib.contenttypes.models import ContentType
from django.utils.encoding import force_str


@admin.action(description="Mark selected books as Published")
def mark_published(modeladmin, request, queryset):
    updated_count = queryset.update(status='published')

    for obj in queryset:
        LogEntry.objects.log_action(
            user_id=request.user.pk,
            content_type_id=ContentType.objects.get_for_model(obj).pk,
            object_id=obj.pk,
            object_repr=force_str(obj),
            action_flag=CHANGE,
            change_message="Marked as published via admin action."
        )

    modeladmin.message_user(request, f"{updated_count} book(s) marked as published.")


class PublishedYearFilter(SimpleListFilter):
    title = 'Published Year'
    parameter_name = 'published_year'

    def lookups(self, request, model_admin):
        years = Book.objects.values_list('published_date__year', flat=True).distinct()
        return [(year, year) for year in years if year]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(published_date__year=self.value())

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'published_date', 'status')
    list_filter = ('status', PublishedYearFilter)
    actions = [mark_published]

    class Media:
        css = {
            'all': ['admin/css/custom.css'],
        }
        js = ['admin/js/custom.js']
