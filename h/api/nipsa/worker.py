"""Worker functions for the NIPSA feature."""
import json
import logging

import elasticsearch
import elasticsearch.helpers


LOGGER = logging.getLogger('h.worker')


def _es_client():
    """Return an Elasticsearch client object."""
    # TODO: Get the host and port from the config.
    return elasticsearch.Elasticsearch(
        [{"host": "localhost", "port": 9200}])


def _nipsa_user(user_id):
    """Add the NIPSA flag to all of a user's annotations."""
    must_clauses = [
        {"not": {"term": {"not_in_public_site_areas": True}}},
        {"term": {"user": user_id}}
    ]
    query = {
        "query": {
            "filtered": {
                "filter": {
                    "bool": {"must": must_clauses}
                }
            },
        }
    }

    es_client = _es_client()
    actions = []
    for annotation in elasticsearch.helpers.scan(es_client, query=query):
        actions.append({
            "_op_type": "update",
            "_index": "annotator",
            "_type": "annotation",
            "_id": annotation["_id"],
            "doc": {
                "not_in_public_site_areas": True
            },
            "fields": "",
        })

    try:
        elasticsearch.helpers.bulk(es_client, actions)
    except elasticsearch.helpers.BulkIndexError as err:
        LOGGER.debug(err)


def _unnipsa_user(user_id):
    """Remove the NIPSA flag from all of a user's annotations."""
    must_clauses = [
        {"term": {"not_in_public_site_areas": True}},
        {"term": {"user": user_id}}
    ]
    query = {
        "query": {
            "filtered": {
                "filter": {
                    "bool": {"must": must_clauses}
                }
            },
        }
    }

    es_client = _es_client()
    actions = []
    for annotation in elasticsearch.helpers.scan(es_client, query=query):
        actions.append({
            "_op_type": "update",
            "_index": "annotator",
            "_type": "annotation",
            "_id": annotation["_id"],
            "script": "ctx._source.remove(\"not_in_public_site_areas\")",
            "fields": "",
        })

    try:
        elasticsearch.helpers.bulk(es_client, actions)
    except elasticsearch.helpers.BulkIndexError as err:
        LOGGER.debug(err)


def _handle_message(_, message):
    """Handle a message on the "nipsa_users_annotations" channel."""
    message_data = json.loads(message.body)
    actions = {
        "nipsa": _nipsa_user,
        "unnipsa": _unnipsa_user
    }
    actions[message_data["action"]](message_data["user_id"])


def user_worker(request):
    """Worker function for NIPSA'ing and un-NIPSA'ing users.

    This is a worker function that listens for user-related NIPSA messages on
    NSQ (when the NIPSA API adds the NIPSA flag to or removes the NIPSA flag
    from a user) and adds the NIPSA flag to or removes the NIPSA flag from all
    of the NIPSA'd user's annotations.

    """
    if request.registry.feature("queue"):
        reader = request.get_queue_reader(
            "nipsa_user_requests", "nipsa_users_annotations")
        reader.on_message.connect(_handle_message)
        reader.start(block=True)
