from django.urls import path
from . import views

urlpatterns = [
    # Project URLs
    path('projects/', views.ProjectListCreateView.as_view(), name='project-list-create'),
    path('projects/<int:pk>/', views.ProjectDetailView.as_view(), name='project-detail'),
    
    # Task URLs
    path('', views.TaskListCreateView.as_view(), name='task-list-create'),
    path('<int:pk>/', views.TaskDetailView.as_view(), name='task-detail'),
    path('<int:task_id>/assign/', views.assign_task, name='task-assign'),
    path('<int:task_id>/update-status/', views.update_task_status, name='task-update-status'),
    
    # Task Comments URLs
    path('<int:task_id>/comments/', views.TaskCommentListCreateView.as_view(), name='task-comment-list-create'),
    path('comments/<int:pk>/', views.TaskCommentDetailView.as_view(), name='task-comment-detail'),
    
    # Task Attachments URLs
    path('<int:task_id>/attachments/', views.TaskAttachmentListCreateView.as_view(), name='task-attachment-list-create'),
    path('attachments/<int:pk>/', views.TaskAttachmentDetailView.as_view(), name='task-attachment-detail'),
    
    # Task History URLs
    path('<int:task_id>/history/', views.TaskHistoryListView.as_view(), name='task-history-list'),
    
    # Time Log URLs
    path('<int:task_id>/time-logs/', views.TimeLogListCreateView.as_view(), name='timelog-list-create'),
    path('time-logs/<int:pk>/', views.TimeLogDetailView.as_view(), name='timelog-detail'),
]
