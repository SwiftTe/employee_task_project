from django.contrib import admin
from .models import (
    EmployeeProductivity, ProjectAnalytics, DepartmentAnalytics,
    TaskPerformanceReport, EmployeeSkillRating, WorkloadDistribution,
    DelayAnalysis
)


@admin.register(EmployeeProductivity)
class EmployeeProductivityAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'tasks_completed', 'tasks_assigned', 'hours_logged', 'efficiency_score')
    list_filter = ('date', 'user__department', 'user__role')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('created_at',)
    ordering = ('-date', 'user__username')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


@admin.register(ProjectAnalytics)
class ProjectAnalyticsAdmin(admin.ModelAdmin):
    list_display = ('project', 'total_tasks', 'completed_tasks', 'completion_percentage', 'last_updated')
    list_filter = ('last_updated',)
    search_fields = ('project__name', 'project__description')
    readonly_fields = ('last_updated',)
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('project')


@admin.register(DepartmentAnalytics)
class DepartmentAnalyticsAdmin(admin.ModelAdmin):
    list_display = ('department', 'date', 'total_employees', 'active_tasks', 'completed_tasks', 'average_efficiency')
    list_filter = ('department', 'date')
    search_fields = ('department',)
    readonly_fields = ('created_at',)
    ordering = ('-date', 'department')


@admin.register(TaskPerformanceReport)
class TaskPerformanceReportAdmin(admin.ModelAdmin):
    list_display = ('report_type', 'start_date', 'end_date', 'generated_by', 'is_generated', 'created_at')
    list_filter = ('report_type', 'is_generated', 'created_at')
    search_fields = ('generated_by__username', 'generated_by__email')
    readonly_fields = ('created_at', 'generated_by')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('generated_by')


@admin.register(EmployeeSkillRating)
class EmployeeSkillRatingAdmin(admin.ModelAdmin):
    list_display = ('user', 'skill_name', 'rating', 'rated_by', 'created_at')
    list_filter = ('skill_name', 'rating', 'created_at')
    search_fields = ('user__username', 'skill_name', 'rated_by__username')
    readonly_fields = ('created_at', 'updated_at')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'rated_by')


@admin.register(WorkloadDistribution)
class WorkloadDistributionAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'active_tasks_count', 'total_estimated_hours', 'overdue_tasks_count', 'workload_score')
    list_filter = ('date', 'user__department', 'user__role')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('created_at',)
    ordering = ('-date', 'user__username')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


@admin.register(DelayAnalysis)
class DelayAnalysisAdmin(admin.ModelAdmin):
    list_display = ('task', 'delay_hours', 'delay_percentage', 'analyzed_at')
    list_filter = ('analyzed_at',)
    search_fields = ('task__title', 'task__assigned_to__username')
    readonly_fields = ('analyzed_at',)
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('task', 'task__assigned_to')
