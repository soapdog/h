# pylint: disable=protected-access
import mock

from h.api.nipsa import worker


def test_add_nipsa_action():
    action = worker.add_nipsa_action({"_id": "test_id"})

    assert action == {
        "_op_type": "update",
        "_index": "annotator",
        "_type": "annotation",
        "_id": "test_id",
        "doc": {"not_in_public_site_areas": True}
    }


def test_remove_nipsa_action():
    action = worker.remove_nipsa_action({"_id": "test_id"})

    assert action == {
        "_op_type": "update",
        "_index": "annotator",
        "_type": "annotation",
        "_id": "test_id",
        "script": "ctx._source.remove(\"not_in_public_site_areas\")"
    }


@mock.patch("elasticsearch.Elasticsearch")
@mock.patch("elasticsearch.helpers")
def test_add_or_remove_nipsa_inits_elasticsearch_client(_, elasticsearch):
    worker.add_or_remove_nipsa("test_user_id", "nipsa")
    elasticsearch.assert_called_once_with(
        [{"host": "localhost", "port": 9200}])


@mock.patch("elasticsearch.Elasticsearch")
@mock.patch("elasticsearch.helpers")
def test_add_or_remove_nipsa_passes_elasticsearch_client_to_scan(
        helpers, elasticsearch):
    es_client = mock.MagicMock()
    elasticsearch.return_value = es_client

    worker.add_or_remove_nipsa("test_user_id", "nipsa")

    assert helpers.scan.call_args[0][0] == es_client


@mock.patch("elasticsearch.Elasticsearch")
@mock.patch("elasticsearch.helpers")
def test_add_or_remove_nipsa_passes_elasticsearch_client_to_bulk(
        helpers, elasticsearch):
    es_client = mock.MagicMock()
    elasticsearch.return_value = es_client

    worker.add_or_remove_nipsa("test_user_id", "nipsa")

    assert helpers.bulk.call_args[0][0] == es_client


@mock.patch("h.api.search.not_nipsad_annotations")
@mock.patch("elasticsearch.Elasticsearch")
@mock.patch("elasticsearch.helpers")
def test_add_nipsa_gets_query(helpers, elasticsearch, not_nipsad_annotations):
    worker.add_or_remove_nipsa("test_user_id", "nipsa")

    not_nipsad_annotations.assert_called_once_with("test_user_id")


@mock.patch("h.api.search.nipsad_annotations")
@mock.patch("elasticsearch.Elasticsearch")
@mock.patch("elasticsearch.helpers")
def test_remove_nipsa_gets_query(helpers, elasticsearch, nipsad_annotations):
    worker.add_or_remove_nipsa("test_user_id", "unnipsa")

    nipsad_annotations.assert_called_once_with("test_user_id")


@mock.patch("h.api.search.not_nipsad_annotations")
@mock.patch("elasticsearch.Elasticsearch")
@mock.patch("elasticsearch.helpers")
def test_add_nipsa_passes_query_to_scan(helpers, _, not_nipsad_annotations):
    query = mock.MagicMock()
    not_nipsad_annotations.return_value = query

    worker.add_or_remove_nipsa("test_user_id", "nipsa")

    assert helpers.scan.call_args[1]["query"] == query


@mock.patch("h.api.search.nipsad_annotations")
@mock.patch("elasticsearch.Elasticsearch")
@mock.patch("elasticsearch.helpers")
def test_remove_nipsa_passes_query_to_scan(helpers, _, nipsad_annotations):
    query = mock.MagicMock()
    nipsad_annotations.return_value = query

    worker.add_or_remove_nipsa("test_user_id", "unnipsa")

    assert helpers.scan.call_args[1]["query"] == query


@mock.patch("elasticsearch.Elasticsearch")
@mock.patch("elasticsearch.helpers")
def test_add_nipsa_passes_actions_to_bulk(helpers, _):
    helpers.scan.return_value = [
        {"_id": "foo"}, {"_id": "bar"}, {"_id": "gar"}]

    worker.add_or_remove_nipsa("test_user_id", "nipsa")

    actions = helpers.bulk.call_args[0][1]
    assert [action["_id"] for action in actions] == ["foo", "bar", "gar"]


@mock.patch("elasticsearch.Elasticsearch")
@mock.patch("elasticsearch.helpers")
def test_remove_nipsa_passes_actions_to_bulk(helpers, _):
    helpers.scan.return_value = [
        {"_id": "foo"}, {"_id": "bar"}, {"_id": "gar"}]

    worker.add_or_remove_nipsa("test_user_id", "unnipsa")

    actions = helpers.bulk.call_args[0][1]
    assert [action["_id"] for action in actions] == ["foo", "bar", "gar"]
