from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SavedItemViewSet, whatsapp_webhook

router = DefaultRouter()
router.register(r'items', SavedItemViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('webhook/whatsapp/', whatsapp_webhook, name='whatsapp_webhook'),
]
