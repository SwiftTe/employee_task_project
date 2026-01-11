from django.db import models
from django.contrib.auth import get_user_model
from django.db.models import Sum, Avg, Count
from datetime import datetime, timedelta

User = get_user_model()


class EmployeeProductivity(models.Model):
    """
    Daily productivity metrics for employees
    """
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='productivity_metrics'
    )
    date = models.DateField()
    tasks_completed = models.PositiveIntegerField(default=0)
    tasks_assigned = models.PositiveIntegerField(default=0)
    hours_logged = models.DecimalField(
        max_digits=6, 
        decimal_places=2, 
        default=0
    )
    efficiency_score = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=0
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'date']
        ordering = ['-date']

    def __str__(self):
        return f"{self.user.username} - {self.date} - Score: {self.efficiency_score}"


class ProjectAnalytics(models.Model):
    """
    Analytics for projects
    """
    project = models.OneToOneField(
        'tasks.Project', 
        on_delete=models.CASCADE, 
        related_name='analytics'
    )
    total_tasks = models.PositiveIntegerField(default=0)
    completed_tasks = models.PositiveIntegerField(default=0)
    total_hours_estimated = models.DecimalField(
        max_digits=8, 
        decimal_places=2, 
        default=0
    )
    total_hours_actual = models.DecimalField(
        max_digits=8, 
        decimal_places=2, 
        default=0
    )
    completion_percentage = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=0
    )
    average_task_duration = models.DecimalField(
        max_digits=6, 
        decimal_places=2, 
        default=0
    )
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Analytics for {self.project.name}"

    def update_metrics(self):
        from tasks.models import Task
        tasks = Task.objects.filter(project=self.project)
        self.total_tasks = tasks.count()
        self.completed_tasks = tasks.filter(status='COMPLETED').count()
        
        if self.total_tasks > 0:
            self.completion_percentage = (self.completed_tasks / self.total_tasks) * 100
        
        self.total_hours_estimated = tasks.aggregate(
            total=Sum('estimated_hours')
        )['total'] or 0
        
        self.total_hours_actual = tasks.aggregate(
            total=Sum('actual_hours')
        )['total'] or 0
        
        completed_tasks_with_dates = tasks.filter(
            status='COMPLETED', 
            completed_at__isnull=False
        )
        
        if completed_tasks_with_dates.exists():
            durations = []
            for task in completed_tasks_with_dates:
                duration = (task.completed_at - task.created_at).total_seconds() / 3600
                durations.append(duration)
            self.average_task_duration = sum(durations) / len(durations)
        
        self.save()


class DepartmentAnalytics(models.Model):
    """
    Analytics for departments
    """
    department = models.CharField(max_length=100)
    date = models.DateField()
    total_employees = models.PositiveIntegerField(default=0)
    active_tasks = models.PositiveIntegerField(default=0)
    completed_tasks = models.PositiveIntegerField(default=0)
    total_hours_logged = models.DecimalField(
        max_digits=8, 
        decimal_places=2, 
        default=0
    )
    average_efficiency = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=0
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['department', 'date']
        ordering = ['-date']

    def __str__(self):
        return f"{self.department} - {self.date}"


class TaskPerformanceReport(models.Model):
    """
    Generated performance reports
    """
    REPORT_TYPES = (
        ('DAILY', 'Daily'),
        ('WEEKLY', 'Weekly'),
        ('MONTHLY', 'Monthly'),
        ('QUARTERLY', 'Quarterly'),
        ('YEARLY', 'Yearly'),
    )

    report_type = models.CharField(max_length=10, choices=REPORT_TYPES)
    start_date = models.DateField()
    end_date = models.DateField()
    generated_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True
    )
    file_path = models.CharField(max_length=255, blank=True, null=True)
    summary_data = models.JSONField(default=dict)
    is_generated = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_report_type_display()} Report - {self.start_date} to {self.end_date}"


class EmployeeSkillRating(models.Model):
    """
    Track employee skills and ratings
    """
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='skill_ratings'
    )
    skill_name = models.CharField(max_length=100)
    rating = models.IntegerField(
        choices=[(i, i) for i in range(1, 6)],
        help_text="Rating from 1 to 5"
    )
    rated_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='given_ratings'
    )
    comments = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['user', 'skill_name', 'rated_by']

    def __str__(self):
        return f"{self.user.username} - {self.skill_name} - {self.rating}"


class WorkloadDistribution(models.Model):
    """
    Track workload distribution across employees
    """
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='workload_metrics'
    )
    date = models.DateField()
    active_tasks_count = models.PositiveIntegerField(default=0)
    total_estimated_hours = models.DecimalField(
        max_digits=6, 
        decimal_places=2, 
        default=0
    )
    overdue_tasks_count = models.PositiveIntegerField(default=0)
    workload_score = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=0
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'date']
        ordering = ['-date']

    def __str__(self):
        return f"{self.user.username} - {self.date} - Workload: {self.workload_score}"


class DelayAnalysis(models.Model):
    """
    Analyze task delays and patterns
    """
    task = models.OneToOneField(
        'tasks.Task', 
        on_delete=models.CASCADE, 
        related_name='delay_analysis'
    )
    planned_duration = models.DecimalField(
        max_digits=6, 
        decimal_places=2, 
        null=True, 
        blank=True
    )
    actual_duration = models.DecimalField(
        max_digits=6, 
        decimal_places=2, 
        null=True, 
        blank=True
    )
    delay_hours = models.DecimalField(
        max_digits=6, 
        decimal_places=2, 
        default=0
    )
    delay_percentage = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=0
    )
    delay_reason = models.TextField(blank=True, null=True)
    analyzed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Delay Analysis for {self.task.title}"

    def calculate_delay(self):
        if self.task.due_date and self.task.completed_at:
            self.actual_duration = (
                self.task.completed_at - self.task.created_at
            ).total_seconds() / 3600
            
            planned_duration = (
                self.task.due_date - self.task.created_at
            ).total_seconds() / 3600
            self.planned_duration = planned_duration
            
            if planned_duration > 0:
                self.delay_hours = max(0, self.actual_duration - planned_duration)
                self.delay_percentage = (self.delay_hours / planned_duration) * 100
        
        self.save()
