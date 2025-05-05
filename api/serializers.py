from .models import *
from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from rest_framework.exceptions import AuthenticationFailed



class HospitalRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)  # Hide password field from response

    class Meta:
        model = Hospital
        fields = ['id','hospital_name', 'email',  'password']

    def create(self, validated_data):
        password = validated_data.pop('password')
        hospital = Hospital.objects.create(**validated_data)
        hospital.set_password(password)  # Set and hash the password
        hospital.save()
        return hospital
    
class HospitalAdditionalInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hospital
        fields = '__all__'  # Or explicitly list fields that can be updated

   
class HospitalLoginSerializer(serializers.Serializer):
    email = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        if email and password:
            user = authenticate(email=email, password=password)

            if user:
                if not user.is_active:
                    raise serializers.ValidationError("User account is disabled.")
                return user
            else:
                raise serializers.ValidationError("Unable to log in with provided credentials.")
        else:
            raise serializers.ValidationError("Must include 'email' and 'password'.")
        
        
class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)  # Hide password field from response

    class Meta:
        model = User
        fields = ['username', 'email', 'password'] 
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user
    
    
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']


User = get_user_model()

class UserLoginSerializer(serializers.Serializer):
    email = serializers.CharField(max_length=255)
    password = serializers.CharField(
        label="Password",
        style={'input_type': 'password'},
        trim_whitespace=False,
        write_only=True
    )

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = authenticate(email=email, password=password)

            if not user:
                msg = 'Unable to log in with provided credentials.'
                raise serializers.ValidationError(msg, code='authorization')

        else:
            msg = 'Must include "email" and "password".'
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user
        return attrs

class HospitalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hospital
        fields = '__all__'
class HospitalSerializers(serializers.ModelSerializer):
    class Meta:
        model = Hospital
        fields = [
            'hospital_name', 
            'email', 
            'phone_number', 
            'address', 
            'city', 
            'district', 
            'pin_code', 
            'is_approved', 
            'license_number',
            'license_expiry_date', 
            'accreditations', 
            'admin_contact_person', 
            'admin_contact_phone', 
            'appointment_limit'
            # Exclude 'photo' and 'owner_photo' if you don't want them in the response
        ]
# class DepartmentSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Department
#         fields = '__all__'
class DepartmentSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(use_url=True)  # Ensure the URL of the image is included
    
    class Meta:
        model = Department
        fields = ['id', 'name', 'image','hospital'] 

# class DoctorSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Doctor  
#         fields =  '__all__'

# class BookingSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Booking
#         fields = '__all__'
class DoctorSerializerHospital(serializers.ModelSerializer):
    class Meta:
        model = Doctor
        fields = '__all__'
    
    image = serializers.ImageField(required=False)  # Make image optional
class DoctorSerializer(serializers.ModelSerializer):
    department_id = serializers.CharField(source='department.id', read_only=True)
    department = serializers.CharField(source='department.name', read_only=True)
    hospital = serializers.CharField(source='department.hospital.hospital_name', read_only=True)
    hospital_id = serializers.CharField(source='department.hospital.id', read_only=True)
    district = serializers.CharField(source='department.hospital.district', read_only=True)
    district_id = serializers.IntegerField(source='department.hospital.district.id', read_only=True)
    image = serializers.SerializerMethodField()  # Image URL

    class Meta:
        model = Doctor
        fields = [
            'id', 'name', 'department_id', 'department',
            'hospital', 'hospital_id', 'district', 'district_id',
            'experience', 'image', 'available_days'
        ]

    def get_image(self, obj):
        request = self.context.get('request')
        return request.build_absolute_uri(obj.image.url) if obj.image and request else None

class BookingSerializer(serializers.ModelSerializer):
    hospital = serializers.CharField(source='hospital.hospital_name', read_only=True)
    department = serializers.CharField(source='department.name', read_only=True)
    doctor = serializers.CharField(source='doctor.name', read_only=True)
    patient_name = serializers.CharField(source='patient.username', read_only=True)  # Add this line
    patient_email = serializers.CharField(source='patient.email', read_only=True)    # Add this line

    class Meta:
        model = Booking
        fields = '__all__'

class PremiumHospitalSerializer(serializers.ModelSerializer):
    class Meta:
        model = PremiumHospital
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'profile_img']        

class FeedbackSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source='user.username', read_only=True)  # Get the patient's username
    class Meta:
        model = Feedback
        fields = '__all__'  # Or specify fields explicitly like ['id', 'message', 'created_at', 'patient_name', 'hospital']


class HospitalPremiumSerializer(serializers.ModelSerializer):
    hospital = HospitalSerializer()  # Use nested serializer

    class Meta:
        model = PremiumHospital
        fields = ['hospital', 'subscription_status', 'premium_fee', 'paid_date']