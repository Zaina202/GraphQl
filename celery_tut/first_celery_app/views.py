# views.py
from django.http import JsonResponse
from .models import UploadedFile
from .tasks import export_agchart_females_to_excel
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def export_females_view(request):
    print("View was called")
    if request.method == 'POST':
        file_record = UploadedFile(status='processing')
        file_record.save()

        export_agchart_females_to_excel.delay(file_record.id)

        return JsonResponse({'message': 'Export started. Email will be sent.', 'file_id': file_record.id})

    return JsonResponse({'error': 'Only POST allowed'}, status=405)
