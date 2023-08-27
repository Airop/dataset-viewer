# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The HuggingFace Authors.

import logging

from libcommon.constants import QUEUE_COLLECTION_LOCKS, QUEUE_MONGOENGINE_ALIAS
from libcommon.queue import Lock
from mongoengine.connection import get_db

from mongodb_migration.check import check_documents
from mongodb_migration.migration import Migration


# connection already occurred in the main.py (caveat: we use globals)
class MigrationAddTtlToQueueLock(Migration):
    def up(self) -> None:
        # See https://docs.mongoengine.org/guide/migration.html#example-1-addition-of-a-field
        logging.info("If missing, add the ttl field to the locks")
        db = get_db(QUEUE_MONGOENGINE_ALIAS)
        db[QUEUE_COLLECTION_LOCKS].update_many({"ttl": {"$exists": False}}, [{"$set": {"ttl": None}}])  # type: ignore

    def down(self) -> None:
        logging.info("Remove the ttl field from all the locks")
        db = get_db(QUEUE_MONGOENGINE_ALIAS)
        db[QUEUE_COLLECTION_LOCKS].update_many({}, {"$unset": {"ttl": ""}})

    def validate(self) -> None:
        logging.info("Ensure that a random selection of locks have the 'ttl' field")

        check_documents(DocCls=Lock, sample_size=10)
