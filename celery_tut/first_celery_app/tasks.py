import sys
import logging
import csv
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

        # Read CSV file
        try:
            with open(file_record.file.path, 'r', encoding='utf-8') as f:
                # Skip header row
                next(f)
                
                # Process each row
                for index, row in enumerate(csv.reader(f), start=1):
                    try:
                        # Skip if row doesn't have enough columns
                        if len(row) < 3:
                            logger.warning(f"Skipping row {index} due to insufficient columns")
                            continue
                            
                        name, age, gender = row
                        
                        # Skip if any required field is empty
                        if not name.strip() or not age.strip() or not gender.strip():
                            logger.warning(f"Skipping row {index} due to empty values")
                            continue
                            
                        # Convert values to appropriate types
                        try:
                            name = name.strip()
                            age = int(float(age))  # Handle both integer and float values
                            gender = gender.strip()
                            
                            Person.objects.create(
                                name=name,
                                age=age,
                                gender=gender
                            )
                            logger.info(f"Successfully created record for {name}")
                        except ValueError as ve:
                            logger.error(f"Error converting values in row {index}: {ve}")
                            continue
                            
                    except Exception as inner_e:
                        logger.error(f"Error processing row {index}: {inner_e}")
                        continue
                        
            file_record.status = 'saved to database'
            
        except Exception as e:
            logger.error(f"Error processing CSV file: {e}")
            file_record.status = 'failed - file processing error'
            
    except Exception as e:
        logger.error(f"Error processing file_id={file_id}: {e}")
        file_record.status = 'failed'
    file_record.save()

