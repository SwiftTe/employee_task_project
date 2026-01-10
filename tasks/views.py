from rest_framework import generics, permissions, filters, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Avg, Sum, Count, F
from django.utils import timezone
from datetime import timedelta, date
from .models import Project, Task, TaskComment, TaskAttachment, TaskHistory, TimeLog
from .serializers import (
    ProjectSerializer, TaskSerializer, TaskCreateSerializer,
    TaskUpdateSerializer, TaskDetailSerializer, TaskCommentSerializer,
    TaskAttachmentSerializer, TaskHistorySerializer, TimeLogSerializer
)
from .throttles import UploadRateThrottle
from users.permissions import (
    IsEmployeeOrHigher, IsManagerOrAdmin, CanAssignTasks,
    IsTaskAssigneeOrCreator, IsOwnerOrManagerOrAdmin
)


class ProjectListCreateView(generics.ListCreateAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [IsManagerOrAdmin]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active']
    search_fields = ['name', 'description']
    ordering_fields = ['created_at', 'name', 'start_date', 'end_date']

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class ProjectDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [IsManagerOrAdmin]


class TaskListCreateView(generics.ListCreateAPIView):
    queryset = Task.objects.all()
    permission_classes = [IsEmployeeOrHigher]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'priority', 'assigned_to', 'project']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'due_date', 'priority', 'status']

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return TaskCreateSerializer
        return TaskSerializer

    def get_queryset(self):
        user = self.request.user
        if user.role in ['MANAGER', 'ADMIN']:
            return Task.objects.all()
        else:
            return Task.objects.filter(
                Q(assigned_to=user) | Q(created_by=user)
            ).distinct()


class TaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Task.objects.all()
    permission_classes = [IsEmployeeOrHigher, IsTaskAssigneeOrCreator]

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return TaskUpdateSerializer
        return TaskDetailSerializer


class TaskCommentListCreateView(generics.ListCreateAPIView):
    serializer_class = TaskCommentSerializer
    permission_classes = [IsEmployeeOrHigher]

    def get_queryset(self):
        task_id = self.kwargs['task_id']
        return TaskComment.objects.filter(task_id=task_id)


class TaskCommentDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = TaskComment.objects.all()
    serializer_class = TaskCommentSerializer
    permission_classes = [IsOwnerOrManagerOrAdmin]


class TaskAttachmentListCreateView(generics.ListCreateAPIView):
    serializer_class = TaskAttachmentSerializer
    permission_classes = [IsEmployeeOrHigher]
    throttle_classes = [UploadRateThrottle]

    def get_queryset(self):
        task_id = self.kwargs['task_id']
        return TaskAttachment.objects.filter(task_id=task_id)


class TaskAttachmentDetailView(generics.RetrieveDestroyAPIView):
    queryset = TaskAttachment.objects.all()
    serializer_class = TaskAttachmentSerializer
    permission_classes = [IsOwnerOrManagerOrAdmin]


class TaskHistoryListView(generics.ListAPIView):
    serializer_class = TaskHistorySerializer
    permission_classes = [IsEmployeeOrHigher]

    def get_queryset(self):
        task_id = self.kwargs['task_id']
        return TaskHistory.objects.filter(task_id=task_id).order_by('-timestamp')


class TimeLogListCreateView(generics.ListCreateAPIView):
    serializer_class = TimeLogSerializer
    permission_classes = [IsEmployeeOrHigher]

    def get_queryset(self):
        task_id = self.kwargs['task_id']
        return TimeLog.objects.filter(task_id=task_id).order_by('-date')


class TimeLogDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = TimeLog.objects.all()
    serializer_class = TimeLogSerializer
    permission_classes = [IsOwnerOrManagerOrAdmin]


@api_view(['POST'])
@permission_classes([IsEmployeeOrHigher])
def assign_task(request, task_id):
    try:
        task = Task.objects.get(id=task_id)
        
        if request.user.role not in ['MANAGER', 'ADMIN'] and task.created_by != request.user:
            return Response(
                {"error": "You don't have permission to assign this task"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        user_id = request.data.get('assigned_to')
        if user_id:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            assigned_user = User.objects.get(id=user_id)
            task.assigned_to = assigned_user
            
            # Create history record
            TaskHistory.objects.create(
                task=task,
                user=request.user,
                action='ASSIGNED',
                new_value=f"Assigned to {assigned_user.full_name}",
                description=f"Task assigned to {assigned_user.full_name}"
            )
            
            task.save()
            return Response({"message": "Task assigned successfully"})
        
        return Response({"error": "User ID is required"}, status=status.HTTP_400_BAD_REQUEST)
    
    except Task.DoesNotExist:
        return Response({"error": "Task not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsEmployeeOrHigher])
def update_task_status(request, task_id):
    try:
        task = Task.objects.get(id=task_id)
        
        if (request.user.role not in ['MANAGER', 'ADMIN'] and 
            task.assigned_to != request.user and 
            task.created_by != request.user):
            return Response(
                {"error": "You don't have permission to update this task"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        new_status = request.data.get('status')
        if new_status not in dict(Task.STATUS_CHOICES):
            return Response({"error": "Invalid status"}, status=status.HTTP_400_BAD_REQUEST)
        
        old_status = task.status
        task.status = new_status
        task.save()
        
        # Create history record
        TaskHistory.objects.create(
            task=task,
            user=request.user,
            action='STATUS_CHANGED',
            old_value=old_status,
            new_value=new_status,
            description=f"Status changed from {old_status} to {new_status}"
        )
        
        return Response({"message": "Task status updated successfully"})
    
    except Task.DoesNotExist:
        return Response({"error": "Task not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
