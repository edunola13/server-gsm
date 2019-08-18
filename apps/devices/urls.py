from rest_framework.routers import DefaultRouter

from apps.devices.views import (DeviceViewSet, LogDeviceViewSet, LogActionViewSet,
                                RuleViewSet, RuleInstanceViewSet)


router = DefaultRouter()
router.register(r'devices', DeviceViewSet, base_name='devices')
router.register(r'logs_devices', LogDeviceViewSet, base_name='logs_devices')
router.register(r'logs_actions', LogActionViewSet, base_name='logs_actions')
router.register(r'rules', RuleViewSet, base_name='rules')
router.register(r'rules_instances', RuleInstanceViewSet, base_name='rules_instances')
urlpatterns = router.urls
