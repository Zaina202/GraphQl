from django.http import JsonResponse
from .models import UploadedFile,UploadeFile,Person, Book, Author
from .tasks import export_agchart_females_to_excel
from django.views.decorators.csrf import csrf_exempt
import openpyxl
from django.http import JsonResponse
from django.core.files.storage import default_storage
import pandas as pd

@csrf_exempt
def export_females_view(request):
    print("View was called")
    if request.method == 'POST':
        file_record = UploadedFile(status='processing')
        file_record.save()

        export_agchart_females_to_excel.delay(file_record.id)

        return JsonResponse({'message': 'Export started. Email will be sent.', 'file_id': file_record.id})

    return JsonResponse({'error': 'Only POST allowed'}, status=405)


@csrf_exempt
def upload_excel_view(request):
    if request.method == 'POST':
        excel_file = request.FILES.get('file')
        if not excel_file:
            return JsonResponse({'error': 'No file provided'}, status=400)

        file_record = UploadeFile.objects.create(file=excel_file)
        try:
            df = pd.read_excel(file_record.file.path)

            model_type = request.POST.get('model')  # 'person', 'book', or 'author'

            if model_type == 'person':
                for _, row in df.iterrows():
                    Person.objects.create(
                        name=row['name'],
                        age=row['age'],
                        gender=row['gender']
                    )
            elif model_type == 'author':
                for _, row in df.iterrows():
                    Author.objects.create(name=row['name'])
            elif model_type == 'book':
                for _, row in df.iterrows():
                    author, _ = Author.objects.get_or_create(name=row['author'])
                    Book.objects.create(
                        title=row['title'],
                        author=author,
                        published_date=row['published_date'],
                        status=row['status'].lower()  # Assuming 'draft'/'published'
                    )
            else:
                return JsonResponse({'error': 'Invalid model type'}, status=400)

            return JsonResponse({'message': f'{model_type.capitalize()}s created successfully.'})

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Only POST allowed'}, status=405)