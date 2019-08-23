from rest_framework.routers import DefaultRouter

from apps.rules.views import (RuleViewSet, RuleInstanceViewSet)


router = DefaultRouter()
router.register(r'rules', RuleViewSet, base_name='rules')
router.register(r'rules_instances', RuleInstanceViewSet, base_name='rules_instances')
urlpatterns = router.urls
