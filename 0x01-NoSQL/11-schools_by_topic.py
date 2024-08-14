#!/usr/bin/env python3

"""Where can I learn Python? """


def schools_by_topic(mongo_collection, topic):
    """Where can I learn Python?"""
    topic_filter = {
        "topics": {
            "$elemMatch": {"$eq": topic},
        },
    }
    return [doc for doc in mongo_collection.find(topic_filter)]
