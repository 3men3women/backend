import requests
from urllib.parse import urlencode

from django.conf import settings
from django.shortcuts import redirect
from django.contrib.auth import get_user_model

from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import RegisterSerializer, LoginSerializer

User = get_user_model()

# ✅ 회원가입 + JWT 발급
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]  # 인증 불필요

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # JWT 토큰 발급
        refresh = RefreshToken.for_user(user)

        return Response({
            "msg": "회원가입 성공",
            "user_id": user.id,
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        }, status=status.HTTP_201_CREATED)


# ✅ 일반 로그인 → JWT 발급
class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]

        refresh = RefreshToken.for_user(user)
        return Response({
            "msg": "로그인 성공",
            "user_id": user.id,
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        }, status=status.HTTP_200_OK)


# ✅ 카카오 로그인 URL
class KakaoLoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        kakao_auth_url = (
            "https://kauth.kakao.com/oauth/authorize"
            f"?client_id={settings.KAKAO_REST_API_KEY}"
            f"&redirect_uri={settings.KAKAO_REDIRECT_URI}"
            f"&response_type=code"
        )
        return redirect(kakao_auth_url)


# ✅ 카카오 로그인 Callback → JWT 발급 후 프론트로 리다이렉트
class KakaoCallbackView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        code = request.GET.get("code")
        if not code:
            return Response({"detail": "code가 없습니다."}, status=400)

        # 1) 인가코드로 토큰 교환
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
        if not access_token:
            return Response({"detail": "카카오 토큰 교환 실패", "raw": token_response}, status=400)

        # 2) 사용자 정보 조회
        profile_url = "https://kapi.kakao.com/v2/user/me"
        headers = {"Authorization": f"Bearer {access_token}"}
        profile_response = requests.get(profile_url, headers=headers).json()

        kakao_id = profile_response.get("id")
        kakao_account = profile_response.get("kakao_account", {}) or {}
        email = kakao_account.get("email") or ""

        # 3) 서비스 사용자 생성/조회
        user, _ = User.objects.get_or_create(
            username=f"kakao_{kakao_id}",
            defaults={"email": email}
        )

        # 4) JWT 발급
        refresh = RefreshToken.for_user(user)
        access_jwt = str(refresh.access_token)
        refresh_jwt = str(refresh)

        # 5) 프론트로 리다이렉트
        params = urlencode({
            "login": "success",
            "user_id": user.id,
            "access": access_jwt,
            "refresh": refresh_jwt,
        })
        return redirect(f"http://localhost:3000/home?{params}")
