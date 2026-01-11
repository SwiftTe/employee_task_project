from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Avg, Sum, Count, F
from django.utils import timezone
from datetime import timedelta, date
from .models import (
    EmployeeProductivity, ProjectAnalytics, DepartmentAnalytics,
    TaskPerformanceReport, EmployeeSkillRating, WorkloadDistribution,
    DelayAnalysis
)
from tasks.models import Task, TimeLog
from .serializers import (
    EmployeeProductivitySerializer, ProjectAnalyticsSerializer,
    DepartmentAnalyticsSerializer, TaskPerformanceReportSerializer,
    EmployeeSkillRatingSerializer, WorkloadDistributionSerializer,
    DelayAnalysisSerializer, AnalyticsSummarySerializer,
    EmployeePerformanceSerializer, ProjectPerformanceSerializer
)
from .throttles import AnalyticsRateThrottle
from users.permissions import CanViewAnalytics, IsManagerOrAdmin


class EmployeeProductivityListView(generics.ListAPIView):
    queryset = EmployeeProductivity.objects.all()
    serializer_class = EmployeeProductivitySerializer
    permission_classes = [CanViewAnalytics]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['user', 'date']
    ordering = ['-date']


class ProjectAnalyticsListView(generics.ListAPIView):
    queryset = ProjectAnalytics.objects.all()
    serializer_class = ProjectAnalyticsSerializer
    permission_classes = [CanViewAnalytics]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['project']


class DepartmentAnalyticsListView(generics.ListAPIView):
    queryset = DepartmentAnalytics.objects.all()
    serializer_class = DepartmentAnalyticsSerializer
    permission_classes = [CanViewAnalytics]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['department']
    ordering = ['-date']


class EmployeeSkillRatingListCreateView(generics.ListCreateAPIView):
    queryset = EmployeeSkillRating.objects.all()
    serializer_class = EmployeeSkillRatingSerializer
    permission_classes = [IsManagerOrAdmin]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['user', 'skill_name']


class WorkloadDistributionListView(generics.ListAPIView):
    queryset = WorkloadDistribution.objects.all()
    serializer_class = WorkloadDistributionSerializer
    permission_classes = [CanViewAnalytics]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['user', 'date']
    ordering = ['-date']


class DelayAnalysisListView(generics.ListAPIView):
    queryset = DelayAnalysis.objects.all()
    serializer_class = DelayAnalysisSerializer
    permission_classes = [CanViewAnalytics]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['task']


