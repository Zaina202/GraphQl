from django.urls import path
from .views import export_females_view

urlpatterns = [
    path('export-females/', export_females_view, name='export-females'),
]
