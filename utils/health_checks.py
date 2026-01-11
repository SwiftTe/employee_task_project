import logging
from django.conf import settings
from django.http import JsonResponse
from django.views import View
from django.core.cache import cache
from django.db import connection
from django.contrib.auth import get_user_model
from django.utils import timezone
from tasks.models import Task
import redis

User = get_user_model()
logger = logging.getLogger(__name__)


class HealthCheckView(View):
    """System health check endpoint"""
    
    def get(self, request):
        try:
            health_status = {
                'status': 'healthy',
                'timestamp': timezone.now().isoformat(),
                'checks': {}
            }
            
            # Database check
            try:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT 1")
                health_status['checks']['database'] = {
                    'status': 'healthy',
                    'message': 'Database connection successful'
                }
            except Exception as e:
                health_status['checks']['database'] = {
                    'status': 'unhealthy',
                    'message': f'Database connection failed: {str(e)}'
                }
                health_status['status'] = 'unhealthy'
            
            # Redis check
            try:
                redis_client = redis.from_url(settings.CELERY_BROKER_URL)
                redis_client.ping()
                health_status['checks']['redis'] = {
                    'status': 'healthy',
                    'message': 'Redis connection successful'
                }
            except Exception as e:
                health_status['checks']['redis'] = {
                    'status': 'unhealthy',
                    'message': f'Redis connection failed: {str(e)}'
                }
                health_status['status'] = 'unhealthy'
            
            # Cache check
            try:
                cache.set('health_check', 'ok', 10)
                cache_result = cache.get('health_check')
                if cache_result == 'ok':
                    health_status['checks']['cache'] = {
                        'status': 'healthy',
                        'message': 'Cache working correctly'
                    }
                else:
                    raise Exception('Cache read/write failed')
            except Exception as e:
                health_status['checks']['cache'] = {
                    'status': 'unhealthy',
                    'message': f'Cache check failed: {str(e)}'
                }
                health_status['status'] = 'unhealthy'
            
            # Basic application checks
            try:
                user_count = User.objects.count()
                task_count = Task.objects.count()
                health_status['checks']['application'] = {
                    'status': 'healthy',
                    'message': f'Application running - Users: {user_count}, Tasks: {task_count}'
                }
            except Exception as e:
                health_status['checks']['application'] = {
                    'status': 'unhealthy',
                    'message': f'Application check failed: {str(e)}'
                }
                health_status['status'] = 'unhealthy'
            
            status_code = 200 if health_status['status'] == 'healthy' else 503
            
            return JsonResponse(health_status, status=status_code)
            
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return JsonResponse({
                'status': 'unhealthy',
                'error': str(e)
            }, status=503)


class DetailedHealthView(View):
    """Detailed system information for monitoring"""
    
    def get(self, request):
        try:
            from django.utils import timezone
            
            detailed_info = {
                'application': {
                    'name': 'Employee Task Management System',
                    'version': '1.0.0',
                    'environment': getattr(settings, 'ENVIRONMENT', 'unknown'),
                    'debug_mode': settings.DEBUG,
                    'timezone': settings.TIME_ZONE,
                },
                'database': {
                    'engine': settings.DATABASES['default']['ENGINE'],
                    'name': settings.DATABASES['default']['NAME'],
                    'host': settings.DATABASES['default']['HOST'],
                    'port': settings.DATABASES['default']['PORT'],
                },
                'cache': {
                    'backend': settings.CACHES['default']['BACKEND'],
                    'location': settings.CACHES['default']['LOCATION'],
                },
                'celery': {
                    'broker_url': settings.CELERY_BROKER_URL,
                    'result_backend': settings.CELERY_RESULT_BACKEND,
                },
                'statistics': {
                    'total_users': User.objects.count(),
                    'active_employees': User.objects.filter(is_active_employee=True).count(),
                    'total_tasks': Task.objects.count(),
                    'completed_tasks': Task.objects.filter(status='COMPLETED').count(),
                    'pending_tasks': Task.objects.filter(status__in=['TODO', 'IN_PROGRESS']).count(),
                },
                'timestamp': timezone.now().isoformat(),
            }
            
            return JsonResponse(detailed_info)
            
        except Exception as e:
            logger.error(f"Detailed health check failed: {str(e)}")
            return JsonResponse({
                'error': str(e),
                'status': 'unhealthy'
            }, status=500)
