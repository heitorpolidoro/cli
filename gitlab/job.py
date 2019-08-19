from datetime import datetime, timedelta

from colors import *
from utils import *


class Job(object):
    def __init__(self):
        self.id = None
        self.name = None
        self.status = None
        self.duration = None
        self.web_url = None
        self.retry_job = None
        self._creation_date = None
        
    def __getattr__(self, item):
        status = ['created', 'pending', 'running', 'success', 'canceled', 'failed']
        if item in status:
            return self.status == item
        super(Job, self).__getattr__(item)

    @property
    def creation_date(self):
        if self._creation_date is None:
            # Timezone
            self._creation_date = \
                datetime.strptime(re.sub('\..*', '', self.created_at), '%Y-%m-%dT%H:%M:%S') - timedelta(hours=3)
        return self._creation_date

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
        # elif self.status != 'canceled':
        #     print(fixed_color, '$f249', re.sub('\..*', '', str(datetime.now() - self.creation_date)), end='\t')

        if self.pending:
            jobs = Job.get_project_jobs('pending')

            if self in jobs:
                print(fixed_color, *color, 'Position in queue: ', len(jobs) - jobs.index(self), end='\t')

        elif self.failed:
            print(self.web_url, end='\t')
        print()

    @staticmethod
    def get_project_jobs(status=None):
        if status is None:
            scope = ''
        elif isinstance(status, str):
            scope = 'scope[]=%s' % status
        elif isinstance(status, list):
            scope = '&'.join('scope[]=%s' % s for s in status)

        jobs = Requests.get_content('https://gitlab.com/api/v4/projects/${GITLAB_PROJECT}/jobs?%s' % scope,
                                    headers={'PRIVATE-TOKEN': '${PRIVATE_TOKEN}'}, clazz=Job)
        if not isinstance(jobs, list):
            jobs = [jobs]
        return jobs
    
    def __gt__(self, other):
        return self.id > other.id

    def __eq__(self, other):
        return self.id == other.id
