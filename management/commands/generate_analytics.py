from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from tasks.models import Task
from analytics.models import EmployeeProductivity, ProjectAnalytics
from datetime import datetime, timedelta
from django.db.models import Sum, Count, Avg

User = get_user_model()


class Command(BaseCommand):
    help = 'Generate analytics data for existing tasks and users'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='Number of days to generate analytics for',
        )

    def handle(self, *args, **options):
        days = options['days']
        self.stdout.write(self.style.SUCCESS(f'Generating analytics for the last {days} days...'))
        
        # Generate employee productivity data
        self.generate_employee_productivity(days)
        
        # Generate project analytics
        self.generate_project_analytics()
        
        self.stdout.write(self.style.SUCCESS('Analytics generation completed!'))

    def generate_employee_productivity(self, days):
        users = User.objects.filter(is_active_employee=True)
        
        for user in users:
            for day_offset in range(days):
                date = datetime.now().date() - timedelta(days=day_offset)
                
                # Calculate metrics for this day
                tasks_completed = Task.objects.filter(
                    assigned_to=user,
                    status='COMPLETED',
                    completed_at__date=date
                ).count()
                
                tasks_assigned = Task.objects.filter(
                    assigned_to=user,
                    created_at__date=date
                ).count()
                
                # Get time logs for this day
                from tasks.models import TimeLog
                hours_logged = TimeLog.objects.filter(
                    user=user,
                    date=date
                ).aggregate(total=Sum('hours'))['total'] or 0
                
                # Calculate efficiency score
                efficiency_score = 0
                if hours_logged > 0:
                    efficiency_score = round((tasks_completed / float(hours_logged)) * 100, 2)
                
                # Create or update productivity record
                EmployeeProductivity.objects.update_or_create(
                    user=user,
                    date=date,
                    defaults={
                        'tasks_completed': tasks_completed,
                        'tasks_assigned': tasks_assigned,
                        'hours_logged': hours_logged,
                        'efficiency_score': efficiency_score
                    }
                )
        
        self.stdout.write(self.style.SUCCESS(f'Generated productivity data for {users.count()} users'))

    def generate_project_analytics(self):
        from tasks.models import Project
        projects = Project.objects.all()
        
        for project in projects:
            analytics, created = ProjectAnalytics.objects.get_or_create(
                project=project
            )
            analytics.update_metrics()
        
        self.stdout.write(self.style.SUCCESS(f'Generated analytics for {projects.count()} projects'))
