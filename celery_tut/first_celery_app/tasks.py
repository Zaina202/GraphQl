import csv
import sys
import logging
from .models import UploadedFile, Person
from celery import shared_task

logger = logging.getLogger(__name__)

@shared_task
def process_csv(file_id):
    print("Hello from process_csv task", file=sys.stderr, flush=True)
    try:
        print("process start", file=sys.stderr, flush=True)
        
        file_record = UploadedFile.objects.get(id=file_id)
        

        print(f"File path: {file_record.file.path}", file=sys.stderr, flush=True)


        with file_record.file.open('r') as f:
            reader = csv.reader(f)
            for row in reader:
                try:
                    name, age, gender = row
                    Person.objects.create(
                        name=name.strip(),
                        age=int(age.strip()),
                        gender=gender.strip()
                    )
                except Exception as inner_e:
                    logger.error(f"Error saving row {row}: {inner_e}")
                    continue

        file_record.status = 'saved to database'
    except Exception as e:
        logger.error(f"Error processing file_id={file_id}: {e}")
        file_record.status = 'failed'
    file_record.save()

