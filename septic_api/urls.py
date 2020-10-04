"""septic_api URL Configuration"""
from rest_framework import routers

from septic_api.views import HomeDataViewSet

router = routers.SimpleRouter()
router.register(r'home', HomeDataViewSet, basename='home')
urlpatterns = router.urls
