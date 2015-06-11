"""Worker functions for the NIPSA feature."""
import json

import annotator
import elasticsearch
import elasticsearch.helpers


def _add_or_remove_nipsa_flags(user_id, add=True):
    """Add or remove the NIPSA flag to or from the user's annotations.

    :param user_id: the ID of the user whose annotations to edit
    :type user_id: unicode

    :param add: if True then add the NIPSA flag to all of the user's
        annotations, if False remove it from them
    :type add: bool

    """
    must_clauses = [{"term": {"user": user_id}}]

    if add:
        # If we're NIPSA'ing a user we want to find all their annotations that
        # are not (yet) NIPSA'd.
        must_clauses.append(
            {"not": {"term": {"not_in_public_site_areas": True}}})
    else:
        # If we're un-NIPSA'ing a user we want to find all their annotations
        # that are currently NIPSA'd.
        must_clauses.append({"term": {"not_in_public_site_areas": True}})

    query = {
        "query": {
            "filtered": {
                "filter": {
                    "bool": {"must": must_clauses}
                }
            },
        }
    }

    # TODO: Get the host and port from the config.
    es_client = elasticsearch.Elasticsearch(
        [{"host": "localhost", "port": 9200}])

    actions = []
    for annotation in elasticsearch.helpers.scan(es_client, query=query,
                                                 fields=[]):
        action = {
            "_op_type": "update",
            "_index": annotator.es.index,
            "_type": "annotation",
            "_id": annotation["_id"],
        }

        if add:
            # We want to add the nipsa flag to the annotations.
            action["doc"] = {"not_in_public_site_areas": True}
        else:
            # We want to remove the nipsa flag from the annotations.
            action["script"] = (
                "ctx._source.remove(\"not_in_public_site_areas\")")

        actions.append(action)

    elasticsearch.helpers.bulk(es_client, actions)


def _handle_message(_, message):
    """Handle a message on the "nipsa_users_annotations" channel."""
    message_data = json.loads(message.body)
    if message_data["action"] == "nipsa":
        _add_or_remove_nipsa_flags(message_data["user_id"], add=True)
    elif message_data["action"] == "unnipsa":
        _add_or_remove_nipsa_flags(message_data["user_id"], add=False)


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
