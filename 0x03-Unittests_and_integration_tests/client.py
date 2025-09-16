import requests


class GithubOrgClient:
    """Simple client to fetch Github organization info."""

    def __init__(self, org_name):
        self.org_name = org_name

    def org(self):
        url = f"https://api.github.com/orgs/{self.org_name}"
        return requests.get(url).json()

    @property
    def _public_repos_url(self):
        data = self.org()
        return data.get('repos_url')

    def public_repos(self, license=None):
        repos_url = self._public_repos_url
        # If the attribute was patched with a Mock (callable), call it
        if callable(repos_url):
            repos_url = repos_url()
        repos = requests.get(repos_url).json()
        names = [r.get('name') for r in repos]
        if license:
            names = [r.get('name') for r in repos if r.get('license') and r.get('license').get('key') == license]
        return names

    @staticmethod
    def has_license(repo, license_key):
        lic = repo.get('license')
        if not lic:
            return False
        return lic.get('key') == license_key
