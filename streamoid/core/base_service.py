from rest_framework import status


class BaseService(object):
    def __init__(self):
        self.response = {"code": "", "data": {}, "errors": {}, "message": ""}

    def set_response(self, code=status.HTTP_200_OK, data=None, errors=None, message="Success"):
        self.response = self._build_response(code=code, data=data, errors=errors, message=message)
        return self.response

    @staticmethod
    def _build_response(code, data=None, errors=None, message=""):
        return {
            "code": code,
            "data": data if data is not None else {},
            "errors": errors if errors is not None else {},
            "message": message,
        }

    # ----------  2XX response code ----------

    @classmethod
    def get_200_response(cls, data, message="Success"):
        return cls._build_response(code=status.HTTP_200_OK, data=data, message=message)

    @classmethod
    def get_201_response(cls, data, message="Created Successfully"):
        return cls._build_response(code=status.HTTP_201_CREATED, data=data, message=message)

    @classmethod
    def get_204_response(cls):
        return status.HTTP_204_NO_CONTENT

    # ----------  4XX response code ----------

    @classmethod
    def get_400_response(cls, errors, data=None, message="Bad Request"):
        return cls._build_response(code=status.HTTP_400_BAD_REQUEST, data=data, errors=errors, message=message)

    @classmethod
    def get_401_response(cls, errors, data=None, message="Unauthorized Request"):
        return cls._build_response(code=status.HTTP_401_UNAUTHORIZED, data=data, errors=errors, message=message)

    @classmethod
    def get_403_response(cls, errors, data=None, message="Forbidden"):
        return cls._build_response(code=status.HTTP_403_FORBIDDEN, data=data, errors=errors, message=message)

    @classmethod
    def get_404_response(cls, errors, data=None, message="Bad Request"):
        return cls._build_response(code=status.HTTP_404_NOT_FOUND, data=data, errors=errors, message=message)

    @classmethod
    def get_412_response(cls, errors, data=None, message="Precondition Failed"):
        return cls._build_response(
            code=status.HTTP_412_PRECONDITION_FAILED, data=data, errors=errors, message=message
        )

    # ----------  5XX response code here ----------

    @classmethod
    def get_500_response(cls, data=None, errors=None, message="Internal Server Error"):
        return cls._build_response(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR, data=data, errors=errors, message=message
        )
