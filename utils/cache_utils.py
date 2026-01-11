from django.core.cache import cache
from django.conf import settings


def get_cached_user_profile(user_id):
    """Get user profile from cache"""
    cache_key = f'user_profile_{user_id}'
    return cache.get(cache_key)


def set_cached_user_profile(user_id, profile_data):
    """Set user profile in cache"""
    cache_key = f'user_profile_{user_id}'
    cache.set(cache_key, profile_data, settings.CACHE_TIMEOUTS['user_profile'])


def get_cached_task_list(user_id, filters=None):
    """Get cached task list for user"""
    cache_key = f'task_list_{user_id}_{hash(str(filters))}'
    return cache.get(cache_key)


def set_cached_task_list(user_id, filters, task_data):
    """Set task list in cache"""
    cache_key = f'task_list_{user_id}_{hash(str(filters))}'
    cache.set(cache_key, task_data, settings.CACHE_TIMEOUTS['task_list'])


def get_cached_analytics(key):
    """Get analytics data from cache"""
    cache_key = f'analytics_{key}'
    return cache.get(cache_key)


def set_cached_analytics(key, data):
    """Set analytics data in cache"""
    cache_key = f'analytics_{key}'
    cache.set(cache_key, data, settings.CACHE_TIMEOUTS['analytics'], using='analytics')


def get_cached_project_data(project_id):
    """Get project data from cache"""
    cache_key = f'project_data_{project_id}'
    return cache.get(cache_key)


def set_cached_project_data(project_id, data):
    """Set project data in cache"""
    cache_key = f'project_data_{project_id}'
    cache.set(cache_key, data, settings.CACHE_TIMEOUTS['project_data'])


def invalidate_user_cache(user_id):
    """Invalidate all cache entries for a user"""
    patterns = [
        f'user_profile_{user_id}',
        f'task_list_{user_id}_*',
    ]
    for pattern in patterns:
        cache.delete_many(cache.keys(pattern))


def invalidate_project_cache(project_id):
    """Invalidate project cache"""
    cache_key = f'project_data_{project_id}'
    cache.delete(cache_key)


def invalidate_analytics_cache(key=None):
    """Invalidate analytics cache"""
    if key:
        cache_key = f'analytics_{key}'
        cache.delete(cache_key, using='analytics')
    else:
        # Clear all analytics cache
        cache.clear(using='analytics')
