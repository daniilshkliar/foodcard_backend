from rest_framework.permissions import BasePermission
from authentication.models import Manager


SAFE_METHODS = ('GET', 'HEAD', 'OPTIONS')

class IsAdminUserOrReadOnly(BasePermission):
    """
    The request is authenticated as an admin, or is a read-only request.
    """

    def has_permission(self, request, view):
        return bool(
            request.method in SAFE_METHODS or
            request.user and
            request.user.is_staff
        )


class IsAdminUserOrManager(BasePermission):
    """
    The request is authenticated as an admin or manager.
    """

    def has_permission(self, request, view):
        try:
            manager = Manager.objects.get(user=request.user.id)
            is_manager = bool(manager.places)
        except:
            is_manager = False
        
        return bool(
            request.user and
            request.user.is_staff or
            is_manager
        )


class ManagerUpdateOnly(BasePermission):
    """
    The request is authenticated as a manager for update.
    """

    def has_permission(self, request, view):
        PATH = request.META.get('PATH_INFO').split('/')
        try:
            pk = PATH[-2]
            manager = Manager.objects.get(user=request.user.id)
            is_manager = pk in [str(place.id) for place in manager.places]
        except:
            is_manager = False
        
        return bool(
            request.user and
            is_manager and
            PATH[-3]=='update' or 
            PATH[-3]=='upload_image' or
            PATH[-3]=='delete_image'
        )