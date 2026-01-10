from functools import wraps

from core.base_service import BaseService


def validate_seller(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        self: BaseService = args[0]
        if not self.seller_id:
            return self.get_412_response("No seller id found in request")
        if not self.seller:
            return self.get_404_response("Seller Not Found")

        return func(*args, **kwargs)

    return wrapper
