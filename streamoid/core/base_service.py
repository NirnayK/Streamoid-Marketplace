from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from rest_framework import serializers, status


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


class PaginationService(BaseService):
    def __init__(self, page_number=None, page_size=None, default_page_size=20):
        super().__init__()
        self.total_page_number = 0
        self.page_number = page_number
        self.page_size = page_size
        self.default_page_size = default_page_size

    def set_total_page_number(self, number, total_count):
        self.total_page_number = number
        self.response.update({"total_page_number": number, "total_count": total_count})

    def _get_total_count(self, data):
        if data is None:
            return 0
        if isinstance(data, (list, tuple, set)):
            return len(data)
        count_method = getattr(data, "count", None)
        if callable(count_method):
            try:
                return count_method()
            except TypeError:
                pass
        try:
            return len(data)
        except TypeError:
            return len(self._coerce_to_list(data))

    @staticmethod
    def _coerce_to_list(data):
        if data is None:
            return []
        if isinstance(data, (list, tuple, set)):
            return list(data)
        if isinstance(data, (str, bytes, dict)):
            return [data]
        try:
            return list(data)
        except TypeError:
            return [data]

    def _validate_pagination(self):
        if self.page_number is None and self.page_size is None:
            return None, None, None
        if self.page_number is None or self.page_size is None:
            return None, None, {"pagination": "Both page_number and page_size are required."}
        serializer = serializers.Serializer(
            data={"page_number": self.page_number, "page_size": self.page_size},
            fields={
                "page_number": serializers.IntegerField(min_value=1),
                "page_size": serializers.IntegerField(min_value=1),
            },
        )
        if not serializer.is_valid():
            return None, None, serializer.errors
        return serializer.validated_data["page_number"], serializer.validated_data["page_size"], None

    def _paginate(self, data, page_number, page_size):
        data = self._coerce_to_list(data)
        paginator_object = Paginator(data, page_size)
        try:
            datalist = paginator_object.page(page_number).object_list
        except PageNotAnInteger:
            datalist = paginator_object.page(1).object_list
        except EmptyPage:
            datalist = []
        finally:
            self.set_total_page_number(paginator_object.num_pages, paginator_object.count)
        return datalist

    def _set_unpaginated_response(self, data, serializer_class=None, serializer_context=None):
        datalist = self._coerce_to_list(data)
        if serializer_class:
            serializer_context = serializer_context or {}
            datalist = serializer_class(datalist, many=True, context=serializer_context).data
        self.set_response(data=datalist)
        total_count = self._get_total_count(datalist)
        self.set_total_page_number(0 if total_count == 0 else 1, total_count)

    def paginated_response(self, data=None, serializer_class=None, serializer_context=None):
        page_number, page_size, errors = self._validate_pagination()
        if errors:
            return self.get_400_response(errors=errors)
        if page_number is None and page_size is None:
            self._set_unpaginated_response(data, serializer_class, serializer_context)
            return self.response
        datalist = self._paginate(data, page_number, page_size)
        if serializer_class:
            serializer_context = serializer_context or {}
            datalist = serializer_class(datalist, many=True, context=serializer_context).data
        self.set_response(data=datalist)
        return self.response
