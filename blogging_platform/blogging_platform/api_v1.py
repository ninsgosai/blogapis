from django.urls import path, include

api_v1 = [
    path('api/v1/', include("api.api_v1.v1_appblog.urls")),
]
