from django.urls import path, include
from .views import (
    analytics_summary, employee_performance, project_performance,
    EmployeeProductivityListView, ProjectAnalyticsListView,
    DepartmentAnalyticsListView, EmployeeSkillRatingListCreateView,
    WorkloadDistributionListView, DelayAnalysisListView,
    generate_performance_report
)

app_name = 'analytics'

urlpatterns = [
    # Analytics Summary
    path('summary/', analytics_summary, name='analytics-summary'),
    path('employee-performance/', employee_performance, name='employee-performance'),
    path('project-performance/', project_performance, name='project-performance'),
    
    # Model-based Analytics
    path('productivity/', EmployeeProductivityListView.as_view(), name='employee-productivity-list'),
    path('project-analytics/', ProjectAnalyticsListView.as_view(), name='project-analytics-list'),
    path('department-analytics/', DepartmentAnalyticsListView.as_view(), name='department-analytics-list'),
    path('skill-ratings/', EmployeeSkillRatingListCreateView.as_view(), name='skill-rating-list-create'),
    path('workload/', WorkloadDistributionListView.as_view(), name='workload-distribution-list'),
    path('delays/', DelayAnalysisListView.as_view(), name='delay-analysis-list'),
    
    # Reports
    path('generate-report/', generate_performance_report, name='generate-performance-report'),
]
