from collections import OrderedDict, namedtuple
import copy

from contracts.utils import check_isinstance

import duckietown_utils as dtu
from easy_regression.conditions.interface import RTCheck, RTParseError


__all__ = [
    'RegressionTest',
    'ChecksWithComment',
]


ChecksWithComment = namedtuple('ChecksWithComment', ['checks', 'comment'])

class RegressionTest(object):
    
    def __init__(self, logs, processors=[], analyzers=[], checks=[], topic_videos=[]):
        self.logs = logs
        self.processors = processors
        self.analyzers = analyzers
        self.topic_videos = topic_videos
        
        check_isinstance(checks, list)
       
        try:
            self.cwcs = parse_list_of_checks(checks)
        except RTParseError as e:
            msg = 'Cannot parse list of checks.'
            msg += '\n' + dtu.indent(dtu.yaml_dump_pretty(checks), '', 'parsing: ')
            dtu.raise_wrapped(RTParseError, e, msg, compact=True)

    @dtu.contract(returns='list(str)')
    def get_processors(self):
        return self.processors

    @dtu.contract(returns='list(str)')
    def get_analyzers(self):
        return self.analyzers
    
    def get_logs(self, algo_db):
        logs = OrderedDict()
        for s in self.logs:
            logs.update(algo_db.query(s))
        return logs
    
    def get_topic_videos(self):
        return self.topic_videos
    
    def get_checks(self):
        return self.cwcs
    
def parse_list_of_checks(checks):
    checks = copy.deepcopy(checks)
    cwcs = []
    for c in checks:
        desc = c.pop('desc', None)
        cond = c.pop('cond')
        if c:
            msg = 'Spurious fields: %s' % list(c)
            raise ValueError(msg)
        lines = [_.strip() for _ in cond.strip().split('\n') if _.strip()]
        
        cwc_checks = [RTCheck.from_string(_) for _ in lines]
        cwc = ChecksWithComment(checks=cwc_checks, comment=desc)
        cwcs.append(cwc)
    return cwcs


    