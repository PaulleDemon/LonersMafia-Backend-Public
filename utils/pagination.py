from collections import OrderedDict
from rest_framework import pagination
from rest_framework.response import Response


class CustomPageNumber(pagination.PageNumberPagination):
    """
        custom pagination class that will contain the following fields
    """

    def get_paginated_response(self, data):
        return Response(OrderedDict([
             ('pages', self.page.paginator.num_pages),
             ('count', self.page.paginator.count),
             ('countItemsOnPage', self.page_size),
             ('current', self.page.number),
             ('next', self.get_next_link()),
             ('previous', self.get_previous_link()),
             ('results', data)
         ]))
