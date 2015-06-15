# pylint: disable=protected-access
import mock

from h.api.nipsa import worker


@mock.patch("elasticsearch.Elasticsearch")
@mock.patch("elasticsearch.helpers")
def test_add_or_remove_nipsa_flags_inits_elasticsearch(_, elasticsearch):
    """It should init the Elasticsearch object with the right params."""
    worker._add_or_remove_nipsa_flags("test_user_id")

    elasticsearch.assert_called_once_with(
        [{"host": "localhost", "port": 9200}])


@mock.patch("elasticsearch.Elasticsearch")
@mock.patch("elasticsearch.helpers")
def test_add_or_remove_nipsa_flags_passes_client_to_scan(
        helpers, elasticsearch):
    """It should pass the Elasticsearch client to scan()."""
    es_client = mock.MagicMock()
    elasticsearch.return_value = es_client

    worker._add_or_remove_nipsa_flags("test_user_id")

    assert helpers.scan.call_count == 1
    assert helpers.scan.call_args[0][0] == es_client

@mock.patch("elasticsearch.Elasticsearch")
@mock.patch("elasticsearch.helpers")
def test_add_or_remove_nipsa_flags_filters_by_user_id(helpers, elasticsearch):
    """It should filter for only the given user's annotations."""
    for add in (True, False):
        worker._add_or_remove_nipsa_flags("test_user_id", add=add)

        query = helpers.scan.call_args[1]["query"]["query"]["filtered"]
        must_clauses = query["filter"]["bool"]["must"]
        assert {"term": {"user": "test_user_id"}} in must_clauses


@mock.patch("elasticsearch.Elasticsearch")
@mock.patch("elasticsearch.helpers")
def test_add_nipsa_flags_filters_by_nipsa(helpers, elasticsearch):
    """When adding nipsa it should filter for only non-nipsa'd annotations."""
    worker._add_or_remove_nipsa_flags("test_user_id", add=True)

    assert helpers.scan.call_count == 1
    query = helpers.scan.call_args[1]["query"]["query"]["filtered"]
    must_clauses = query["filter"]["bool"]["must"]
    assert {"not": {"term": {"not_in_public_site_areas": True}}} in (
        must_clauses)


@mock.patch("elasticsearch.Elasticsearch")
@mock.patch("elasticsearch.helpers")
def test_remove_nipsa_flags_filters_by_nipsa(helpers, elasticsearch):
    """When removing nipsa it should filter for only nipsa'd annotations."""
    worker._add_or_remove_nipsa_flags("test_user_id", add=False)

    assert helpers.scan.call_count == 1
    query = helpers.scan.call_args[1]["query"]["query"]["filtered"]
    must_clauses = query["filter"]["bool"]["must"]
    assert {"term": {"not_in_public_site_areas": True}} in must_clauses


@mock.patch("elasticsearch.Elasticsearch")
@mock.patch("elasticsearch.helpers")
def test_add_nipsa_flags_passes_es_client_to_bulk(helpers, elasticsearch):
    """It should pass the Elasticsearch object to bulk()."""
    es_client = mock.MagicMock()
    elasticsearch.return_value = es_client

    worker._add_or_remove_nipsa_flags("test_user_id", add=True)

    assert helpers.bulk.call_count == 1
    assert helpers.bulk.call_args[0][0] == es_client


@mock.patch("elasticsearch.Elasticsearch")
@mock.patch("elasticsearch.helpers")
def test_add_nipsa_flags_actions(helpers, _):
    """It should pass the right actions to bulk()."""
    annotations = [{"_id": "foo"}, {"_id": "bar"}, {"_id": "gar"}]
    helpers.scan.return_value = annotations

    worker._add_or_remove_nipsa_flags("test_user_id", add=True)

    assert helpers.bulk.call_count == 1
    assert helpers.bulk.call_args[0][1] == [
        {
            "_op_type": "update",
            "_index": "annotator",
            "_type": "annotation",
            "_id": annotation["_id"],
            "doc": {"not_in_public_site_areas": True}
        }
        for annotation in annotations]


@mock.patch("elasticsearch.Elasticsearch")
@mock.patch("elasticsearch.helpers")
def test_remove_nipsa_flags_passes_es_client_to_bulk(helpers, elasticsearch):
    """It should pass the Elasticsearch object to bulk()."""
    es_client = mock.MagicMock()
    elasticsearch.return_value = es_client

    worker._add_or_remove_nipsa_flags("test_user_id", add=False)

    assert helpers.bulk.call_count == 1
    assert helpers.bulk.call_args[0][0] == es_client


@mock.patch("elasticsearch.Elasticsearch")
@mock.patch("elasticsearch.helpers")
def test_remove_nipsa_flags_actions(helpers, _):
    """It should pass the right actions to bulk()."""
    annotations = [{"_id": "foo"}, {"_id": "bar"}, {"_id": "gar"}]
    helpers.scan.return_value = annotations

    worker._add_or_remove_nipsa_flags("test_user_id", add=False)

    assert helpers.bulk.call_count == 1
    assert helpers.bulk.call_args[0][1] == [
        {
            "_op_type": "update",
            "_index": "annotator",
            "_type": "annotation",
            "_id": annotation["_id"],
            "script": "ctx._source.remove(\"not_in_public_site_areas\")"
        }
        for annotation in annotations]
