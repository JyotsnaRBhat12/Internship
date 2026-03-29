from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from datetime import timedelta
import uuid
import random
from .models import Note, SharedLink, UserOTP, LoginAttempt


@api_view(['POST'])
def create_note(request):
    try:
        if not request.user.is_authenticated:
            return Response({"error": "Authentication required"}, status=401)

        title = request.data.get('title')
        content = request.data.get('content')

        if not title or not content:
            return Response({"error": "Title and content are required"})

        note = Note.objects.create(user=request.user, title=title, content=content)

        return Response({
            "message": "Note created successfully",
            "note_id": note.id
        })

    except Exception as e:
        return Response({"error": str(e)})


@api_view(['POST'])
def share_note(request):
    try:
        if not request.user.is_authenticated:
            return Response({"error": "Authentication required"}, status=401)

        note_id = request.data.get('note_id')
        expiry_date = request.data.get('expiry_date')

        if not note_id:
            return Response({"error": "Note ID required"})

        try:
            note = Note.objects.get(id=note_id)
        except Note.DoesNotExist:
            return Response({"error": "Note not found"})

        if note.user != request.user:
            return Response({"error": "Not allowed to share this note"}, status=403)

        parsed_expiry = None
        if expiry_date:
            parsed_expiry = parse_datetime(expiry_date)
            if parsed_expiry is None:
                return Response({"error": "Invalid expiry_date format"}, status=400)

        link = SharedLink.objects.create(note=note, expiry_date=parsed_expiry)

        share_url = f"http://127.0.0.1:8000/api/public/{link.token}/"

        return Response({"share_link": share_url})

    except Exception:
        return Response({"error": "Something went wrong"})


@api_view(['GET'])
def public_note(request, token):
    try:
        try:
            link = SharedLink.objects.select_related('note').get(token=token)
        except SharedLink.DoesNotExist:
            return Response({"error": "Invalid link"})

        if link.expiry_date and timezone.now() > link.expiry_date:
            return Response({"error": "Link expired"})

        link.access_count += 1
        link.save()

        return Response({
            "title": link.note.title,
            "content": link.note.content,
            "access_count": link.access_count
        })

    except Exception:
        return Response({"error": "Something went wrong"})


@api_view(['POST'])
def login_user(request):
    try:
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            return Response({"error": "Username and password are required"})

        existing_user = User.objects.filter(username=username).first()
        if existing_user:
            attempt, _ = LoginAttempt.objects.get_or_create(user=existing_user)
            if attempt.is_locked:
                return Response({"error": "Account locked due to multiple failed attempts"})

        user = authenticate(username=username, password=password)

        if user is None:
            if existing_user:
                attempt, _ = LoginAttempt.objects.get_or_create(user=existing_user)
                attempt.attempt_count += 1
                if attempt.attempt_count >= 5:
                    attempt.is_locked = True
                attempt.save()

            return Response({"error": "Invalid credentials"})

        attempt, _ = LoginAttempt.objects.get_or_create(user=user)

        if attempt.is_locked:
            return Response({"error": "Account locked due to multiple failed attempts"})

        attempt.attempt_count = 0
        attempt.is_locked = False
        attempt.save()

        otp = str(random.randint(100000, 999999))
        UserOTP.objects.filter(user=user).delete()
        UserOTP.objects.create(user=user, otp=otp)

        try:
            send_mail(
                'Your OTP',
                f'Your OTP is {otp}',
                settings.EMAIL_HOST_USER,
                [user.email],
                fail_silently=False
            )
        except Exception:
            return Response({"error": "Email sending failed"})

        return Response({"message": "OTP sent to email"})

    except Exception:
        return Response({"error": "Something went wrong"})


@api_view(['POST'])
def verify_otp(request):
    try:
        username = request.data.get('username')
        otp = request.data.get('otp')

        if not username or not otp:
            return Response({"error": "Invalid request"})

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response({"error": "Invalid request"})

        attempt, _ = LoginAttempt.objects.get_or_create(user=user)

        if attempt.is_locked:
            return Response({"error": "Account locked due to multiple failed attempts"})

        otp_obj = UserOTP.objects.filter(user=user).order_by('-created_at').first()

        if not otp_obj:
            return Response({"error": "Invalid or expired OTP"})

        if (
            timezone.now() > otp_obj.created_at + timedelta(minutes=5)
            or otp_obj.otp != otp
        ):
            attempt.attempt_count += 1

            if attempt.attempt_count >= 5:
                attempt.is_locked = True

            attempt.save()

            return Response({"error": "Invalid or expired OTP"})

        otp_obj.is_verified = True
        otp_obj.save()

        attempt.attempt_count = 0
        attempt.is_locked = False
        attempt.save()

        login(request, user)
        return Response({"message": "Login successful"})

    except Exception:
        return Response({"error": "Something went wrong"})

@api_view(['GET'])
def admin_only(request):
    return Response({"message": "Welcome Admin"})
