from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.hashers import make_password, check_password
from utils.mongo_documents import UserProfile

@api_view(["POST"])
def register_user(request):
    email = request.data.get("email", "").strip().lower()
    full_name = request.data.get("name", "").strip()
    password = request.data.get("password", "")

    if not email or not full_name or not password:
        return Response({"error": "All fields are required."}, status=status.HTTP_400_BAD_REQUEST)

    existing = UserProfile.objects(email=email).first()
    if existing:
        return Response({"error": "Email already exists."}, status=status.HTTP_409_CONFLICT)

    user = UserProfile(
        email=email,
        full_name=full_name,
        profile={"password_hash": make_password(password)}
    )
    user.save()

    return Response({
        "status": "success",
        "user": {
            "email": user.email,
            "full_name": user.full_name
        }
    })

@api_view(["POST"])
def login_user(request):
    email = request.data.get("email", "").strip().lower()
    password = request.data.get("password", "")

    if not email or not password:
        return Response({"error": "Email and password are required."}, status=status.HTTP_400_BAD_REQUEST)

    user = UserProfile.objects(email=email).first()
    if not user:
        return Response({"error": "Invalid credentials."}, status=status.HTTP_401_UNAUTHORIZED)

    hashed = user.profile.get("password_hash")
    if not hashed or not check_password(password, hashed):
        return Response({"error": "Invalid credentials."}, status=status.HTTP_401_UNAUTHORIZED)

    return Response({
        "status": "success",
        "user": {
            "email": user.email,
            "full_name": user.full_name
        }
    })
