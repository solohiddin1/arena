from rest_framework.pagination import PageNumberPagination
from django.core.paginator import EmptyPage
# from apps.shared.utils.utils import SuccessResponse


class CustomPageNumberPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

    def paginate_queryset(self, queryset, request, view=None):
        try:
            return super().paginate_queryset(queryset, request, view=view)
        except EmptyPage:
            self.page = None
            return []

    def get_paginated_response(self, data):
        return {
            'total_count': self.page.paginator.count if self.page else 0,
            'count': len(data),
            'next': self.get_next_link() if self.page else None,
            'previous': self.get_previous_link() if self.page else None,
            'results': data
        }
