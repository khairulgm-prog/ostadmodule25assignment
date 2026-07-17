from django.shortcuts import render
from rest_framework import generics, permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from .models import CustomUser, Doctor, Appointment, Bill
from .serializers import (
    RegisterSerializer, ProfileSerializer, DoctorSerializer, 
    AppointmentSerializer, BillSerializer, PasswordResetRequestSerializer, 
    PasswordResetConfirmSerializer
)
from .permissions import IsAdminOrReadOnly, AppointmentPermission, BillPermission




# Create your views here.

# --- Auth Architecture ---
class RegisterView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

class ForgotPasswordView(APIView):
    permission_classes = [permissions.AllowAny]
    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # Mock logic handling: In production hooks pass notification engine token items here
        return Response({"message": "Password reset link sent to your email."}, status=status.HTTP_200_OK)

class ResetPasswordView(APIView):
    permission_classes = [permissions.AllowAny]
    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            user = CustomUser.objects.get(email=serializer.validated_data['email'])
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return Response({"message": "Password has been reset successfully."}, status=status.HTTP_200_OK)
        except CustomUser.DoesNotExist:
            return Response({"error": "User with this email does not exist."}, status=status.HTTP_404_NOT_FOUND)

# --- Profile Engine ---
class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

# --- Model ViewSets (Doctor, Appointment, Bill) ---
class DoctorViewSet(viewsets.ModelViewSet):
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['department']
    search_fields = ['name']
    ordering_fields = ['visiting_fee']

class AppointmentViewSet(viewsets.ModelViewSet):
    serializer_class = AppointmentSerializer
    permission_classes = [AppointmentPermission]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'doctor']
    search_fields = ['patient__full_name', 'doctor__name']
    ordering_fields = ['appointment_date']

    def get_queryset(self):
        user = self.request.user
        if user.role == 'Admin':
            return Appointment.objects.all()
        elif user.role == 'Doctor':
            return Appointment.objects.filter(doctor__user=user)
        return Appointment.objects.filter(patient=user)

    def perform_create(self, serializer):
        appointment = serializer.save(patient=self.request.user)

    def perform_update(self, serializer):
        instance = serializer.save()
        # Automate Billing Creation if Status hits "Completed"
        if instance.status == 'Completed' and not Bill.objects.filter(appointment=instance).exists():
            Bill.objects.create(
                patient=instance.patient,
                doctor=instance.doctor,
                appointment=instance,
                consultation_fee=instance.doctor.visiting_fee,
                discount=0.00
            )

class BillViewSet(viewsets.ModelViewSet):
    serializer_class = BillSerializer
    permission_classes = [BillPermission]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'Admin':
            return Bill.objects.all()
        elif user.role == 'Doctor':
            return Bill.objects.filter(doctor__user=user)
        return Bill.objects.filter(patient=user)

# --- Aggregate Metrics Dashboard ---
class DashboardSummaryView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response({
            "Total Patients": CustomUser.objects.filter(role='Patient').count(),
            "Total Doctors": Doctor.objects.count(),
            "Total Appointments": Appointment.objects.count(),
            "Pending Appointments": Appointment.objects.filter(status='Pending').count(),
            "Completed Appointments": Appointment.objects.filter(status='Completed').count(),
        }, status=status.HTTP_200_OK)
