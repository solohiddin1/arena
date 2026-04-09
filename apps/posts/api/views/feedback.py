from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from apps.posts.api.serializers import FeedbackReadSerializer, FeedbackWriteSerializer
from apps.posts.services import PostService
from apps.shared.utils import SuccessResponse
from apps.users.permissions import ClientPermission

post_service = PostService()


@extend_schema(tags=["post-feedback"], summary="List post feedbacks")
class PostFeedbackListView(GenericAPIView):
    permission_classes = [AllowAny]

    def get(self, request, post_id, *args, **kwargs):
        post = post_service.get_post(post_id)
        if post is None:
            return SuccessResponse({"detail": "Post not found."})

        feedbacks = post_service.list_feedbacks(post)
        serializer = FeedbackReadSerializer(feedbacks, many=True, context={"request": request})
        return SuccessResponse(serializer.data)


@extend_schema(tags=["post-feedback"], summary="Create or update feedback for a post")
class PostFeedbackUpsertView(GenericAPIView):
    permission_classes = [ClientPermission]
    serializer_class = FeedbackWriteSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        post = post_service.get_post(serializer.validated_data["post_id"])
        if post is None:
            return SuccessResponse({"detail": "Post not found."})

        feedback = post_service.upsert_feedback(request.user, post, serializer.validated_data)
        return SuccessResponse(FeedbackReadSerializer(feedback, context={"request": request}).data)
