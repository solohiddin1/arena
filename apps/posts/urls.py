from django.urls import path

from apps.posts.api.views import (
    CategoryListView,
    MyPostListView,
    PostCreateView,
    PostDeleteView,
    PostDetailView,
    PostFeedbackListView,
    PostFeedbackUpsertView,
    PostListView,
    PostUpdateView,
)

urlpatterns = [
    path("list/", PostListView.as_view(), name="post_list"),
    path("my-posts/", MyPostListView.as_view(), name="my_post_list"),
    path("create/", PostCreateView.as_view(), name="post_create"),
    path("detail/<int:post_id>/", PostDetailView.as_view(), name="post_detail"),
    path("update/<int:post_id>/", PostUpdateView.as_view(), name="post_update"),
    path("delete/<int:post_id>/", PostDeleteView.as_view(), name="post_delete"),
    path("feedback/list/<int:post_id>/", PostFeedbackListView.as_view(), name="post_feedback_list"),
    path("feedback/upsert/", PostFeedbackUpsertView.as_view(), name="post_feedback_upsert"),
    path("categories/", CategoryListView.as_view(), name="post_category_list"),
]
