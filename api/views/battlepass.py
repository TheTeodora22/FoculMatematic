from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from api.serializers import BattlePassSerializer


class BattlePassView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = BattlePassSerializer(request.user)
        return Response(
            {
                "season": serializer.get_season(request.user),
                "profile_level": serializer.get_profile_level(request.user),
                "tiers": serializer.get_tiers(request.user),
            }
        )
