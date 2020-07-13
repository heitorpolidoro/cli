from wip_clis import gitlab
from pyutils import *


class _Gitlab(object):
    _cache = {'projects': {}}

    def __init__(self):
        self.gitlab = gitlab.Gitlab('https://gitlab.com', private_token=get_env_var('PRIVATE_TOKEN'))
        self.gitlab.auth()

    def __getattr__(self, item):
        return getattr(self.gitlab, item)

    @staticmethod
    def get_project(project_name=None):
        if project_name is None:
            project_name = run_and_return_output('git config --get remote.origin.url').split('/')[1].replace('.git', '')

        if project_name in _Gitlab._cache['projects']:
            return _Gitlab._cache['projects'][project_name]

        projects = Gitlab.projects.list(search=project_name)
        for p in projects:
            if p.name == project_name:
                _Gitlab._cache['projects'][project_name] = p
                return p

        exit('Project "%s" not found in GitLab' % project_name)

    @staticmethod
    def get_last_commit(branch=None):
        if branch is None:
            branch = get_current_branch()

        # Replacing any '/' into '%2F'
        branch = branch.replace('/', '%2F')

        try:
            content = Gitlab.get_project().commits.list(ref_name=branch)
            if content:
                return content[0].id
        except HTTPError as e:
            if e.response.status_code == 404:
                pass
            else:
                raise


Gitlab = _Gitlab()
