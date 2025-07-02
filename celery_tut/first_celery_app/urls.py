from django.urls import path
from .views import export_females_view,upload_excel_view
from graphene_django.views import GraphQLView
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    path('export-females/', export_females_view, name='export-females'),
    path("graphql/", csrf_exempt(GraphQLView.as_view(graphiql=True))),
    path('upload-excel/', upload_excel_view, name='upload-excel'),

]
