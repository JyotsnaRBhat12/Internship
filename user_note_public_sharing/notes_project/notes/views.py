from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Note, SharedLink
from .serializers import NoteSerializer, ShareLinkCreateSerializer
import uuid
from django.utils import timezone


@api_view(['POST'])
def create_note(request):

    try:

        serializer = NoteSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()

            return Response({
                "message": "Note created successfully",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)

        return Response({
            "error": "Invalid data",
            "details": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:

        return Response({
            "error": "Something went wrong",
            "details": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
@api_view(['POST'])
def generate_share_link(request, note_id):

    try:

        note = Note.objects.get(id=note_id)

        expiry_serializer = ShareLinkCreateSerializer(data=request.data)
        if not expiry_serializer.is_valid():
            return Response({
                "error": "Invalid data",
                "details": expiry_serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        expiry = expiry_serializer.validated_data.get("expiry_date")

        share = SharedLink.objects.create(
            note=note,
            token=uuid.uuid4(),
            expiry_date=expiry
        )

        link = request.build_absolute_uri(f"/api/share/{share.token}/")

        return Response({
            "message": "Share link created",
            "share_link": link
        }, status=status.HTTP_201_CREATED)

    except Note.DoesNotExist:

        return Response({
            "error": "Note not found"
        }, status=status.HTTP_404_NOT_FOUND)

    except Exception as e:

        return Response({
            "error": "Something went wrong",
            "details": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
@api_view(['GET'])
def access_shared_note(request, token):

    try:

        link = SharedLink.objects.get(token=token)

        if link.expiry_date and timezone.now() > link.expiry_date:
            return Response({
                "error": "This link has expired"
            }, status=status.HTTP_410_GONE)

        link.access_count += 1
        link.save()

        note = link.note

        return Response({
            "title": note.title,
            "content": note.content,
            "access_count": link.access_count
        }, status=status.HTTP_200_OK)

    except SharedLink.DoesNotExist:

        return Response({
            "error": "Invalid share link"
        }, status=status.HTTP_404_NOT_FOUND)
