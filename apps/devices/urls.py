from rest_framework.routers import DefaultRouter

from apps.devices.views import (
    DeviceViewSet, LogDeviceViewSet, LogActionViewSet)


router = DefaultRouter()
router.register(r'devices', DeviceViewSet, base_name='devices')
router.register(r'logs_devices', LogDeviceViewSet, base_name='logs_devices')
router.register(r'logs_actions', LogActionViewSet, base_name='logs_actions')
urlpatterns = router.urls
