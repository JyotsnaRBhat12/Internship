from django.http import JsonResponse

class RoleMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        if request.path.startswith('/api/admin-only/'):
            if not request.user.is_authenticated:
                return JsonResponse({"error": "Authentication required"}, status=401)
            if not request.user.is_staff:
                return JsonResponse({"error": "Admin role required"}, status=403)

        return self.get_response(request)
