from rest_framework.permissions import BasePermission


class IsObjectOwner(BasePermission):
    # detail = False, only has permission
    # detail = True, both has permission and has object permission

    message = "You do not have permission to access this object"

    def has_permission(self, request, view):
        return True

    def has_object_permission(self, request, view, obj):
        return request.user == obj.user