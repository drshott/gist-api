from fastapi.testclient import TestClient
import unittest
import responses
from requests.exceptions import ConnectionError, Timeout


from app import APP


class AppTest(unittest.TestCase):

    def setUp(self):
        self.app = TestClient(APP)
        self.test_github_url = f'https://api.github.com/users/octocat/gists?per_page=100'
        self.octocat_json = {'url': 'https://api.github.com/gists/6cad326836d38bd3a7ae',
                 'forks_url': 'https://api.github.com/gists/6cad326836d38bd3a7ae/forks',
                 'commits_url': 'https://api.github.com/gists/6cad326836d38bd3a7ae/commits',
                 'id': '6cad326836d38bd3a7ae', 'node_id': 'MDQ6R2lzdDZjYWQzMjY4MzZkMzhiZDNhN2Fl',
                 'git_pull_url': 'https://gist.github.com/6cad326836d38bd3a7ae.git',
                 'git_push_url': 'https://gist.github.com/6cad326836d38bd3a7ae.git',
                 'html_url': 'https://gist.github.com/octocat/6cad326836d38bd3a7ae', 'files': {
                'hello_world.rb': {'filename': 'hello_world.rb', 'type': 'application/x-ruby', 'language': 'Ruby',
                                   'raw_url': 'https://gist.githubusercontent.com/octocat/6cad326836d38bd3a7ae/raw/db9c55113504e46fa076e7df3a04ce592e2e86d8/hello_world.rb',
                                   'size': 175}}, 'public': True, 'created_at': '2014-10-01T16:19:34Z',
                 'updated_at': '2024-01-14T06:42:08Z', 'description': 'Hello world!', 'comments': 281, 'user': None,
                 'comments_url': 'https://api.github.com/gists/6cad326836d38bd3a7ae/comments',
                 'owner': {'login': 'octocat', 'id': 583231, 'node_id': 'MDQ6VXNlcjU4MzIzMQ==',
                           'avatar_url': 'https://avatars.githubusercontent.com/u/583231?v=4', 'gravatar_id': '',
                           'url': 'https://api.github.com/users/octocat', 'html_url': 'https://github.com/octocat',
                           'followers_url': 'https://api.github.com/users/octocat/followers',
                           'following_url': 'https://api.github.com/users/octocat/following{/other_user}',
                           'gists_url': 'https://api.github.com/users/octocat/gists{/gist_id}',
                           'starred_url': 'https://api.github.com/users/octocat/starred{/owner}{/repo}',
                           'subscriptions_url': 'https://api.github.com/users/octocat/subscriptions',
                           'organizations_url': 'https://api.github.com/users/octocat/orgs',
                           'repos_url': 'https://api.github.com/users/octocat/repos',
                           'events_url': 'https://api.github.com/users/octocat/events{/privacy}',
                           'received_events_url': 'https://api.github.com/users/octocat/received_events',
                           'type': 'User', 'site_admin': False}, 'truncated': False}

    def test_index(self):
        """
        testing index page for application
        will return guidance lines in case no username is provided
        """
        #act
        response = self.app.get('/')
        #assert
        self.assertEqual(response.status_code, 200)
        self.assertEqual(str(response.text),
                         'Welcome to gist interface API, Please provide an Username to get gists eg. /octocat')

    def test_user_public_gist_ok(self):
        """
        check for response for user octocat
        the only test that will require an internet connection
        """
        #act
        response = self.app.get('/octocat')
        #assert
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json()['items'], list)

    @responses.activate
    def test_user_public_gist_paginated(self):
        """
        return a paginated response if acquired result count is more than 50
        """
        # a GitHub link header showing next page
        link_header_next = (
            '<https://api.github.com/user/583231/gists?per_page=100&page=2>; rel="next"'
        )
        # a GitHub link header showing no next page
        link_header_last = (
            '<https://api.github.com/user/583231/gists?per_page=100&page=1>; rel="prev"'
        )
        # mocking response of 1st GitHub api call
        responses.get(
            url=self.test_github_url,
            headers={'link': link_header_next},
            json=[self.octocat_json for i in range(60)]
        )
        # mocking response of GitHub api call made using next url in link header
        responses.get(
            url='https://api.github.com/user/583231/gists?per_page=100&page=2',
            headers={'link': link_header_last},
            json=[self.octocat_json]
        )
        #act
        response = self.app.get('/octocat')
        #assert
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['page'], 1)
        self.assertEqual(response.json()['total'], 61)

    @responses.activate
    def test_user_public_gist_rate_limit_403(self):
        # mocking GitHub api response with rate limit error
        responses.get(
            url=self.test_github_url,
            json={'message': "API rate limit exceeded for XX.XX.XX.XX. (But here's the good news: Authenticated "
                             "requests get a higher rate limit. Check out the documentation for more details.)",
                  'documentation_url': 'https://docs.github.com/rest/overview/resources-in-the-rest-api#rate-limiting'},
            status=403
        )
        # act
        response = self.app.get('/octocat')
        # assert
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()['message'],
                         'Rate Limit for GitHub API has been exceeded please try after 1 hour')

    @responses.activate
    def test_user_public_gist_forbidden_403(self):
        # mocking github api response for forbidden error
        responses.get(
            url=self.test_github_url,
            status=403
        )
        # act
        response = self.app.get('/octocat')
        # assert
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()['message'], 'Operation not allowed in GitHub')

    @responses.activate
    def test_user_public_gist_404(self):
        # mocking GitHub api response with not found error
        responses.get(
            url=self.test_github_url,
            status=404
        )
        # act
        response = self.app.get('/octocat')
        # assert
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()['message'],
                         'User/Resource not found or permissions are missing')

    @responses.activate
    def test_user_public_gist_raises_connection_error_503(self):
        # mocking GitHub api call with a perceived connection error
        responses.get(
            url=self.test_github_url,
            body=ConnectionError('Connection error was raised')
        )
        # act
        response = self.app.get('/octocat')
        # assert
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json()['message'],
                         'Connection error was raised')

    @responses.activate
    def test_user_public_gist_raises_timeout_error_504(self):
        # mocking GitHub api call with a perceived timeout error
        responses.get(
            url=self.test_github_url,
            body=Timeout('Connection to server timed out')
        )
        # act
        response = self.app.get('/octocat')
        # assert
        self.assertEqual(response.status_code, 504)
        self.assertEqual(response.json()['message'],
                         'Connection to server timed out')


if __name__ == "__main__":
    unittest.main()
