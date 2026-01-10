from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Only admin users can edit, others can read
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_authenticated and request.user.role == 'ADMIN'


class IsManagerOrAdmin(permissions.BasePermission):
    """
    Only managers or admins can access
    """
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.role in ['MANAGER', 'ADMIN']
        )


class IsOwnerOrManagerOrAdmin(permissions.BasePermission):
    """
    Users can access their own data, managers and admins can access all
    """
    def has_object_permission(self, request, view, obj):
        if request.user.role in ['MANAGER', 'ADMIN']:
            return True
        
        if hasattr(obj, 'user'):
            return obj.user == request.user
        elif hasattr(obj, 'assigned_to'):
            return obj.assigned_to == request.user
        elif hasattr(obj, 'created_by'):
            return obj.created_by == request.user
        
        return False


class IsEmployeeOrHigher(permissions.BasePermission):
    """
    Only authenticated employees, managers, or admins
    """
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.role in ['EMPLOYEE', 'MANAGER', 'ADMIN']
        )


class CanAssignTasks(permissions.BasePermission):
    """
    Only managers and admins can assign tasks
    """
    def has_permission(self, request, view):
        if request.method in ['POST', 'PUT', 'PATCH']:
            return (
                request.user and 
                request.user.is_authenticated and 
                request.user.role in ['MANAGER', 'ADMIN']
            )
        return request.user and request.user.is_authenticated


class CanViewAnalytics(permissions.BasePermission):
    """
    Only managers and admins can view analytics
    """
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.role in ['MANAGER', 'ADMIN']
        )


class IsTaskAssigneeOrCreator(permissions.BasePermission):
    """
    Only task assignee or creator can modify task
    """
    def has_object_permission(self, request, view, obj):
        if request.user.role in ['MANAGER', 'ADMIN']:
            return True
        
        return (
            obj.assigned_to == request.user or 
            obj.created_by == request.user
        )
