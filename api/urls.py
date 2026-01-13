from django.urls import path, include

urlpatterns = [
    path('v1/auth/', include('users.urls_v1')),
    path('v1/tasks/', include('tasks.urls_v1')),
    path('v1/analytics/', include('analytics.urls_v1')),
]
