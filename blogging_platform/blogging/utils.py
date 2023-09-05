from django.utils.translation import gettext_lazy as _
from rest_framework.views import exception_handler
from utils.functions import custom_response


def custom_exception_handler(exc, context):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)

    # Update the structure of the response data.
    if response is not None:
        customized_response = {}

        for key, value in response.data.items():
            if isinstance(value, list):
                error = custom_response(False, message=_(value[0]))
            else:
                error = custom_response(False, message=_(value))
            customized_response.update(error)
            response.data = customized_response
            break

    return response