from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.utils import timezone
from .models import Task, TaskHistory, TimeLog
from analytics.models import EmployeeProductivity, ProjectAnalytics, DelayAnalysis
from .celery import send_task_notification_email


@receiver(pre_save, sender=Task)
def task_pre_save(sender, instance, **kwargs):
    """Track task changes before saving"""
    if instance.pk:
        try:
            old_instance = Task.objects.get(pk=instance.pk)
            instance._old_status = old_instance.status
            instance._old_assigned_to = old_instance.assigned_to
        except Task.DoesNotExist:
            pass


@receiver(post_save, sender=Task)
def task_post_save(sender, instance, created, **kwargs):
    """Handle task creation and updates"""
    if created:
        # Create history for new task
        TaskHistory.objects.create(
            task=instance,
            user=instance.created_by,
            action='CREATED',
            description=f"Task '{instance.title}' was created"
        )
        
        # Send notification to assigned user
        if instance.assigned_to and instance.assigned_to != instance.created_by:
            send_task_notification_email.delay(
                instance.assigned_to.id,
                instance.title,
                f"You have been assigned a new task: {instance.title}\n\nDescription: {instance.description}\n\nPriority: {instance.priority}"
            )
    else:
        # Check for status change
        old_status = getattr(instance, '_old_status', None)
        if old_status and old_status != instance.status:
            TaskHistory.objects.create(
                task=instance,
                user=getattr(instance, '_updated_by', instance.assigned_to or instance.created_by),
                action='STATUS_CHANGED',
                old_value=old_status,
                new_value=instance.status,
                description=f"Task status changed from {old_status} to {instance.status}"
            )
            
            # Send notification for status change
            if instance.assigned_to:
                send_task_notification_email.delay(
                    instance.assigned_to.id,
                    instance.title,
                    f"Task '{instance.title}' status updated to {instance.status}"
                )
        
        # Check for assignment change
        old_assigned_to = getattr(instance, '_old_assigned_to', None)
        if old_assigned_to != instance.assigned_to:
            TaskHistory.objects.create(
                task=instance,
                user=getattr(instance, '_updated_by', instance.created_by),
                action='ASSIGNED',
                new_value=f"Assigned to {instance.assigned_to.full_name if instance.assigned_to else 'Unassigned'}",
                description=f"Task reassigned from {old_assigned_to.full_name if old_assigned_to else 'Unassigned'} to {instance.assigned_to.full_name if instance.assigned_to else 'Unassigned'}"
            )
            
            # Send notification to new assignee
            if instance.assigned_to and instance.assigned_to != old_assigned_to:
                send_task_notification_email.delay(
                    instance.assigned_to.id,
                    instance.title,
                    f"You have been assigned to task: {instance.title}\n\nDescription: {instance.description}"
                )
    
    # Update project analytics if task has project
    if instance.project:
        update_project_analytics.delay(instance.project.id)


@receiver(post_save, sender=TimeLog)
def timelog_post_save(sender, instance, created, **kwargs):
    """Update productivity metrics when time is logged"""
    if created and instance.user:
        # Trigger daily productivity update
        from .celery import generate_daily_productivity_report
        generate_daily_productivity_report.delay()


@receiver(post_delete, sender=Task)
def task_post_delete(sender, instance, **kwargs):
    """Handle task deletion"""
    TaskHistory.objects.create(
        task=instance,
        user=getattr(instance, '_deleted_by', None),
        action='UPDATED',
        description=f"Task '{instance.title}' was deleted"
    )


@receiver(post_save, sender=DelayAnalysis)
def delay_analysis_post_save(sender, instance, created, **kwargs):
    """Handle delay analysis completion"""
    if created and instance.delay_hours > 0:
        # Send notification about significant delays
        if instance.delay_percentage > 50:  # More than 50% delay
            if instance.task.assigned_to:
                send_task_notification_email.delay(
                    instance.task.assigned_to.id,
                    instance.task.title,
                    f"Task '{instance.task.title}' has a significant delay of {instance.delay_hours:.1f} hours ({instance.delay_percentage:.1f}%). Please review and update the timeline."
                )


# Import Celery tasks to avoid circular imports
from .celery import update_project_analytics
