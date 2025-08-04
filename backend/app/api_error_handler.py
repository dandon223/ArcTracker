from typing import Any

from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import exception_handler


def custom_exception_handler(exc: Any, context: Any) -> Any:
    response = exception_handler(exc, context)
    if isinstance(exc, ValidationError):
        message = exc.detail
        if isinstance(message, list):
            detail = " ".join(str(m) for m in message)
        elif isinstance(message, dict):
            detail = "; ".join(f"{field}: {' '.join(map(str, msgs))}" for field, msgs in message.items())
        else:
            detail = str(message)

        return Response({"detail": detail}, status=response.status_code if response else status.HTTP_400_BAD_REQUEST)

    return response
