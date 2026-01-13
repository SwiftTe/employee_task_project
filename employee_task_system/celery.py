from celery import Celery
import os
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'employee_task_system.settings')

app = Celery('employee_task_system')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

User = get_user_model()


@app.task(bind=True)
def send_task_notification_email(self, user_id, task_title, message):
    """
    Send email notification to user about task updates
    """
    try:
        user = User.objects.get(id=user_id)
        subject = f"Task Update: {task_title}"
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
        
        return f"Email sent to {user.email}"
    
    except Exception as exc:
        self.retry(exc=exc, countdown=60, max_retries=3)


@app.task(bind=True)
def generate_daily_productivity_report(self):
    """
    Generate daily productivity metrics for all employees
    """
    try:
        from tasks.models import Task, TimeLog
        from analytics.models import EmployeeProductivity, WorkloadDistribution
        from django.db.models import Sum, Count
        
        today = timezone.now().date()
        employees = User.objects.filter(is_active_employee=True)
        
        for employee in employees:
            # Calculate daily metrics
            tasks_assigned = Task.objects.filter(assigned_to=employee).count()
            tasks_completed = Task.objects.filter(
                assigned_to=employee,
                status='COMPLETED',
                completed_at__date=today
            ).count()
            
            hours_logged = TimeLog.objects.filter(
                user=employee,
                date=today
            ).aggregate(total=Sum('hours'))['total'] or 0
            
            # Calculate efficiency score
            efficiency_score = 0
            if hours_logged > 0:
                efficiency_score = round((tasks_completed / float(hours_logged)) * 100, 2)
            
            # Update or create productivity record
            EmployeeProductivity.objects.update_or_create(
                user=employee,
                date=today,
                defaults={
                    'tasks_completed': tasks_completed,
                    'tasks_assigned': tasks_assigned,
                    'hours_logged': hours_logged,
                    'efficiency_score': efficiency_score
                }
            )
            
            # Update workload distribution
            active_tasks = Task.objects.filter(
                assigned_to=employee,
                status__in=['TODO', 'IN_PROGRESS']
            ).count()
            
            total_estimated_hours = Task.objects.filter(
                assigned_to=employee,
                status__in=['TODO', 'IN_PROGRESS']
            ).aggregate(total=Sum('estimated_hours'))['total'] or 0
            
            overdue_tasks = Task.objects.filter(
                assigned_to=employee,
                due_date__lt=timezone.now(),
                status__in=['TODO', 'IN_PROGRESS']
            ).count()
            
            # Calculate workload score
            workload_score = 0
            if total_estimated_hours > 0:
                workload_score = min(100, (total_estimated_hours / 8) * 100)  # 8 hours = 100% workload
            
            WorkloadDistribution.objects.update_or_create(
                user=employee,
                date=today,
                defaults={
                    'active_tasks_count': active_tasks,
                    'total_estimated_hours': total_estimated_hours,
                    'overdue_tasks_count': overdue_tasks,
                    'workload_score': workload_score
                }
            )
        
        return f"Daily productivity report generated for {employees.count()} employees"
    
    except Exception as exc:
        self.retry(exc=exc, countdown=60, max_retries=3)


@app.task(bind=True)
def update_project_analytics(self):
    """
    Update analytics for all projects
    """
    try:
        from tasks.models import Project
        from analytics.models import ProjectAnalytics
        
        projects = Project.objects.all()
        
        for project in projects:
            analytics, created = ProjectAnalytics.objects.get_or_create(
                project=project
            )
            analytics.update_metrics()
        
        return f"Analytics updated for {projects.count()} projects"
    
    except Exception as exc:
        self.retry(exc=exc, countdown=60, max_retries=3)


@app.task(bind=True)
def analyze_task_delays(self):
    """
    Analyze delays for completed tasks
    """
    try:
        from tasks.models import Task
        from analytics.models import DelayAnalysis
        
        completed_tasks = Task.objects.filter(
            status='COMPLETED',
            completed_at__isnull=False,
            delay_analysis__isnull=True
        )
        
        for task in completed_tasks:
            delay_analysis = DelayAnalysis.objects.create(task=task)
            delay_analysis.calculate_delay()
        
        return f"Delay analysis completed for {completed_tasks.count()} tasks"
    
    except Exception as exc:
        self.retry(exc=exc, countdown=60, max_retries=3)


