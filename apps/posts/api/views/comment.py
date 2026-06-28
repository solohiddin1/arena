from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny

from apps.posts.api.serializers import FeedbackReadSerializer, FeedbackWriteSerializer
from apps.posts.models import Feedback, Post
from apps.posts.services import PostService
from apps.shared.utils import SuccessResponse
from apps.users.permissions import ClientPermission

post_service = PostService()


@extend_schema(tags=["comment"], summary="List comments of a post")
class CommentListView(GenericAPIView):
    permission_classes = [AllowAny]

    def get(self, request, post_id, *args, **kwargs):
        comments = (
            Feedback.objects.filter(post_id=post_id, comment__isnull=False)
            .exclude(comment="")
            .select_related("user")
            .order_by("-created_at")
        )
        serializer = FeedbackReadSerializer(comments, many=True, context={"request": request})
        return SuccessResponse(serializer.data)


@extend_schema(tags=["comment"], summary="Add or update comment on a post", request=FeedbackWriteSerializer)
class CommentCreateView(GenericAPIView):
    permission_classes = [ClientPermission]
    serializer_class = FeedbackWriteSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if not serializer.validated_data.get("comment"):
            return SuccessResponse({"detail": "comment field is required."}, status=status.HTTP_400_BAD_REQUEST)

        post = post_service.get_post(serializer.validated_data["post_id"])
        if post is None:
            return SuccessResponse({"detail": "Post not found."}, status=status.HTTP_404_NOT_FOUND)

        feedback = post_service.upsert_feedback(request.user, post, serializer.validated_data)
        return SuccessResponse(FeedbackReadSerializer(feedback, context={"request": request}).data)