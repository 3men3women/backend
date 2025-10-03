from rest_framework import generics, permissions
from rest_framework.response import Response
from .models import Profile
from .serializers import ProfileSerializer

class ProfileDetailView(generics.RetrieveUpdateAPIView):
    """
    현재 로그인한 유저의 프로필을 가져오거나 수정
    """
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        # ✅ Profile이 없으면 자동 생성
        profile, created = Profile.objects.get_or_create(user=self.request.user)
        return profile

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        # ✅ username도 같이 반환 (MainPage.jsx에서 쓰려고)
        data = serializer.data
        data["username"] = request.user.username
        data["email"] = request.user.email
        return Response(data)
