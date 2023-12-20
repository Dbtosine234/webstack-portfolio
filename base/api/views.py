from django.http import JsonResponse

def getRoutes(request):
    routes = [
        'GET /api',
        'GET /api/courses',
        'GET /api/courses/:id'
    ]
    return JsonResponse(routes, safe=False)