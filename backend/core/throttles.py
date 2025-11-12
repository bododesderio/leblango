from rest_framework.throttling import UserRateThrottle


class StrictWriteThrottle(UserRateThrottle):
    rate = '30/min'
