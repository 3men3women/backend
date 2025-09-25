# users/urls.py
from django.urls import path
from .views import RegisterView, LoginView,KakaoLoginView, KakaoCallbackView

urlpatterns = [
    path("register/", RegisterView.as_view()),
    path("login/", LoginView.as_view()),
    path("kakao/login/", KakaoLoginView.as_view()),      # 카카오 로그인 요청
    path("kakao/callback/", KakaoCallbackView.as_view()), # 카카오 Redirect URI
]