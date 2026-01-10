from rest_framework import routers
from django.urls import path, include
from .views import (
    ProjectListCreateView, ProjectDetailView,
    TaskListCreateView, TaskDetailView, assign_task, update_task_status,
    TaskCommentListCreateView, TaskCommentDetailView,
    TaskAttachmentListCreateView, TaskAttachmentDetailView,
    TaskHistoryListView, TimeLogListCreateView, TimeLogDetailView
)

router = routers.DefaultRouter()
# Add any viewsets here

app_name = 'tasks'

urlpatterns = [
    # Project URLs
    path('projects/', ProjectListCreateView.as_view(), name='project-list-create'),
    path('projects/<int:pk>/', ProjectDetailView.as_view(), name='project-detail'),
    
    # Task URLs
    path('', TaskListCreateView.as_view(), name='task-list-create'),
    path('<int:pk>/', TaskDetailView.as_view(), name='task-detail'),
    path('<int:task_id>/assign/', assign_task, name='task-assign'),
    path('<int:task_id>/update-status/', update_task_status, name='task-update-status'),
    
    # Task Comments URLs
    path('<int:task_id>/comments/', TaskCommentListCreateView.as_view(), name='task-comment-list-create'),
    path('comments/<int:pk>/', TaskCommentDetailView.as_view(), name='task-comment-detail'),
    
    # Task Attachments URLs
    path('<int:task_id>/attachments/', TaskAttachmentListCreateView.as_view(), name='task-attachment-list-create'),
    path('attachments/<int:pk>/', TaskAttachmentDetailView.as_view(), name='task-attachment-detail'),
    
    # Task History URLs
    path('<int:task_id>/history/', TaskHistoryListView.as_view(), name='task-history-list'),
    
    # Time Log URLs
    path('<int:task_id>/time-logs/', TimeLogListCreateView.as_view(), name='timelog-list-create'),
    path('time-logs/<int:pk>/', TimeLogDetailView.as_view(), name='timelog-detail'),
]
