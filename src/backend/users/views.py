import requests
from django.conf import settings
from django.shortcuts import redirect
from django.contrib.auth import get_user_model
from rest_framework import generics, status
from rest_framework.response import Response
from .serializers import RegisterSerializer, LoginSerializer
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

# 회원가입
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer


# 일반 로그인 → JWT 발급
class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]  # LoginSerializer에서 user 반환하도록 해야 함

        refresh = RefreshToken.for_user(user)
        return Response({
            "msg": "로그인 성공",
            "user_id": user.id,
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        }, status=status.HTTP_200_OK)


# 카카오 로그인 URL
class KakaoLoginView(APIView):
    def get(self, request):
        kakao_auth_url = (
            "https://kauth.kakao.com/oauth/authorize"
            f"?client_id={settings.KAKAO_REST_API_KEY}"
            f"&redirect_uri={settings.KAKAO_REDIRECT_URI}"
            f"&response_type=code"
        )
        return redirect(kakao_auth_url)


# 카카오 로그인 Callback → JWT 발급
class KakaoCallbackView(APIView):
    def get(self, request):
        code = request.GET.get("code")
        token_url = "https://kauth.kakao.com/oauth/token"
        data = {
            "grant_type": "authorization_code",
            "client_id": settings.KAKAO_REST_API_KEY,
            "redirect_uri": settings.KAKAO_REDIRECT_URI,
            "code": code,
            "client_secret": settings.KAKAO_CLIENT_SECRET,
        }

        token_response = requests.post(token_url, data=data).json()
        access_token = token_response.get("access_token")

        # 사용자 정보 가져오기
        profile_url = "https://kapi.kakao.com/v2/user/me"
        headers = {"Authorization": f"Bearer {access_token}"}
        profile_response = requests.get(profile_url, headers=headers).json()

        kakao_id = profile_response.get("id")
        kakao_account = profile_response.get("kakao_account", {})
        email = kakao_account.get("email")

        # User 생성 or 조회
        user, created = User.objects.get_or_create(
            username=f"kakao_{kakao_id}",
            defaults={"email": email if email else ""}
        )

        # ✅ JWT 발급
        refresh = RefreshToken.for_user(user)
        return Response({
            "msg": "카카오 로그인 성공",
            "user_id": user.id,
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        }, status=status.HTTP_200_OK)
