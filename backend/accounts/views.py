from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.contrib.auth import get_user_model, authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import RegisterSerializer
from .models import PatientProfile, DoctorProfile

User = get_user_model()


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()

        if user.role == 'patient':
            PatientProfile.objects.create(
                user=user,
                date_of_birth     = request.data.get('dob') or None,
                blood_group       = request.data.get('blood_group', ''),
                height            = request.data.get('height') or None,
                weight            = request.data.get('weight') or None,
                city              = request.data.get('city', ''),
                state             = request.data.get('state', ''),
                allergies         = request.data.get('allergies', ''),
                chronic_condition = request.data.get('chronic', ''),
            )
        elif user.role == 'doctor':
            DoctorProfile.objects.create(
                user           = user,
                specialty      = request.data.get('specialty', ''),
                license_number = request.data.get('license_number', ''),
                hospital       = request.data.get('hospital', ''),
            )

        refresh = RefreshToken.for_user(user)
        return Response({
            'message':    'Account created!',
            'access':     str(refresh.access_token),
            'refresh':    str(refresh),
            'role':       user.role,
            'first_name': user.first_name,
            'last_name':  user.last_name,
            'email':      user.email,
            'phone':      user.phone,
        }, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    email    = request.data.get('email', '').strip()
    password = request.data.get('password', '')

    # authenticate EMAIL se karta hai kyunki USERNAME_FIELD = 'email'
    user = authenticate(request, username=email, password=password)

    if user is not None:
        refresh = RefreshToken.for_user(user)
        return Response({
            'access':     str(refresh.access_token),
            'refresh':    str(refresh),
            'role':       user.role,
            'first_name': user.first_name,
            'last_name':  user.last_name,
            'email':      user.email,
            'phone':      user.phone,
        })

    try:
        User.objects.get(email=email)
        return Response({'error': 'Wrong password'}, status=400)
    except User.DoesNotExist:
        return Response({'error': 'No account found with this email'}, status=404)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def me(request):
    user = request.user
    data = {
        'email':      user.email,
        'first_name': user.first_name,
        'last_name':  user.last_name,
        'phone':      user.phone,
        'role':       user.role,
    }

    if user.role == 'patient':
        try:
            p = PatientProfile.objects.get(user=user)
            data.update({
                'dob':               str(p.date_of_birth) if p.date_of_birth else '',
                'blood_group':       p.blood_group       or '',
                'height':            str(p.height)       if p.height else '',
                'weight':            str(p.weight)       if p.weight else '',
                'city':              p.city              or '',
                'state':             p.state             or '',
                'allergies':         p.allergies         or '',
                'chronic_condition': p.chronic_condition or '',
            })
        except PatientProfile.DoesNotExist:
            pass

    elif user.role == 'doctor':
        try:
            d = DoctorProfile.objects.get(user=user)
            data.update({
                'specialty':      d.specialty      or '',
                'license_number': d.license_number or '',
                'hospital':       d.hospital       or '',
                'is_verified':    d.is_verified,
            })
        except DoctorProfile.DoesNotExist:
            pass

    return Response(data)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_patient_profile(request):
    try:
        profile = PatientProfile.objects.get(user=request.user)

        h = request.data.get('height', '')
        w = request.data.get('weight', '')
        if h: profile.height = float(h)
        if w: profile.weight = float(w)

        profile.city              = request.data.get('city',              profile.city)
        profile.state             = request.data.get('state',             profile.state)
        profile.allergies         = request.data.get('allergies',         profile.allergies)
        profile.chronic_condition = request.data.get('chronic_condition', profile.chronic_condition)
        profile.save()

        return Response({'message': 'Profile updated!'})
    except PatientProfile.DoesNotExist:
        return Response({'error': 'Profile not found'}, status=404)