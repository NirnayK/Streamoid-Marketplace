from functools import wraps

from core.base_service import BaseService


def validate_marketplace(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        self: BaseService = args[0]
        if not self.marketplace_id:
            return self.get_412_response("No marketplace id found in request")
        if not self.marketplace:
            return self.get_404_response("Marketplace Not Found")

        return func(*args, **kwargs)

    return wrapper
