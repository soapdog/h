"""Worker functions for the NIPSA feature."""
import json

import annotator
import elasticsearch
import elasticsearch.helpers

from h.api import search


def _add_nipsa_action(annotation):
    """Return an Elasticsearch action for adding NIPSA to the annotation."""
    return {
        "_op_type": "update",
        "_index": annotator.es.index,
        "_type": "annotation",
        "_id": annotation["_id"],
        "doc": {"not_in_public_site_areas": True}
    }


def _remove_nipsa_action(annotation):
    """Return an Elasticsearch action to remove NIPSA from the annotation."""
    return {
        "_op_type": "update",
        "_index": annotator.es.index,
        "_type": "annotation",
        "_id": annotation["_id"],
        "script": "ctx._source.remove(\"not_in_public_site_areas\")"
    }


def _es_client():
    """Return an elasticsearch.Elasticsearch client object."""
    return elasticsearch.Elasticsearch([{"host": "localhost", "port": 9200}])


def _add_or_remove_nipsa(user_id, action):
    """Add/remove the NIPSA flag to/from all of the user's annotations."""
    assert action in ("nipsa", "unnipsa")

    if action == "nipsa":
        query = search.not_nipsad_annotations(user_id)
    else:
        query = search.nipsad_annotations(user_id)

    es_client = _es_client()

    annotations = elasticsearch.helpers.scan(es_client, query=query, fields=[])

    if action == "add":
        actions = [_add_nipsa_action(a) for a in annotations]
    else:
        actions = [_remove_nipsa_action(a) for a in annotations]

    elasticsearch.helpers.bulk(es_client, actions)


def _handle_message(_, message):
    """Handle a message on the "nipsa_users_annotations" channel."""
    _add_or_remove_nipsa(**json.loads(message.body))


def user_worker(request):
    """Worker function for NIPSA'ing and un-NIPSA'ing users.

    This is a worker function that listens for user-related NIPSA messages on
    NSQ (when the NIPSA API adds the NIPSA flag to or removes the NIPSA flag
    from a user) and adds the NIPSA flag to or removes the NIPSA flag from all
    of the NIPSA'd user's annotations.

    """
    reader = request.get_queue_reader(
        "nipsa_user_requests", "nipsa_users_annotations")
    reader.on_message.connect(_handle_message)
    reader.start(block=True)
