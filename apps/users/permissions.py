from rest_framework import permissions


#Esta clase permite que el administrador pueda realizar todas las acciones
#Mientras que un usuario comun solo puede realziar GET y PUT
class IsAdminOrSameUser(permissions.BasePermission):

    def has_permission(self, request, view):
        # check if the request is for a single object
        if 'pk' in view.kwargs:
            return True
        return request.user.is_staff

    def has_object_permission(self, request, view, obj):
        #Si es administrador puede realizar todas las accciones
        if request.user.is_staff:
            return True;
        #Si no es administrador no puede eliminarse el mismo
        if request.method == 'DELETE':
            return False
        return obj == request.user
