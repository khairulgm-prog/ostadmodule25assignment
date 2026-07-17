from rest_framework import permissions

class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated and request.user.role == 'Admin'

class AppointmentPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        if request.user.role == 'Admin':
            return True
        if request.method == 'POST' and request.user.role == 'Patient':
            return True
        if request.method in permissions.SAFE_METHODS:
            return True
        return True

    def has_object_permission(self, request, view, obj):
        if request.user.role == 'Admin':
            return True
        if request.user.role == 'Patient':
            return obj.patient == request.user
        if request.user.role == 'Doctor':
            return obj.doctor.user == request.user or (obj.doctor == request.user)
        return False

class BillPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.user.role == 'Admin':
            return True
        if request.user.role == 'Patient':
            return obj.patient == request.user
        if request.user.role == 'Doctor':
            return obj.doctor.user == request.user
        return False
