from .base import BaseAPITest
import os
import re
import unittest

@unittest.skipIf(not os.environ.get('TEST_WITH_ROOT_WORKERS'),
    "not running fork worker as root")
class TestForkWorkerRunningAsRoot(BaseAPITest):
    def test_running_job_as_root_should_fail(self):
        callback_server = self.create_callback_server([200])

        user = 'root'
        post_response = self.post(self.jobs_url, {
            'commandLine': ['true'],
            'user': user,
            'callbacks': {
                'error': callback_server.url,
            },
        })

        webhook_data = callback_server.stop()
        expected_data = [
            {
                'status': 'error',
                'jobId': post_response.DATA['jobId'],
                'errorMessage': 'Refusing to execute job as root user'
            },
        ]
        self.assertEqual(expected_data, webhook_data)


    def test_job_user_and_group(self):
        callback_server = self.create_callback_server([200])

        user = 'nobody'
        primarygroup = 'nobody'
        self.post(self.jobs_url, {
            'commandLine': ['id'],
            'user': user,
            'callbacks': {
                'ended': callback_server.url,
            },
        })

        webhook_data = callback_server.stop()
        id_result = webhook_data[0]['stdout']

        actual_user = self._find_match(r"uid=\d+\((\w+)\)", id_result)
        actual_primarygroup = self._find_match(r"gid=\d+\((\w+)\)", id_result)

        self.assertEqual(user, actual_user)
        self.assertEqual(primarygroup, actual_user)

    def _find_match(self, regexp, target):
        match = re.search(regexp, target)
        if match:
            return match.group(1)
        else:
            return ''
