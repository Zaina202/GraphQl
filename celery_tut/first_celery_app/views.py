from django.http import JsonResponse
from .models import UploadedFile
from .tasks import process_csv
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def upload_csv(request):
    if request.method == 'POST':
        file = request.FILES['file']
        file_obj = UploadedFile(file=file, status='processing')
        file_obj.save() 
        
        process_csv.delay(file_obj.id)  
        return JsonResponse({'status': 'success','file_id': file_obj.id})
    else:
        return JsonResponse({'error': 'Only POST allowed'}, status=405)
