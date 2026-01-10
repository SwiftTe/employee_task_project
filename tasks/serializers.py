from rest_framework import serializers
from django.db import models
from .models import Project, Task, TaskComment, TaskAttachment, TaskHistory, TimeLog
from django.contrib.auth import get_user_model

User = get_user_model()


class ProjectSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.full_name', read_only=True)
    task_count = serializers.SerializerMethodField()
    completion_percentage = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = [
            'id', 'name', 'description', 'start_date', 'end_date',
            'is_active', 'created_by', 'created_by_name', 'task_count',
            'completion_percentage', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_by', 'created_at', 'updated_at']

    def get_task_count(self, obj):
        return obj.tasks.count()

    def get_completion_percentage(self, obj):
        total = obj.tasks.count()
        if total == 0:
            return 0
        completed = obj.tasks.filter(status='COMPLETED').count()
        return round((completed / total) * 100, 2)


class TaskSerializer(serializers.ModelSerializer):
    assigned_to_name = serializers.CharField(source='assigned_to.full_name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.full_name', read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True)
    comments_count = serializers.SerializerMethodField()
    attachments_count = serializers.SerializerMethodField()
    time_logs_total = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'project', 'project_name',
            'assigned_to', 'assigned_to_name', 'created_by', 'created_by_name',
            'priority', 'status', 'estimated_hours', 'actual_hours',
            'due_date', 'completed_at', 'comments_count', 'attachments_count',
            'time_logs_total', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_by', 'completed_at', 'created_at', 'updated_at']

    def get_comments_count(self, obj):
        return obj.comments.count()

    def get_attachments_count(self, obj):
        return obj.attachments.count()

    def get_time_logs_total(self, obj):
        return obj.time_logs.aggregate(
            total=models.Sum('hours')
        )['total'] or 0


class TaskCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = [
            'title', 'description', 'project', 'assigned_to',
            'priority', 'estimated_hours', 'due_date'
        ]

    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class TaskUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = [
            'title', 'description', 'project', 'assigned_to',
            'priority', 'status', 'estimated_hours', 'actual_hours', 'due_date'
        ]


class TaskCommentSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.full_name', read_only=True)

    class Meta:
        model = TaskComment
        fields = [
            'id', 'task', 'author', 'author_name', 'content',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['author', 'created_at', 'updated_at']

    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)


class TaskAttachmentSerializer(serializers.ModelSerializer):
    uploaded_by_name = serializers.CharField(source='uploaded_by.full_name', read_only=True)

    class Meta:
        model = TaskAttachment
        fields = [
            'id', 'task', 'uploaded_by', 'uploaded_by_name',
            'file', 'filename', 'file_size', 'uploaded_at'
        ]
        read_only_fields = ['uploaded_by', 'filename', 'file_size', 'uploaded_at']

    def create(self, validated_data):
        validated_data['uploaded_by'] = self.context['request'].user
        file = validated_data['file']
        validated_data['filename'] = file.name
        validated_data['file_size'] = file.size
        return super().create(validated_data)


class TaskHistorySerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.full_name', read_only=True)

    class Meta:
        model = TaskHistory
        fields = [
            'id', 'task', 'user', 'user_name', 'action',
            'old_value', 'new_value', 'description', 'timestamp'
        ]
        read_only_fields = ['user', 'timestamp']


class TimeLogSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.full_name', read_only=True)
    task_title = serializers.CharField(source='task.title', read_only=True)

    class Meta:
        model = TimeLog
        fields = [
            'id', 'task', 'task_title', 'user', 'user_name',
            'hours', 'description', 'date', 'created_at'
        ]
        read_only_fields = ['user', 'created_at']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class TaskDetailSerializer(TaskSerializer):
    comments = TaskCommentSerializer(many=True, read_only=True)
    attachments = TaskAttachmentSerializer(many=True, read_only=True)
    history = TaskHistorySerializer(many=True, read_only=True)
    time_logs = TimeLogSerializer(many=True, read_only=True)

    class Meta(TaskSerializer.Meta):
        fields = TaskSerializer.Meta.fields + [
            'comments', 'attachments', 'history', 'time_logs'
        ]
