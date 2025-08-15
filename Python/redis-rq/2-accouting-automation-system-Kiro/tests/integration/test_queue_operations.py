"""Integration tests for Redis queue operations using RQService.

These tests verify that jobs are enqueued correctly and queue stats
are reported via the service with a fake Redis backend.
"""

from uuid import uuid4
from unittest.mock import patch

import pytest
from fakeredis import FakeRedis

from app.infrastructure.queue import RQService


@pytest.mark.integration
class TestRedisQueueOperations:
    def test_enqueue_and_queue_info_with_fake_redis(self):
        """Jobs are enqueued and reflected in queue info with FakeRedis."""
        fake = FakeRedis(decode_responses=True)

        # Patch redis.from_url so RQService uses FakeRedis
        with patch('app.infrastructure.queue.redis.from_url', return_value=fake):
            service = RQService(redis_url='redis://fake:6379/0', queue_name='test')

            job_id = uuid4()
            # Enqueue the worker function name; it will be resolved dynamically
            service.enqueue_job(
                function_name='trigger_n8n_workflow',
                job_id=job_id,
                image_data=b'\xff\xd8...\xff\xd9',
                filename='test.jpg',
                notion_database_id='1234567890abcdef1234567890abcdef',
                content_type='image/jpeg'
            )

            info = service.get_queue_info()
            assert info['name'] == 'test'
            assert info['length'] >= 1

            service.close()
