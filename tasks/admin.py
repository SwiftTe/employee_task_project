from django.contrib import admin
from .models import Project, Task, TaskComment, TaskAttachment, TaskHistory, TimeLog


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_by', 'start_date', 'end_date', 'is_active', 'task_count')
    list_filter = ('is_active', 'start_date', 'created_at')
    search_fields = ('name', 'description', 'created_by__username')
    readonly_fields = ('created_at', 'updated_at')
    
    def task_count(self, obj):
        return obj.tasks.count()
    task_count.short_description = 'Tasks'


class TaskCommentInline(admin.TabularInline):
    model = TaskComment
    extra = 1
    readonly_fields = ('created_at', 'updated_at')


class TaskAttachmentInline(admin.TabularInline):
    model = TaskAttachment
    extra = 1
    readonly_fields = ('uploaded_at', 'file_size')


class TimeLogInline(admin.TabularInline):
    model = TimeLog
    extra = 1
    readonly_fields = ('created_at',)


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'project', 'assigned_to', 'created_by', 'priority', 'status', 'due_date', 'created_at')
    list_filter = ('status', 'priority', 'project', 'created_at', 'due_date')
    search_fields = ('title', 'description', 'assigned_to__username', 'created_by__username')
    readonly_fields = ('created_at', 'updated_at', 'completed_at')
    inlines = [TaskCommentInline, TaskAttachmentInline, TimeLogInline]
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('title', 'description', 'project')
        }),
        ('Assignment', {
            'fields': ('assigned_to', 'created_by')
        }),
        ('Details', {
            'fields': ('priority', 'status', 'estimated_hours', 'actual_hours', 'due_date')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'completed_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(TaskComment)
class TaskCommentAdmin(admin.ModelAdmin):
    list_display = ('task', 'author', 'content_preview', 'created_at')
    list_filter = ('created_at', 'task__project')
    search_fields = ('content', 'author__username', 'task__title')
    readonly_fields = ('created_at', 'updated_at')
    
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content'


@admin.register(TaskAttachment)
class TaskAttachmentAdmin(admin.ModelAdmin):
    list_display = ('task', 'uploaded_by', 'filename', 'file_size', 'uploaded_at')
    list_filter = ('uploaded_at', 'task__project')
    search_fields = ('filename', 'uploaded_by__username', 'task__title')
    readonly_fields = ('uploaded_at', 'file_size')


@admin.register(TaskHistory)
class TaskHistoryAdmin(admin.ModelAdmin):
    list_display = ('task', 'user', 'action', 'description', 'timestamp')
    list_filter = ('action', 'timestamp', 'task__project')
    search_fields = ('description', 'user__username', 'task__title')
    readonly_fields = ('timestamp',)
    ordering = ('-timestamp',)


@admin.register(TimeLog)
class TimeLogAdmin(admin.ModelAdmin):
    list_display = ('task', 'user', 'hours', 'date', 'created_at')
    list_filter = ('date', 'created_at', 'task__project')
    search_fields = ('description', 'user__username', 'task__title')
    readonly_fields = ('created_at',)