@app.task(bind=True)
def send_overdue_task_notifications(self):
    """
    Send notifications for overdue tasks
    """
    try:
        from tasks.models import Task
        
        overdue_tasks = Task.objects.filter(
            due_date__lt=timezone.now(),
            status__in=['TODO', 'IN_PROGRESS']
        )
        
        for task in overdue_tasks:
            if task.assigned_to:
                message = f"""
                Dear {task.assigned_to.full_name},
                
                This is a reminder that the following task is overdue:
                
                Title: {task.title}
                Due Date: {task.due_date.strftime('%Y-%m-%d')}
                Priority: {task.priority}
                
                Please update the task status or contact your manager if you need an extension.
                
                Best regards,
                Employee Task Management System
                """
                
                send_task_notification_email.delay(
                    task.assigned_to.id,
                    task.title,
                    message
                )
        
        return f"Overdue task notifications sent for {overdue_tasks.count()} tasks"
    
    except Exception as exc:
        self.retry(exc=exc, countdown=60, max_retries=3)


@app.task(bind=True)
def generate_department_analytics(self):
    """
    Generate daily department analytics
    """
    try:
        from analytics.models import DepartmentAnalytics
        from django.db.models import Avg
        
        today = timezone.now().date()
        departments = User.objects.filter(
            is_active_employee=True,
            department__isnull=False
        ).values_list('department', flat=True).distinct()
        
        for department in departments:
            employees = User.objects.filter(
                department=department,
                is_active_employee=True
            )
            
            total_employees = employees.count()
            
            # Get productivity metrics for this department
            productivity_metrics = EmployeeProductivity.objects.filter(
                user__department=department,
                date=today
            )
            
            active_tasks = 0
            completed_tasks = 0
            total_hours = 0
            efficiency_scores = []
            
            for metric in productivity_metrics:
                active_tasks += metric.tasks_assigned - metric.tasks_completed
                completed_tasks += metric.tasks_completed
                total_hours += metric.hours_logged
                efficiency_scores.append(metric.efficiency_score)
            
            average_efficiency = 0
            if efficiency_scores:
                average_efficiency = sum(efficiency_scores) / len(efficiency_scores)
            
            DepartmentAnalytics.objects.update_or_create(
                department=department,
                date=today,
                defaults={
                    'total_employees': total_employees,
                    'active_tasks': active_tasks,
                    'completed_tasks': completed_tasks,
                    'total_hours_logged': total_hours,
                    'average_efficiency': round(average_efficiency, 2)
                }
            )
        
        return f"Department analytics generated for {len(departments)} departments"
    
    except Exception as exc:
        self.retry(exc=exc, countdown=60, max_retries=3)


# Schedule periodic tasks
from celery.schedules import crontab

app.conf.beat_schedule = {
    'generate-daily-productivity': {
        'task': 'employee_task_system.celery.generate_daily_productivity_report',
        'schedule': crontab(hour=23, minute=59),  # Run daily at 11:59 PM
    },
    'update-project-analytics': {
        'task': 'employee_task_system.celery.update_project_analytics',
        'schedule': crontab(hour=0, minute=5),  # Run daily at 12:05 AM
    },
    'analyze-task-delays': {
        'task': 'employee_task_system.celery.analyze_task_delays',
        'schedule': crontab(hour=0, minute=10),  # Run daily at 12:10 AM
    },
    'send-overdue-notifications': {
        'task': 'employee_task_system.celery.send_overdue_task_notifications',
        'schedule': crontab(hour=9, minute=0),  # Run daily at 9:00 AM
    },
    'generate-department-analytics': {
        'task': 'employee_task_system.celery.generate_department_analytics',
        'schedule': crontab(hour=23, minute=30),  # Run daily at 11:30 PM
    },
}
