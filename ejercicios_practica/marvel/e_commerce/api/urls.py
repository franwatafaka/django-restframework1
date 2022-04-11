from django.urls import path
from e_commerce.api.marvel_api_views import *

urlpatterns = [
    path('get_comics/',get_comics),
    path('get_comics_by_titles/',get_comics_by_titles),
    path('get_characters/',get_characters),
    path('purchased_item/',purchased_item),
]
 