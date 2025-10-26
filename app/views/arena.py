from rest_framework.decorators import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated , AllowAny
from app.models.post import Post
from app.serializers_f.post_serializer import ArenaSerializer
from rest_framework import status
from app.models.owner import Owner


class ArenaCreateView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        print('creating arena', request.data)
        owner = request.data.owner
        try:
            owner_user = Owner.object.get(pk=owner)
        except Owner.DoesNotExist:
            return Response({"error":"User does not exist"},status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error":str(e)},status=status.HTTP_400_BAD_REQUEST)
        if owner_user.arena_count > 1:
            return Response({"limit":"adding arena is limited!, please buy premium"})
        serializer = ArenaSerializer(data=request.data)
        if serializer.is_valid():
            arena = serializer.save()
            arena.owner.arena_count += 1
            arena.owner.save()
            return Response(ArenaSerializer(arena).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    # else:
    #     return Response({"error": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)


# {
# "name":"arena2",
# "location":"name",
# "owner":2,
# "cost":"1020",
# "open_time":"10:10",
# "close_time":"20:20"
# }


class ArenaListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            owner = request.user
            arena = Post.objects.filter(owner=owner)
            serializer = ArenaSerializer(arena, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            arena = Post.objects.get(pk=pk)
            serializer = ArenaSerializer(arena)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Post.DoesNotExist:
            return Response({"error": "Post not found"}, status=status.HTTP_404_NOT_FOUND)
    
    def put(self, request, pk):
        try:
            arena = Post.objects.get(pk=pk)
            serializer = ArenaSerializer(arena, data=request.data, partial=True)
            if serializer.is_valid():
                arena = serializer.save()
                return Response(ArenaSerializer(arena).data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Post.DoesNotExist:
            return Response({"error": "Post not found"}, status=status.HTTP_404_NOT_FOUND)
    
    def delete(self, request, pk):
        try:
            arena = Post.objects.get(pk=pk)
            arena.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Post.DoesNotExist:
            return Response({"error": "Post not found"}, status=status.HTTP_404_NOT_FOUND)