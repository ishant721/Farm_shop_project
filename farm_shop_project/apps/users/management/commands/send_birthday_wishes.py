# apps/users/management/commands/send_birthday_wishes.py
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import date, datetime
from django.db.models import Q
from django.conf import settings

from apps.users.models import CustomUser
from apps.users.utils import send_birthday_wishing_email #, send_whatsapp_message, send_sms_message # Commented out Twilio

class Command(BaseCommand):
    help = 'Sends birthday wishes email to users whose birthday is today.'

    def handle(self, *args, **options):
        # Get today's date in the project's TIME_ZONE
        # Use timezone.localtime(timezone.now()).date() for local time if TIME_ZONE is set correctly
        today_local = timezone.localtime(timezone.now()).date()
        current_hour_local = timezone.localtime(timezone.now()).hour

        # Check if the current hour matches the desired sending hour
        if current_hour_local != settings.BIRTHDAY_WISH_HOUR:
            self.stdout.write(self.style.WARNING(
                f"Skipping birthday wishes. Current hour ({current_hour_local}) does not match configured sending hour ({settings.BIRTHDAY_WISH_HOUR})."
            ))
            return

        # Filter active users whose date_of_birth matches today's month and day
        # Ensure date_of_birth is not null for this query
        users_with_birthday = CustomUser.objects.filter(
            Q(is_active=True),
            Q(date_of_birth__month=today_local.month),
            Q(date_of_birth__day=today_local.day)
        ).exclude(is_superuser=True) # Exclude superusers from automated wishes if desired

        if not users_with_birthday.exists():
            self.stdout.write(self.style.SUCCESS(f"No birthdays today ({today_local.strftime('%Y-%m-%d')})."))
            return

        self.stdout.write(self.style.SUCCESS(f"Attempting to send birthday wishes for {len(users_with_birthday)} users on {today_local.strftime('%Y-%m-%d')} at {settings.BIRTHDAY_WISH_HOUR}:00..."))

        emails_sent = 0
        # messages_sent = 0 # Commented out for Twilio

        for user in users_with_birthday:
            if user.email:
                if send_birthday_wishing_email(user):
                    emails_sent += 1
            else:
                self.stdout.write(self.style.WARNING(f"Skipping birthday email for {user.username}: No email address found."))

            # --- Twilio Messaging (Commented out for now) ---
            # if settings.TWILIO_ACCOUNT_SID and settings.TWILIO_AUTH_TOKEN:
            #     if user.phone_number:
            #         message_body = f"Happy Birthday, {user.first_name if user.first_name else user.username}! Wishing you a great day from Farm Shop!"
            #         # For WhatsApp, ensure the number is formatted as 'whatsapp:+1234567890'
            #         # For SMS, ensure the number is formatted as '+1234567890'
            #         if user.phone_number.is_valid(): # Check if it's a valid E.164 number
            #             # Example: WhatsApp first, then SMS if WhatsApp not configured or desired
            #             if settings.TWILIO_WHATSAPP_NUMBER and send_whatsapp_message(user.phone_number.as_e164, message_body):
            #                 messages_sent += 1
            #             elif settings.TWILIO_PHONE_NUMBER and send_sms_message(user.phone_number.as_e164, message_body):
            #                 messages_sent += 1
            #         else:
            #             self.stdout.write(self.style.WARNING(f"Skipping birthday message for {user.username}: Invalid phone number format or not provided."))
            #     else:
            #         self.stdout.write(self.style.WARNING(f"Skipping birthday message for {user.username}: No phone number found."))

        self.stdout.write(self.style.SUCCESS(f"Successfully sent {emails_sent} birthday emails."))
        # self.stdout.write(self.style.SUCCESS(f"Successfully sent {messages_sent} birthday messages.")) # Commented out