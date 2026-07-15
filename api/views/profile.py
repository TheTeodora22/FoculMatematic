from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.forms import ProfileEditForm
from accounts.utils import get_or_create_profile
from api.serializers import ProfileSerializer


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        profile = get_or_create_profile(request.user)
        return Response(ProfileSerializer(profile).data)

    def patch(self, request):
        profile = get_or_create_profile(request.user)
        form = ProfileEditForm(request.data, instance=profile, user=request.user)
        if not form.is_valid():
            return Response(form.errors, status=400)
        form.save()
        return Response(ProfileSerializer(profile).data)
