#!/usr/bin/env python

#  Copyright (C) 2016 Joshua Charles Campbell
#  Copyright (C) 2016 Eddie Antonio Santos

#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

"""
Integration tests for PartyCrasher's REST API.

**Assumes ElasticSearch is running and accessible AT localhost:9200!**

Starts a fresh version of PartyCrasher for each test. Note: we DO NOT ever
import PartyCrasher in this test!
"""


import datetime
import os
import random
import signal
import subprocess
import sys
import time
import unittest
import uuid

import requests


# Full path to ./rest_service.py
REST_SERVICE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                 'rest_service.py')


class RestServiceTestCase(unittest.TestCase):
    def setUp(self):
        self.port = random.randint(5000, 5999)
        self.origin = 'http://localhost:' + str(self.port)

        # Use currently activated Python (system-wide or in virtualenv).
        python_cmd = subprocess.check_output("which python",
                                             shell=True).rstrip()

        # Start PartyCrasher REST server.
        # Note: preexec_fn is "pre-execute function"
        #
        # os.setsid() is required to start the server in a new session in
        # Unix; Windows needs something else...
        self.rest_service = subprocess.Popen([python_cmd, REST_SERVICE_PATH,
                                              str(self.port)],
                                             preexec_fn=os.setsid)

        # Wait for the REST service to start up.
        time.sleep(1)

    @property
    def root_url(self):
        """
        The root URL of the REST service.
        """
        return self.origin + '/'

    def path_to(self, *args):
        """
        Create a URL path, relative to the current origin.
        """
        return '/'.join((self.origin,) + args)

    def test_alive(self):
        """
        Can we access the root path?
        """
        response = requests.get(self.root_url)
        assert response.status_code == 200

    def test_basic_cors(self):
        """
        Can we send a pre-flight header?
        Does it state that *any* origin can make non-idempotent requests?
        """
        assert is_cross_origin_accessible(self.root_url)

    def test_add_crash(self):
        """
        Add a single crash, globally;
        it must return its default bucket assignment.
        """
        assert is_cross_origin_accessible(self.path_to('reports'))

        # Make a new, unique database ID.
        database_id = str(uuid.uuid4())
        response = requests.post(self.path_to('reports'),
                                 json={'database_id': database_id})

        # TODO: Link header/Location header
        assert response.status_code == 201
        assert response.json()['crash']['database_id'] == database_id
        assert response.json()['crash']['bucket'] is not None
        # TODO: bucket url

    def test_add_crash_project(self):
        """
        Add a single crash to a project;
        it must return its default bucket assignment
        """

        url = self.path_to('alan_parsons', 'reports')
        assert is_cross_origin_accessible(url)

        # Make a new, unique database ID.
        database_id = str(uuid.uuid4())
        response = requests.post(url, json={'database_id': database_id})

        assert response.status_code == 201
        assert response.json()['crash']['database_id'] == database_id
        assert response.json()['crash']['bucket'] is not None
        assert response.json()['crash']['project'] == 'alan_parsons'

        # TODO: bucket url
        # TODO: ensure if URL project and JSON project conflict HTTP 400
        #       is returned

    def test_add_multiple(self):
        """
        Add multiple crashes to a single project;
        it must return a summary list of bucket assignments.
        """
        url = self.path_to('alan_parsons', 'reports')
        assert is_cross_origin_accessible(url)

        # Make a bunch of unique database IDs
        database_id_a = str(uuid.uuid4())
        database_id_b = str(uuid.uuid4())
        database_id_c = str(uuid.uuid4())
        response = requests.post(url,
                                 json=[
                                     {'database_id': database_id_a},
                                     {'database_id': database_id_b},
                                     {'database_id': database_id_c},
                                 ])

        assert response.status_code == 201
        assert response.json()['crashes'][0]['database_id'] == database_id_a
        assert response.json()['crashes'][0]['bucket'] is not None
        assert response.json()['crashes'][0]['project'] == 'alan_parsons'
        # TODO: bucket url

        assert response.json()['crashes'][1]['database_id'] == database_id_b
        assert response.json()['crashes'][1]['bucket'] is not None
        assert response.json()['crashes'][1]['project'] == 'alan_parsons'
        # TODO: bucket url

        assert response.json()['crashes'][2]['database_id'] == database_id_c
        assert response.json()['crashes'][2]['bucket'] is not None
        assert response.json()['crashes'][2]['project'] == 'alan_parsons'
        # TODO: bucket url
        # TODO: ensure if URL project and JSON project conflict HTTP 400
        #       is returned

    def test_get_crash(self):
        """
        Fetch a report from a project.

        Note that GETs are ALWAYS cross-origin accessible.
        """
        create_url = self.path_to('alan_parsons', 'reports')
        assert is_cross_origin_accessible(create_url)

        # Insert a new crash with a unique database ID.
        database_id = str(uuid.uuid4())
        response = requests.post(create_url, json={'database_id': database_id})
        assert response.status_code == 201

        report_url = self.path_to('alan_parsons', 'reports', database_id)
        response = requests.get(report_url)
        assert response.status_code == 200
        assert response.json()['crash']['database_id'] == database_id
        assert response.json()['crash']['bucket'] is not None
        assert response.json()['crash']['project'] == 'alan_parsons'
        # TODO: bucket url

    @unittest.skip
    def testGetCrashProject(self):
        """
        I'm not super sure what this could be for? (ambiguous)
        """
        raise NotImplementedError()
        # TODO: ensure if URL project and JSON project conflict HTTP 400
        #       is returned

    def test_dry_run(self):
        """
        Returns the bucket assignment were the given crash to be added.
        This crash must NOT be added, however.
        """
        url = self.path_to('alan_parsons', 'reports', 'dry-run')
        assert is_cross_origin_accessible(url)

        database_id = str(uuid.uuid4())
        response = requests.post(url, json={'database_id': database_id})

        assert response.status_code == 202
        assert response.json()['crash']['database_id'] == database_id
        assert response.json()['crash']['bucket'] is not None
        assert response.json()['crash']['project'] == 'alan_parsons'
        # TODO: bucket url

        # Try to find this crash... and fail!
        response = requests.get(self.path_to('alan_parsons', 'reports',
                                             database_id))
        assert response.status_code == 404

    def test_delete_crash(self):
        """
        Remove a report globally.
        """

        # Create a unique crash report.
        database_id = str(uuid.uuid4())
        create_url = self.path_to('alan_parsons', 'reports')
        assert is_cross_origin_accessible(create_url)

        response = requests.post(create_url,
                                 json={'database_id': database_id})
        assert response.status_code == 202

        report_url = self.path_to('alan_parsons/reports/', database_id)
        assert is_cross_origin_accessible(report_url)

        # Delete it.
        response = requests.delete(report_url)
        assert response.status_code == 204

        # Try to access it; you just can't do it!
        response = requests.get(report_url)
        assert response.status_code == 404

    def test_delete_crash_project(self):
        """
        Remove a report, referenced through its project.

        Note that this should also delete the report globally.
        """

        create_url = self.path_to('alan_parsons', 'reports')
        assert is_cross_origin_accessible(create_url)

        # Insert a new crash with a unique database ID.
        database_id = str(uuid.uuid4())
        response = requests.post(create_url, json={'database_id': database_id})
        assert response.status_code == 201

        report_url = self.path_to('alan_parsons', 'reports', database_id)
        assert is_cross_origin_accessible(report_url)

        # We can access it now...
        response = requests.get(report_url)
        assert response.status_code == 200
        # TODO: bucket url

        # Delete it.
        response = requests.delete(report_url)
        assert reponse.status_code in 204

        # Now we should NOT be able to access it!
        response = requests.get(report_url)
        assert response.status_code == 404

        # TODO: ensure if URL project and JSON project conflict HTTP 400
        #       is returned

    def test_get_project_bucket(self):
        """
        Fetch a bucket and its contents.
        """

        # Make a bunch of reports with IDENTICAL content!
        database_id_a = str(uuid.uuid4())
        database_id_b = str(uuid.uuid4())
        database_id_c = str(uuid.uuid4())
        # This is the only content for each report, so there must only be
        # *one* bucket that contains reports A, B, and C!
        tfidf_trickery = str(uuid.uuid4())

        create_url = self.path_to('alan_parsons', 'reports')
        assert is_cross_origin_accessible(create_url)

        # Create all dem duplicated reports!
        response = requests.post(create_url,
                                 json=[
                                     {'database_id': database_id_a,
                                      'tfidf_trickery': tfidf_trickery},
                                     {'database_id': database_id_b,
                                      'tfidf_trickery': tfidf_trickery},
                                     {'database_id': database_id_c,
                                      'tfidf_trickery': tfidf_trickery},
                                 ])
        assert response.status_code == 201

        # Now, look up ONE of the crashes; it should
        bucket_url = self.path_to('alan_parsons', 'buckets', '4.0',
                                  database_id_a)
        response = requests.get(bucket_url)

        assert response.status_code == 200
        # The bucket is named after the first crash... I guess?
        assert response.json()['bucket'] == database_id_a
        assert response.json()['number_of_reports'] == 3
        # Look at the top report; it must contain tfidf_trickery.
        assert (response.json()['top_reports'][0]['tfidf_trickery'] ==
                tfidf_trickery)

    def test_get_top_buckets(self):
        """
        Get top buckets for a given time frame.
        """
        now = datetime.datetime.utcnow()

        # Create a bunch of reports with IDENTICAL content
        database_id_a = str(uuid.uuid4())
        database_id_b = str(uuid.uuid4())
        database_id_c = str(uuid.uuid4())
        tfidf_trickery = str(uuid.uuid4())

        response = requests.post(self.path_to('alan_parsons', 'buckets'),
                                 json=[
                                     {'database_id': database_id_a,
                                      'tfidf_trickery': tfidf_trickery},
                                     {'database_id': database_id_b,
                                      'tfidf_trickery': tfidf_trickery},
                                     {'database_id': database_id_c,
                                      'tfidf_trickery': tfidf_trickery}]
                                 )
        assert response.status_code == 201

        # We should find our newly created reports as the most populous
        # bucket.
        bucket_url = self.path_to('alan_parsons', 'buckets', '4.0')
        response = requests.get(bucket_url, params={'since': str(now)})
        assert response.json()['since'] == str(now)
        assert response.json()['top_buckets'][0]['bucket'] == database_id_a
        assert response.json()['top_buckets'][0]['number_of_reports'] == 3

    def test_get_project_config(self):
        """
        Fetch per-project configuration.
        """
        response = requests.get(self.path_to('alan_parsons', 'config'))
        assert response.status_code == 200
        assert 0.0 <= float(response.json()['default_threshold']) <= 10.0

    @unittest.skip
    def test_change_project_config(self):
        """
        Patch the project's default threshold.
        """
        raise NotImplementedError

    def tearDown(self):
        # Kill the ENTIRE process group of the REST server.
        # This should really be the subprocess.Popen.terminate() behavior by
        # default...
        os.killpg(os.getpgid(self.rest_service.pid), signal.SIGTERM)
        self.rest_service.wait()


def is_cross_origin_accessible(path, origin='http://example.org'):
    """
    Returns True if the path is accessible at the given origin
    (default: example.org).

    Raises AssertionError otherwise.
    """

    response = requests.options(path, headers={'Origin': origin})
    assert response.status_code == 200
    assert is_allowed_origin(origin, response)

    return True


def is_allowed_origin(origin, response):
    """
    Returns True when origin is allowed by the OPTIONS response.

    Raises AssertionError otherwise.
    """
    assert 'Access-Control-Allow-Origin' in response.headers

    # Either we're allowing ALL...
    raw_origins = response.headers['Access-Control-Allow-Origin']
    if raw_origins.strip() == '*':
        return True

    # Or we're explicitly allowing this host.
    allowed_origins = [o.strip() for o in raw_origins.split(',')]
    assert origin in allowed_origins
    return True


if __name__ == '__main__':
    unittest.main()