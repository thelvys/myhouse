from django.urls import path
from .views import (
    LandingPageView,
    SignUpView,
    CustomLoginView,
    ProfileView,
    CustomPasswordResetView,
    CustomPasswordResetDoneView,
    CustomPasswordResetConfirmView,
    CustomPasswordResetCompleteView,
    CustomPasswordChangeView,
    Custom404View,
    Custom500View,
    custom_logout
)

app_name = 'accounts'

urlpatterns = [
    path('', LandingPageView.as_view(), name='landing'),
    path('signup/', SignUpView.as_view(), name='signup'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', custom_logout, name='logout'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('password_reset/', CustomPasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', CustomPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', CustomPasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('password_change/', CustomPasswordChangeView.as_view(), name='password_change'),
    path('password_change/done/', CustomPasswordChangeView.as_view(), name='password_change_done'),
]

# Ces handlers doivent être ajoutés au urls.py du projet principal
handler404 = Custom404View.as_view()
handler500 = Custom500View.as_view()