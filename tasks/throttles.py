from rest_framework.throttling import UserRateThrottle


class UploadRateThrottle(UserRateThrottle):
    scope = 'upload'


class AnalyticsRateThrottle(UserRateThrottle):
    scope = 'analytics'
