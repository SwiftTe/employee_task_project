from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings
from datetime import datetime, timedelta

User = get_user_model()


class Command(BaseCommand):
    help = 'Send daily summary emails to all users'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be sent without actually sending emails',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN - No emails will be sent'))
        
        users = User.objects.filter(is_active_employee=True)
        
        for user in users:
            summary = self.generate_user_summary(user)
            
            if dry_run:
                self.stdout.write(f'\n--- Email for {user.username} ---')
                self.stdout.write(f'Subject: {summary["subject"]}')
                self.stdout.write(f'Body:\n{summary["body"]}')
            else:
                try:
                    send_mail(
                        subject=summary['subject'],
                        message=summary['body'],
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[user.email],
                        fail_silently=False,
                    )
                    self.stdout.write(self.style.SUCCESS(f'Email sent to {user.email}'))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Failed to send email to {user.email}: {e}'))
        
        self.stdout.write(self.style.SUCCESS(f'Processed {users.count()} users'))

    def generate_user_summary(self, user):
        from tasks.models import Task
        from analytics.models import EmployeeProductivity
        
        today = datetime.now().date()
        
        # Get today's productivity
        try:
            productivity = EmployeeProductivity.objects.get(user=user, date=today)
            productivity_summary = f"""
Today's Summary:
- Tasks Completed: {productivity.tasks_completed}
- Tasks Assigned: {productivity.tasks_assigned}
- Hours Logged: {productivity.hours_logged}
- Efficiency Score: {productivity.efficiency_score}
"""
        except EmployeeProductivity.DoesNotExist:
            productivity_summary = "No productivity data recorded for today."
        
        # Get pending tasks
        pending_tasks = Task.objects.filter(
            assigned_to=user,
            status__in=['TODO', 'IN_PROGRESS']
        ).count()
        
        # Get overdue tasks
        overdue_tasks = Task.objects.filter(
            assigned_to=user,
            due_date__lt=datetime.now(),
            status__in=['TODO', 'IN_PROGRESS']
        ).count()
        
        subject = f"Daily Task Summary - {today.strftime('%Y-%m-%d')}"
        
        body = f"""
Hello {user.first_name},

{productivity_summary}

Current Status:
- Pending Tasks: {pending_tasks}
- Overdue Tasks: {overdue_tasks}

Have a productive day!

Best regards,
Employee Task Management System
"""
        
        return {
            'subject': subject,
            'body': body.strip()
        }
