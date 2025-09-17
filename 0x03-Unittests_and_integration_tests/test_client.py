#!/usr/bin/env python3
import unittest
from unittest.mock import patch, Mock
from client import GithubOrgClient
import fixtures


class TestGithubOrgClient(unittest.TestCase):
	@patch('client.requests.get')
	def test_org(self, mock_get):
		# parametrize with a couple of org names
		for org_name in ('google', 'abc'):
			mock_get.return_value.json.return_value = {"login": org_name}
			gh = GithubOrgClient(org_name)
			self.assertEqual(gh.org(), {"login": org_name})
			mock_get.assert_called_with(f"https://api.github.com/orgs/{org_name}")

	def test_public_repos_url(self):
		payload = {"repos_url": "https://api.github.com/orgs/test/repos"}
		with patch.object(GithubOrgClient, 'org', return_value=payload):
			gh = GithubOrgClient('test')
			self.assertEqual(gh._public_repos_url, payload['repos_url'])

	@patch('client.requests.get')
	def test_public_repos(self, mock_get):
		# Mock the property to return a url, and mock requests.get to return repos
		mock_get.return_value.json.return_value = fixtures.repos_payload
		with patch.object(GithubOrgClient, '_public_repos_url', new_callable=Mock) as mock_prop:
			mock_prop.return_value = 'https://api.github.com/orgs/test/repos'
			gh = GithubOrgClient('test')
			repos = gh.public_repos()
			self.assertEqual(repos, fixtures.expected_repos)
			mock_prop.assert_called()
			mock_get.assert_called()

	def test_has_license(self):
		cases = [
			({"license": {"key": "my_license"}}, "my_license", True),
			({"license": {"key": "other_license"}}, "my_license", False),
		]
		for repo, license_key, expected in cases:
			with self.subTest(repo=repo, license_key=license_key):
				self.assertEqual(GithubOrgClient.has_license(repo, license_key), expected)


class TestIntegrationGithubOrgClient(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		# Patch requests.get so that .json() returns different payloads
		cls.get_patcher = patch('client.requests.get')
		mock_get = cls.get_patcher.start()

		def side_effect(url, *args, **kwargs):
			m = Mock()
			if url == fixtures.org_payload['repos_url']:
				m.json.return_value = fixtures.repos_payload
			else:
				m.json.return_value = fixtures.org_payload
			return m

		mock_get.side_effect = side_effect

	@classmethod
	def tearDownClass(cls):
		cls.get_patcher.stop()

	def test_public_repos_integration(self):
		gh = GithubOrgClient(fixtures.org_payload['login'])
		repos = gh.public_repos()
		self.assertEqual(repos, fixtures.expected_repos)
		repos_with_license = gh.public_repos(license='apache-2.0')
		self.assertEqual(repos_with_license, fixtures.apache2_repos)


if __name__ == '__main__':
	unittest.main()

