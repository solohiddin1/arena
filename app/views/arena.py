from rest_framework import ApiView, statuss
from rest_framework.response import Response
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated
from app.models import Arena
from app.serializers_f.arena_serializer import ArenaSerializer
from rest_framework import status


class ArenaCreateView(ApiView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if request.user.is_authenticated:
            serializer = ArenaSerializer(data=request.data)
            if serializer.is_valid():
                arena = serializer.save()
                return Response(ArenaSerializer(arena).data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)


class ArenaListView(ApiView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            owner = request.user
            arena = Arena.objects.filter(owner=owner)
            serializer = ArenaSerializer(arena, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            arena = Arena.objects.get(pk=pk)
            serializer = ArenaSerializer(arena)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Arena.DoesNotExist:
            return Response({"error": "Arena not found"}, status=status.HTTP_404_NOT_FOUND)
    
    def put(self, request, pk):
        try:
            arena = Arena.objects.get(pk=pk)
            serializer = ArenaSerializer(arena, data=request.data, partial=True)
            if serializer.is_valid():
                arena = serializer.save()
                return Response(ArenaSerializer(arena).data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Arena.DoesNotExist:
            return Response({"error": "Arena not found"}, status=status.HTTP_404_NOT_FOUND)
    
    def delete(self, request, pk):
        try:
            arena = Arena.objects.get(pk=pk)
            arena.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Arena.DoesNotExist:
            return Response({"error": "Arena not found"}, status=status.HTTP_404_NOT_FOUND)