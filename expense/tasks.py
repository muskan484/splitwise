from celery import shared_task
from django.core.mail import send_mail
from splitwise.settings import DEFAULT_FROM_EMAIL
from expense.models import Passbook
from user.models import User
from collections import defaultdict
from django.db.models import Sum
from django.utils import timezone
from datetime import timedelta,datetime

from_email= DEFAULT_FROM_EMAIL

@shared_task
def send_email_task(email_data):
    """
    Sends an email notification each time an expense is created.

    Parameters: A dictionary containing email-related data, including user name, email address,
                name of the person who owes, and the amount of the expense.
    """
    subject = f'Notification: New Expense Created on Splitwise'
    message = f'''Dear {email_data['user_name']},\n\nYou've been included in a new expense by {email_data['owes_to_name']}.\n\nExpense Details:\nAmount: {email_data['amount']}\n\nPlease take a moment to review the details and address any necessary actions.\nThank you'''
    recipient = [email_data['user_email']]
    send_mail(subject, message,from_email,recipient)


@shared_task
def send_weekly_summary_email():
    """
    Sends a weekly summary email to each user.

    Queries passbook entries for each user to calculate the total amount owed to other users within the last week.
    Then, sends an email containing the summary of amounts owed to other user.

    """
    unique_users = User.objects.all()
    today = timezone.now().date()

    last_week_start = today - timedelta(days=today.weekday() + 7)

    for user in unique_users:
        required_dict = defaultdict(float)
        entries_per_user = Passbook.objects.filter(user=user,
                                                    user__expenses_paid__created_at__date__gte=last_week_start,
                                                    user__expenses_paid__created_at__date__lte=today
                                                ).\
                                            exclude(owes_to=user).\
                                            values('owes_to__userId').\
                                            annotate(total_amount=Sum('amount'))
        for entry in entries_per_user:
            owes_to_user_id = entry['owes_to__userId']
            total_amount = float(entry['total_amount'])
            required_dict[owes_to_user_id] += total_amount

        if required_dict:
            subject = 'Your Weekly Splitwise Summary'
            message = format_email_message(user, required_dict)
            send_mail(
                subject = subject,
                message = message,
                from_email = from_email,
                recipient_list = [user.email],
                fail_silently=False)

def format_email_message(user, required_dict):
    """
    Formats the email message containing the weekly Splitwise summary for a user.

    Parameters:
    - user (User): The user to whom the email will be sent.
    - required_dict (dict): A dictionary containing the summary of amounts owed to the user by other users.
                            Keys are user IDs, and values are the total amounts owed.

    Returns: The formatted email message containing the weekly Splitwise summary.
    """
    formatted_summary = "\n".join([f"{User.objects.get(userId=user_id).name}: ₹{total_amount:.2f}" for user_id, total_amount in required_dict.items()])
    total_owed_amount = sum(required_dict.values())
    formatted_summary += f"\n\nTotal Owed Amount: ₹{total_owed_amount:.2f}"
    return f"""Dear {user.name},\n\nWe hope this message finds you well. As part of our weekly Splitwise summary, here's a breakdown of the amounts you owe to other users:\n\n{formatted_summary}\n\nPlease take a moment to review the details and address any necessary actions.\n\nThank you"""


    