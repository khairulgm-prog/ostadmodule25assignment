from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import (
    RegisterView, ForgotPasswordView, ResetPasswordView, 
    ProfileView, DashboardSummaryView, DoctorViewSet, 
    AppointmentViewSet, BillViewSet
)

router = DefaultRouter()
router.register(r'doctors', DoctorViewSet, basename='doctor')
router.register(r'appointments', AppointmentViewSet, basename='appointment')
router.register(r'bills', BillViewSet, basename='bill')

urlpatterns = [
    # Auth Endpoints
    path('register/', RegisterView.as_view(), name='auth_register'),
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot_password'),
    path('reset-password/', ResetPasswordView.as_view(), name='reset_password'),
    
    # Profile & Systems Endpoints
    path('profile/', ProfileView.as_view(), name='user_profile'),
    path('dashboard/', DashboardSummaryView.as_view(), name='dashboard_summary'),
    
    # Router inclusions
    path('', include(router.urls)),
]
