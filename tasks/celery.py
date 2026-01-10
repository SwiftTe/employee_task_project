import os
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings


@shared_task
def send_task_notification_email(task_id, notification_type):
    """
    Send task notification email to assigned user
    """
    try:
        from .models import Task
        
        task = Task.objects.get(id=task_id)
        subject = f"Task {notification_type}: {task.title}"
        
        message = f"""
        Task: {task.title}
        Description: {task.description}
        Priority: {task.priority}
        Due Date: {task.due_date}
        Status: {task.status}
        
        Please check your dashboard for more details.
        """
        
        recipient_list = [task.assigned_to.email] if task.assigned_to else []
        
        if recipient_list:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=recipient_list,
                fail_silently=False,
            )
            return f"Email sent to {recipient_list}"
        else:
            return "No recipient found"
            
    except Exception as e:
        return f"Error sending email: {str(e)}"


@shared_task
def generate_daily_productivity_report():
    """
    Generate daily productivity report for all employees
    """
    try:
        from analytics.models import EmployeeProductivity
        from django.utils import timezone
        from datetime import timedelta
        
        yesterday = timezone.now() - timedelta(days=1)
        
        # Generate productivity reports for all employees
        employees = EmployeeProductivity.objects.filter(
            date=yesterday.date()
        )
        
        report_data = []
        for emp_prod in employees:
            report_data.append({
                'user': emp_prod.user.username,
                'tasks_completed': emp_prod.tasks_completed,
                'hours_worked': emp_prod.hours_worked,
                'efficiency_score': emp_prod.efficiency_score,
            })
        
        return f"Generated report for {len(report_data)} employees"
        
    except Exception as e:
        return f"Error generating report: {str(e)}"


@shared_task
def update_project_analytics(project_id):
    """
    Update project analytics when tasks are modified
    """
    try:
        from analytics.models import ProjectAnalytics
        from .models import Task, Project
        
        project = Project.objects.get(id=project_id)
        
        # Calculate project metrics
        tasks = Task.objects.filter(project=project)
        total_tasks = tasks.count()
        completed_tasks = tasks.filter(status='completed').count()
        
        # Update or create project analytics
        analytics, created = ProjectAnalytics.objects.get_or_create(
            project=project,
            defaults={
                'total_tasks': total_tasks,
                'completed_tasks': completed_tasks,
                'completion_rate': (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0,
            }
        )
        
        if not created:
            analytics.total_tasks = total_tasks
            analytics.completed_tasks = completed_tasks
            analytics.completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
            analytics.save()
        
        return f"Updated analytics for project {project.name}"
        
    except Exception as e:
        return f"Error updating project analytics: {str(e)}"
