from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.generics import GenericAPIView

from apps.posts.api.serializers.favourite import FavouriteReadSerializer, FavouriteWriteSerializer
from apps.posts.models import Favourite, Post
from apps.shared.utils import SuccessResponse
from apps.users.permissions import ClientPermission


@extend_schema(tags=["favourite"], summary="List my favourite posts")
class FavouriteListView(GenericAPIView):
    permission_classes = [ClientPermission]

    def get(self, request, *args, **kwargs):
        favourites = (
            Favourite.objects.filter(user=request.user)
            .select_related("post__owner", "post__region", "post__district", "post__category")
            .prefetch_related("post__work_days", "post__amenities__translations")
            .order_by("-created_at")
        )
        serializer = FavouriteReadSerializer(favourites, many=True, context={"request": request})
        return SuccessResponse(serializer.data)


@extend_schema(tags=["favourite"], summary="Add post to favourites", request=FavouriteWriteSerializer)
class FavouriteCreateView(GenericAPIView):
    permission_classes = [ClientPermission]
    serializer_class = FavouriteWriteSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        post_id = serializer.validated_data["post_id"]
        post = Post.objects.filter(id=post_id, is_hidden=False, state="ACCEPTED").first()
        if post is None:
            return SuccessResponse({"detail": "Post not found."})

        favourite, created = Favourite.objects.get_or_create(user=request.user, post=post)
        return SuccessResponse({
            "post_id": post_id,
            "is_favourite": True,
            "created": created,
        })


@extend_schema(tags=["favourite"], summary="Remove post from favourites")
class FavouriteDeleteView(GenericAPIView):
    permission_classes = [ClientPermission]

    def delete(self, request, post_id, *args, **kwargs):
        deleted, _ = Favourite.objects.filter(user=request.user, post_id=post_id).delete()
        if not deleted:
            return SuccessResponse({"detail": "Post not found in favourites."}, status=status.HTTP_404_NOT_FOUND)
        return SuccessResponse({"post_id": post_id, "is_favourite": False})