
from rest_framework import serializers
from django.utils import timezone
from .models import CustomUser, Doctor, Appointment, Bill

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'password', 'full_name', 'phone_number', 'address']

    def create(self, validated_data):
        validated_data['role'] = 'Patient'
        return CustomUser.objects.create_user(**validated_data)

class ProfileSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(read_only=True) # Lock unique baseline identifying parameters

    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'full_name', 'phone_number', 'address', 'role']
        read_only_fields = ['role']

class DoctorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Doctor
        fields = '__all__'

    def validate_visiting_fee(self, value):
        if value < 0:
            raise serializers.ValidationError("Visiting fee cannot be negative.")
        return value

class AppointmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = '__all__'
        read_only_fields = ['patient']

    def validate_appointment_date(self, value):
        if value < timezone.now().date():
            raise serializers.ValidationError("Appointment date cannot be in the past.")
        return value

class BillSerializer(serializers.ModelSerializer):
    total_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Bill
        fields = '__all__'

    def validate(self, data):
        consultation_fee = data.get('consultation_fee')
        discount = data.get('discount', 0)
        if discount > consultation_fee:
            raise serializers.ValidationError({"discount": "Discount cannot be greater than consultation fee."})
        return data

class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

class PasswordResetConfirmSerializer(serializers.Serializer):
    email = serializers.EmailField()
    new_password = serializers.CharField(write_only=True)
