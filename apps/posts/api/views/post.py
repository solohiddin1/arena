from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from apps.posts.api.serializers.post import PostBaseSerializer, CategorySerializer, PostListSerializer, PostWriteSerializer
from apps.posts.services import PostService
from apps.shared.utils import SuccessResponse
from apps.users.permissions import ClientPermission

post_service = PostService()


POST_LIST_PARAMETERS = [
    OpenApiParameter(
        name="lat",
        type=OpenApiTypes.FLOAT,
        location=OpenApiParameter.QUERY,
        required=False,
        description="User latitude for distance filtering.",
    ),
    OpenApiParameter(
        name="long",
        type=OpenApiTypes.FLOAT,
        location=OpenApiParameter.QUERY,
        required=False,
        description="User longitude for distance filtering.",
    ),
    OpenApiParameter(
        name="radius_km",
        type=OpenApiTypes.FLOAT,
        location=OpenApiParameter.QUERY,
        required=False,
        description="Distance radius in kilometers. Default is 10 km.",
    ),
    OpenApiParameter(
        name="category_ids",
        type=OpenApiTypes.STR,
        location=OpenApiParameter.QUERY,
        required=False,
        description="Comma-separated category ids, e.g. '1,2,3'.",
    ),
    OpenApiParameter(
        name="rating",
        type=OpenApiTypes.FLOAT,
        location=OpenApiParameter.QUERY,
        required=False,
        description="Minimum average rating filter.",
    ),
]


@extend_schema(
    tags=["post"],
    summary="List posts",
    parameters=POST_LIST_PARAMETERS,
    responses={200: PostListSerializer(many=True)},
)
class PostListView(GenericAPIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        queryset = post_service.list_posts(request.query_params)
        serializer = PostListSerializer(queryset, many=True, context={"request": request})
        return SuccessResponse(serializer.data)


@extend_schema(
    tags=["post"],
    summary="List my posts",
    responses={200: PostBaseSerializer(many=True)},
)
class MyPostListView(GenericAPIView):
    permission_classes = [ClientPermission]

    def get(self, request, *args, **kwargs):
        queryset = post_service.list_my_posts(request.user)
        serializer = PostBaseSerializer(queryset, many=True, context={"request": request})
        return SuccessResponse(serializer.data)


@extend_schema(
    tags=["post"],
    summary="Create post",
    description="Create a post with post fields and upload one or multiple images via Swagger (multipart/form-data).",
    request={
        "multipart/form-data": {
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "Post title"},
                "location_title": {"type": "string", "description": "Location title"},
                "cost": {"type": "number", "format": "float", "description": "Post cost"},
                "lat": {"type": "number", "format": "float", "description": "Latitude"},
                "long": {"type": "number", "format": "float", "description": "Longitude"},
                # "state": {
                #     "type": "string",
                #     "description": "Post state",
                #     "enum": ["CHECKING", "ACCEPTED", "CANCELLED", "FROZEN"],
                # },
                "region": {"type": "integer", "description": "Region id"},
                "district": {"type": "integer", "description": "District id"},
                "category": {"type": "integer", "description": "Category id"},
                "images": {
                    "type": "array",
                    "items": {"type": "string", "format": "binary"},
                    "description": "Post images. You can upload multiple files.",
                },
                "work_hours": {
                    "type": "string",
                    "example": '[{"days":["MONDAY","TUESDAY","WEDNESDAY","THURSDAY","FRIDAY"],'
                               '"start_time":"08:00","end_time":"20:00"},{"days":["SATURDAY"],'
                               '"start_time":"10:00","end_time":"16:00"},{"days":["SUNDAY"],'
                               '"is_closed":true}]',
                    "description": "JSON string. Groups of days sharing the same hours.",
                },
            },
            "required": ["title", "cost"],
        }
    },
    responses={200: PostListSerializer},
)
class PostCreateView(GenericAPIView):
    permission_classes = [ClientPermission]
    serializer_class = PostWriteSerializer
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        post = post_service.create_post(request.user, serializer.validated_data)
        post_service.create_post_images(post, request.FILES.getlist("images"))
        return SuccessResponse(PostBaseSerializer(post, context={"request": request}).data)


@extend_schema(tags=["post"], summary="Get post detail")
class PostDetailView(GenericAPIView):
    permission_classes = [AllowAny]

    def get(self, request, post_id, *args, **kwargs):
        post = post_service.get_post(post_id)
        if post is None:
            return SuccessResponse({"detail": "Post not found."})
        return SuccessResponse(PostListSerializer(post, context={"request": request}).data)


@extend_schema(tags=["post"], summary="Update post")
class PostUpdateView(GenericAPIView):
    permission_classes = [ClientPermission]
    serializer_class = PostWriteSerializer

    def patch(self, request, post_id, *args, **kwargs):
        post = post_service.get_post(post_id)
        if post is None:
            return SuccessResponse({"detail": "Post not found."})

        if post.owner_id != request.user.id:
            return SuccessResponse({"detail": "You can update only your own post."})

        serializer = self.get_serializer(post, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        post = post_service.update_post(post, serializer.validated_data)
        return SuccessResponse(PostListSerializer(post, context={"request": request}).data)


@extend_schema(tags=["post"], summary="Delete post")
class PostDeleteView(GenericAPIView):
    permission_classes = [ClientPermission]

    def delete(self, request, post_id, *args, **kwargs):
        post = post_service.get_post(post_id)
        if post is None:
            return SuccessResponse({"detail": "Post not found."}, status=status.HTTP_404_NOT_FOUND)

        if post.owner_id != request.user.id:
            return SuccessResponse({"detail": "You can delete only your own post."}, status=status.HTTP_403_FORBIDDEN)

        post_service.delete_post(post)
        return SuccessResponse({"detail": "Post deleted successfully."}, status=status.HTTP_204_NO_CONTENT)


@extend_schema(tags=["post-category"], summary="List categories")
class CategoryListView(GenericAPIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        categories = post_service.list_categories()
        serializer = CategorySerializer(categories, many=True, context={"request": request})
        return SuccessResponse(serializer.data)
