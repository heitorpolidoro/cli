from wip_clis.gitlab import Gitlab
from colors.colors import *
from pyutils.pyutils import *


class Job(object):
    _jobs_status = {}

    def __init__(self, gitlab_job):
        self._gitlab_job = gitlab_job
        self.retry_job = None
        if self.id in Job._jobs_status and self.status != Job._jobs_status[self.id]:
            notify('Job %s' % self.name, self.status)

        Job._jobs_status[self.id] = self.status

    def __getattr__(self, item):
        status = ['created', 'pending', 'running', 'success', 'canceled', 'failed']
        if item in status:
            return self.status == item
        return getattr(self._gitlab_job, item)

    def print_info(self, fixed_color=''):
        color_running = Bold if self.status == 'running' else ''

        print(fixed_color, color_running, self.name, end='\t')
        color = {
            'created': ['$f249'],
            'success': [Green, Bold],
            'running': [IBlue, Bold],
            'pending': [Yellow],
            'failed': [Red, Bold],
            'canceled': [Bold, Purple],
        }.get(self.status, ())

        # max len(color) = 8
        print(fixed_color, *color, '{0:8}'.format(self.status), end='\t')

        if self.status == 'running':
            fixed_color += Bold

        if self.duration:
            print(fixed_color, '$f249', convert_duration(self.duration), end='\t')

        if self.pending:
            jobs = list(filter(lambda j: Job(j).pending, Gitlab.get_project().jobs.list()))

            if self in jobs:
                print(fixed_color, *color, 'Position in queue: ', len(jobs) - jobs.index(self), end='\t')

        elif self.failed:
            print(self.web_url, end='\t')
        print()
