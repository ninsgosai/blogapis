from django.http import JsonResponse
from rest_framework import status
from rest_framework.response import Response

from utils.functions import custom_response


class CustomPaginationMixin(object):
    @property
    def paginator(self):
        """
        The paginator instance associated with the view, or `None`.
        """
        if not hasattr(self, '_paginator'):
            if self.pagination_class is None:
                self._paginator = None
            else:
                self._paginator = self.pagination_class()
        return self._paginator

    def paginate_queryset(self, queryset):
        """
        Return a single page of results, or `None` if pagination
        is disabled.
        """
        if self.paginator is None:
            return None
        return self.paginator.paginate_queryset(
            queryset, self.request, view=self)

    def get_paginated_response(self, data):
        """
        Return a paginated style `Response` object for the given
        output data.
        """
        assert self.paginator is not None
        
        return Response({"status": True,
                         "message": "Success",
                         'links': {'next': self.paginator.get_next_link(),
                                   'previous': self.paginator.get_previous_link(),
                                   'current_page': self.paginator.page.number,
                                   'last_page': self.paginator.page.paginator.num_pages,
                                   },    
                         'count': self.paginator.page.paginator.count,
                         'data': data,
                         "status_code": 200})