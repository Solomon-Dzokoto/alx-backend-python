org_payload = {
    "login": "google",
    "repos_url": "https://api.github.com/orgs/google/repos"
}

repos_payload = [
    {"name": "repo1", "license": {"key": "apache-2.0"}},
    {"name": "repo2", "license": {"key": "bsd-3-clause"}},
    {"name": "apache", "license": {"key": "apache-2.0"}},
]

expected_repos = [r['name'] for r in repos_payload]

apache2_repos = [r['name'] for r in repos_payload if r.get('license', {}).get('key') == 'apache-2.0']
