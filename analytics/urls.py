from django.urls import path
from . import views

urlpatterns = [
    # Analytics Summary
    path('summary/', views.analytics_summary, name='analytics-summary'),
    
    # Performance Metrics
    path('employee-performance/', views.employee_performance, name='employee-performance'),
    path('project-performance/', views.project_performance, name='project-performance'),
    
    # Model-based Analytics
    path('productivity/', views.EmployeeProductivityListView.as_view(), name='employee-productivity-list'),
    path('project-analytics/', views.ProjectAnalyticsListView.as_view(), name='project-analytics-list'),
    path('department-analytics/', views.DepartmentAnalyticsListView.as_view(), name='department-analytics-list'),
    path('skill-ratings/', views.EmployeeSkillRatingListCreateView.as_view(), name='skill-rating-list-create'),
    path('workload/', views.WorkloadDistributionListView.as_view(), name='workload-distribution-list'),
    path('delays/', views.DelayAnalysisListView.as_view(), name='delay-analysis-list'),
    
    # Reports
    path('generate-report/', views.generate_performance_report, name='generate-performance-report'),
]
