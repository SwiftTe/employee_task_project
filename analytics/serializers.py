from rest_framework import serializers
from .models import (
    EmployeeProductivity, ProjectAnalytics, DepartmentAnalytics,
    TaskPerformanceReport, EmployeeSkillRating, WorkloadDistribution,
    DelayAnalysis
)
from django.contrib.auth import get_user_model

User = get_user_model()


class EmployeeProductivitySerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.full_name', read_only=True)
    user_department = serializers.CharField(source='user.department', read_only=True)

    class Meta:
        model = EmployeeProductivity
        fields = [
            'id', 'user', 'user_name', 'user_department', 'date',
            'tasks_completed', 'tasks_assigned', 'hours_logged',
            'efficiency_score', 'created_at'
        ]
        read_only_fields = ['created_at']


class ProjectAnalyticsSerializer(serializers.ModelSerializer):
    project_name = serializers.CharField(source='project.name', read_only=True)
    
    class Meta:
        model = ProjectAnalytics
        fields = [
            'id', 'project', 'project_name', 'total_tasks', 'completed_tasks',
            'total_hours_estimated', 'total_hours_actual', 'completion_percentage',
            'average_task_duration', 'last_updated'
        ]
        read_only_fields = ['last_updated']


class DepartmentAnalyticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = DepartmentAnalytics
        fields = [
            'id', 'department', 'date', 'total_employees', 'active_tasks',
            'completed_tasks', 'total_hours_logged', 'average_efficiency',
            'created_at'
        ]
        read_only_fields = ['created_at']


class TaskPerformanceReportSerializer(serializers.ModelSerializer):
    generated_by_name = serializers.CharField(source='generated_by.full_name', read_only=True)
    
    class Meta:
        model = TaskPerformanceReport
        fields = [
            'id', 'report_type', 'start_date', 'end_date',
            'generated_by', 'generated_by_name', 'file_path',
            'summary_data', 'is_generated', 'created_at'
        ]
        read_only_fields = ['generated_by', 'created_at']


class EmployeeSkillRatingSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.full_name', read_only=True)
    rated_by_name = serializers.CharField(source='rated_by.full_name', read_only=True)
    
    class Meta:
        model = EmployeeSkillRating
        fields = [
            'id', 'user', 'user_name', 'skill_name', 'rating',
            'rated_by', 'rated_by_name', 'comments', 'created_at', 'updated_at'
        ]
        read_only_fields = ['rated_by', 'created_at', 'updated_at']

    def create(self, validated_data):
        validated_data['rated_by'] = self.context['request'].user
        return super().create(validated_data)


class WorkloadDistributionSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.full_name', read_only=True)
    user_department = serializers.CharField(source='user.department', read_only=True)
    
    class Meta:
        model = WorkloadDistribution
        fields = [
            'id', 'user', 'user_name', 'user_department', 'date',
            'active_tasks_count', 'total_estimated_hours', 'overdue_tasks_count',
            'workload_score', 'created_at'
        ]
        read_only_fields = ['created_at']


class DelayAnalysisSerializer(serializers.ModelSerializer):
    task_title = serializers.CharField(source='task.title', read_only=True)
    assigned_to_name = serializers.CharField(source='task.assigned_to.full_name', read_only=True)
    
    class Meta:
        model = DelayAnalysis
        fields = [
            'id', 'task', 'task_title', 'assigned_to_name',
            'planned_duration', 'actual_duration', 'delay_hours',
            'delay_percentage', 'delay_reason', 'analyzed_at'
        ]
        read_only_fields = ['analyzed_at']


class AnalyticsSummarySerializer(serializers.Serializer):
    """
    Summary serializer for dashboard analytics
    """
    total_employees = serializers.IntegerField()
    total_tasks = serializers.IntegerField()
    completed_tasks = serializers.IntegerField()
    pending_tasks = serializers.IntegerField()
    overdue_tasks = serializers.IntegerField()
    average_completion_time = serializers.FloatField()
    productivity_score = serializers.FloatField()
    total_hours_logged = serializers.FloatField()


class EmployeePerformanceSerializer(serializers.Serializer):
    """
    Employee performance metrics
    """
    user_id = serializers.IntegerField()
    user_name = serializers.CharField()
    department = serializers.CharField()
    tasks_completed = serializers.IntegerField()
    tasks_assigned = serializers.IntegerField()
    completion_rate = serializers.FloatField()
    average_task_duration = serializers.FloatField()
    efficiency_score = serializers.FloatField()
    total_hours_logged = serializers.FloatField()


class ProjectPerformanceSerializer(serializers.Serializer):
    """
    Project performance metrics
    """
    project_id = serializers.IntegerField()
    project_name = serializers.CharField()
    total_tasks = serializers.IntegerField()
    completed_tasks = serializers.IntegerField()
    completion_percentage = serializers.FloatField()
    total_estimated_hours = serializers.FloatField()
    total_actual_hours = serializers.FloatField()
    efficiency_ratio = serializers.FloatField()
    average_task_duration = serializers.FloatField()
