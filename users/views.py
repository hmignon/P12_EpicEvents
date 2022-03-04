from rest_framework import generics, permissions

from .serializers import UpdatePasswordSerializer


class UpdatePassword(generics.UpdateAPIView):
    http_method_names = ['put', 'options']
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = UpdatePasswordSerializer

    def get_object(self):
        return self.request.user
