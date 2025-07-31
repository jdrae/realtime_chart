from django.db import connection
from django.db.utils import OperationalError
from django.http import JsonResponse


def health_check(request):
    try:
        connection.ensure_connection()
        return JsonResponse({"status": "ok"})
    except OperationalError:
        return JsonResponse({"status": "error"}, status=500)
