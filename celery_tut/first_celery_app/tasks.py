
# tasks.py
import pandas as pd
import tempfile
import logging
from django.core.files import File
from django.core.mail import EmailMessage
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import get_user_model
from celery import shared_task
from .models import UploadedFile
from graphene_django.settings import graphene_settings

logger = logging.getLogger(__name__)


@shared_task
def export_agchart_females_to_excel(file_id):
    print("Task started")
    try:
        file_record = UploadedFile.objects.get(id=file_id)
        print("File record found:", file_id)
        schema = graphene_settings.SCHEMA
        query = '''
        query {
            femaleNamesWithCounts {
                name
                count
            }
        }
        '''
        result = schema.execute(query)

        if result.errors:
            file_record.status = 'failed - query error'
            file_record.save()
            logger.error(f"GraphQL error: {result.errors}")
            return

        data = result.data['femaleNamesWithCounts']
        df = pd.DataFrame(data)

        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp:
            df.to_excel(tmp.name, index=False)
            tmp.seek(0)
            file_record.file.save(f"female_names_{file_id}.xlsx", File(tmp))
            file_record.status = 'saved to database'
            file_record.save()

        subject = "GraphQl query results"
        message = "Attached is the Excel export of query results."

        User = get_user_model()
        superusers = User.objects.filter(is_superuser=True)
        to_emails = [u.email for u in superusers if u.email]
        print("Email sending to:", to_emails)
        if to_emails:
            email = EmailMessage(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                to_emails,
            )
            email.attach_file(file_record.file.path)
            email.send(fail_silently=False)

    except Exception as e:
        logger.error(f"Export error: {e}")
        file_record.status = 'failed'
        file_record.save()
