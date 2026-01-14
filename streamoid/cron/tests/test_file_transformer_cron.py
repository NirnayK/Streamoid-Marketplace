from io import BytesIO
from types import SimpleNamespace
from unittest.mock import patch

from cron.file_transformer_cron import FileTransformerCron

from mapping.constants import (
    EVALUATION_STATUS_FAILED,
    EVALUATION_STATUS_SUCCESS,
    TRANSFORMED_FOLDER,
)
from seller.constants import CSV


class FakeMapping:
    def __init__(self, seller_file, marketplace_template, mappings):
        self.id = 1
        self.seller_file = seller_file
        self.marketplace_template = marketplace_template
        self.mappings = mappings
        self.evaluation_status = None
        self.transformed_file_path = None
        self.saved_update_fields = None

    def save(self, update_fields=None):
        self.saved_update_fields = update_fields


class FakeQuerySet:
    def __init__(self, items):
        self._items = items

    def select_related(self, *args, **kwargs):
        return self

    def iterator(self):
        return iter(self._items)


def test_run_processes_pending_mappings():
    mappings = [SimpleNamespace(), SimpleNamespace()]
    queryset = FakeQuerySet(mappings)

    with patch("cron.file_transformer_cron.Mappings.objects.filter", return_value=queryset) as filter_mock:
        with patch.object(FileTransformerCron, "_process_mapping") as process_mock:
            FileTransformerCron.run()

    filter_mock.assert_called_once_with(evaluation_status="pending")
    assert process_mock.call_count == len(mappings)


def test_process_mapping_success_updates_status_and_path():
    seller = SimpleNamespace(bucket_name="bucket")
    seller_file = SimpleNamespace(name="items.csv", path="bucket/items.csv", file_type=CSV, seller=seller)
    marketplace_template = SimpleNamespace(template={"sku": {"type": "string"}})
    mapping = FakeMapping(seller_file, marketplace_template, mappings=[{"seller": "sku", "marketplace": "sku"}])
    output_file = BytesIO(b"data")

    with patch.object(FileTransformerCron, "_read_file_bytes", return_value=b"file"):
        with patch.object(FileTransformerCron, "_parse_rows", return_value=(["sku"], [["1"]])):
            with patch("cron.file_transformer_cron.validate_file_iter", return_value=iter([{"sku": "1"}])):
                with patch.object(FileTransformerCron, "_build_transformed_file", return_value=output_file):
                    with patch(
                        "cron.file_transformer_cron.MinioHandler.store_file", return_value=True
                    ) as store_mock:
                        FileTransformerCron._process_mapping(mapping)

    assert mapping.evaluation_status == EVALUATION_STATUS_SUCCESS
    assert mapping.transformed_file_path == f"bucket/{TRANSFORMED_FOLDER}/items.csv"
    assert mapping.saved_update_fields == ["evaluation_status", "transformed_file_path", "updated_at"]
    assert output_file.closed
    store_mock.assert_called_once()
    args, _kwargs = store_mock.call_args
    assert args[0] == "bucket"
    assert args[1] == f"{TRANSFORMED_FOLDER}/items.csv"
    assert args[2] is output_file


def test_process_mapping_sets_failed_when_storage_fails():
    seller = SimpleNamespace(bucket_name="bucket")
    seller_file = SimpleNamespace(name="items.csv", path="bucket/items.csv", file_type=CSV, seller=seller)
    marketplace_template = SimpleNamespace(template={"sku": {"type": "string"}})
    mapping = FakeMapping(seller_file, marketplace_template, mappings=[{"seller": "sku", "marketplace": "sku"}])
    output_file = BytesIO(b"data")

    with patch.object(FileTransformerCron, "_read_file_bytes", return_value=b"file"):
        with patch.object(FileTransformerCron, "_parse_rows", return_value=(["sku"], [["1"]])):
            with patch("cron.file_transformer_cron.validate_file_iter", return_value=iter([{"sku": "1"}])):
                with patch.object(FileTransformerCron, "_build_transformed_file", return_value=output_file):
                    with patch("cron.file_transformer_cron.MinioHandler.store_file", return_value=False):
                        FileTransformerCron._process_mapping(mapping)

    assert mapping.evaluation_status == EVALUATION_STATUS_FAILED
    assert mapping.transformed_file_path is None
    assert mapping.saved_update_fields == ["evaluation_status", "transformed_file_path", "updated_at"]
    assert output_file.closed