@api_view(['GET'])
@permission_classes([CanViewAnalytics])
@throttle_classes([AnalyticsRateThrottle])
def analytics_summary(request):
    """
    Get overall analytics summary for dashboard
    """
    try:
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        # Basic counts
        total_employees = User.objects.filter(is_active_employee=True).count()
        total_tasks = Task.objects.count()
        completed_tasks = Task.objects.filter(status='COMPLETED').count()
        pending_tasks = Task.objects.filter(status__in=['TODO', 'IN_PROGRESS']).count()
        
        # Overdue tasks
        overdue_tasks = Task.objects.filter(
            due_date__lt=timezone.now(),
            status__in=['TODO', 'IN_PROGRESS']
        ).count()
        
        # Average completion time
        completed_tasks_with_time = Task.objects.filter(
            status='COMPLETED',
            completed_at__isnull=False
        )
        
        avg_completion_time = 0
        if completed_tasks_with_time.exists():
            durations = []
            for task in completed_tasks_with_time:
                duration = (task.completed_at - task.created_at).total_seconds() / 3600
                durations.append(duration)
            avg_completion_time = sum(durations) / len(durations)
        
        # Productivity score
        total_hours_logged = TimeLog.objects.aggregate(
            total=Sum('hours')
        )['total'] or 0
        
        productivity_score = 0
        if total_hours_logged > 0:
            productivity_score = round((completed_tasks / total_hours_logged) * 100, 2)
        
        data = {
            'total_employees': total_employees,
            'total_tasks': total_tasks,
            'completed_tasks': completed_tasks,
            'pending_tasks': pending_tasks,
            'overdue_tasks': overdue_tasks,
            'average_completion_time': round(avg_completion_time, 2),
            'productivity_score': productivity_score,
            'total_hours_logged': float(total_hours_logged)
        }
        
        serializer = AnalyticsSummarySerializer(data)
        return Response(serializer.data)
    
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([CanViewAnalytics])
def employee_performance(request):
    """
    Get performance metrics for all employees
    """
    try:
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        employees = User.objects.filter(is_active_employee=True)
        performance_data = []
        
        for employee in employees:
            # Task metrics
            assigned_tasks = Task.objects.filter(assigned_to=employee)
            completed_tasks = assigned_tasks.filter(status='COMPLETED')
            
            tasks_assigned_count = assigned_tasks.count()
            tasks_completed_count = completed_tasks.count()
            
            completion_rate = 0
            if tasks_assigned_count > 0:
                completion_rate = round((tasks_completed_count / tasks_assigned_count) * 100, 2)
            
            # Average task duration
            avg_duration = 0
            if completed_tasks.exists():
                durations = []
                for task in completed_tasks:
                    if task.completed_at:
                        duration = (task.completed_at - task.created_at).total_seconds() / 3600
                        durations.append(duration)
                if durations:
                    avg_duration = sum(durations) / len(durations)
            
            # Hours logged
            total_hours = TimeLog.objects.filter(user=employee).aggregate(
                total=Sum('hours')
            )['total'] or 0
            
            # Efficiency score
            efficiency_score = 0
            if total_hours > 0:
                efficiency_score = round((tasks_completed_count / float(total_hours)) * 100, 2)
            
            performance_data.append({
                'user_id': employee.id,
                'user_name': employee.full_name,
                'department': employee.department or 'N/A',
                'tasks_completed': tasks_completed_count,
                'tasks_assigned': tasks_assigned_count,
                'completion_rate': completion_rate,
                'average_task_duration': round(avg_duration, 2),
                'efficiency_score': efficiency_score,
                'total_hours_logged': float(total_hours)
            })
        
        serializer = EmployeePerformanceSerializer(performance_data, many=True)
        return Response(serializer.data)
    
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([CanViewAnalytics])
def project_performance(request):
    """
    Get performance metrics for all projects
    """
    try:
        projects = Task.objects.values('project').annotate(
            project_name=F('project__name'),
            total_tasks=Count('id'),
            completed_tasks=Count('id', filter=Q(status='COMPLETED')),
            total_estimated_hours=Sum('estimated_hours'),
            total_actual_hours=Sum('actual_hours')
        ).filter(project__isnull=False)
        
        performance_data = []
        
        for project in projects:
            total_tasks = project['total_tasks']
            completed_tasks = project['completed_tasks']
            
            completion_percentage = 0
            if total_tasks > 0:
                completion_percentage = round((completed_tasks / total_tasks) * 100, 2)
            
            estimated_hours = project['total_estimated_hours'] or 0
            actual_hours = project['total_actual_hours'] or 0
            
            efficiency_ratio = 0
            if estimated_hours > 0:
                efficiency_ratio = round(estimated_hours / actual_hours, 2) if actual_hours > 0 else 0
            
            # Average task duration
            avg_duration = 0
            completed_tasks_with_dates = Task.objects.filter(
                project_id=project['project'],
                status='COMPLETED',
                completed_at__isnull=False
            )
            
            if completed_tasks_with_dates.exists():
                durations = []
                for task in completed_tasks_with_dates:
                    duration = (task.completed_at - task.created_at).total_seconds() / 3600
                    durations.append(duration)
                if durations:
                    avg_duration = sum(durations) / len(durations)
            
            performance_data.append({
                'project_id': project['project'],
                'project_name': project['project_name'],
                'total_tasks': total_tasks,
                'completed_tasks': completed_tasks,
                'completion_percentage': completion_percentage,
                'total_estimated_hours': float(estimated_hours),
                'total_actual_hours': float(actual_hours),
                'efficiency_ratio': efficiency_ratio,
                'average_task_duration': round(avg_duration, 2)
            })
        
        serializer = ProjectPerformanceSerializer(performance_data, many=True)
        return Response(serializer.data)
    
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsManagerOrAdmin])
def generate_performance_report(request):
    """
    Generate performance report for a specific period
    """
    try:
        report_type = request.data.get('report_type', 'MONTHLY')
        start_date = request.data.get('start_date')
        end_date = request.data.get('end_date')
        
        if not start_date or not end_date:
            return Response(
                {'error': 'Start date and end date are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create report record
        report = TaskPerformanceReport.objects.create(
            report_type=report_type,
            start_date=start_date,
            end_date=end_date,
            generated_by=request.user
        )
        
        # Generate summary data (simplified for example)
        summary_data = {
            'total_tasks': Task.objects.filter(
                created_at__date__range=[start_date, end_date]
            ).count(),
            'completed_tasks': Task.objects.filter(
                status='COMPLETED',
                completed_at__date__range=[start_date, end_date]
            ).count(),
            'total_hours': TimeLog.objects.filter(
                date__range=[start_date, end_date]
            ).aggregate(total=Sum('hours'))['total'] or 0
        }
        
        report.summary_data = summary_data
        report.is_generated = True
        report.save()
        
        serializer = TaskPerformanceReportSerializer(report)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
