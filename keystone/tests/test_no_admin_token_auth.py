# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2013 OpenStack Foundation
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import os
import webtest

from keystone import tests


def _generate_paste_config():
    # Generate a file, based on keystone-paste.ini, that doesn't include
    # admin_token_auth in the pipeline

    with open(tests.etcdir('keystone-paste.ini'), 'r') as f:
        contents = f.read()

    new_contents = contents.replace(' admin_token_auth ', ' ')

    with open(tests.tmpdir('no_admin_token_auth-paste.ini'), 'w') as f:
        f.write(new_contents)


class TestNoAdminTokenAuth(tests.TestCase):
    def setUp(self):
        super(TestNoAdminTokenAuth, self).setUp()
        self.load_backends()

        _generate_paste_config()

        self.admin_app = webtest.TestApp(
            self.loadapp(tests.tmpdir('no_admin_token_auth'), name='admin'),
            extra_environ=dict(REMOTE_ADDR='127.0.0.1'))

    def tearDown(self):
        self.admin_app = None
        os.remove(tests.tmpdir('no_admin_token_auth-paste.ini'))
        super(TestNoAdminTokenAuth, self).tearDown()

    def test_request_no_admin_token_auth(self):
        # This test verifies that if the admin_token_auth middleware isn't
        # in the paste pipeline that users can still make requests.

        # Note(blk-u): Picked /v2.0/tenants because it's an operation that
        # requires is_admin in the context, any operation that requires
        # is_admin would work for this test.
        REQ_PATH = '/v2.0/tenants'

        # If the following does not raise, then the test is successful.
        self.admin_app.get(REQ_PATH, headers={'X-Auth-Token': 'NotAdminToken'},
                           status=401)
