import argparse
import logging
import re


# Regex (allow IPv6)
LOG_REGEX = r'(?P<ip>[(\d\.\w\:)]+) - - \[(?P<date>.*?) (.*?)\] "(?P<method>\w+) (?P<request_path>.*?) HTTP/(?P<http_version>.*?)" (?P<status_code>\d+) (?P<response_size>\d+) "(?P<referrer>.*?)" "(?P<user_agent>.*?)"'
compiled = re.compile(LOG_REGEX)
logger = logging.getLogger(__name__)


def parse_line(line):
    """ Analize one Apache log line
        test line = 172.183.134.216 - - [12/Jul/2016:12:22:14 -0700] "GET /wp-content HTTP/1.0"       200 4980  "http://farmer-harris.com/category/index/" "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_8; rv:1.9.3.20) Gecko/2013-07-10 02:46:11 Firefox/9.0"
        result {'ip': '172.183.134.216', 'date': '12/Jul/2016:12:22:14', 'method': 'GET', 'request_path': '/wp-content', 'http_version': '1.0', 'status_code': '200', 'response_size': '4980', 'referrer': 'http://farmer-harris.com/category/index/', 'user_agent': 'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_8; rv:1.9.3.20) Gecko/2013-07-10 02:46:11 Firefox/9.0'}
        """
    match = compiled.match(line)
    if match is None:
        logger.warn('Not match for \n\t[{}]'.format(line))
        # sample 172.30.74.115 - - [20/Oct/2020:06:35:52 +0000] "OPTIONS / RTSP/1.0" 400 0 "-" "-"
        return None
    data = match.groupdict()
    return process_line(data)


def process_line(data):
    """ Analize a line to determine if we want it """

    skip_start = ['/fanstatic', '/server-status', '/saml2',
                  '/css/', '/base/', '/gsa/', '/?host',
                  '/apple-', '/favicon']

    for ss in skip_start:
        if data['request_path'].startswith(ss):
            return None

    if data['method'] != 'GET':
        return None

    return data


def parse_file(apache_log_path, output_path='results.txt', limit=0):
    f = open(apache_log_path, 'r')
    out = open(output_path, 'w')
    nf = open('not_found.txt', 'w')

    weigths = {
        'resource':
            {'regex': re.compile(r'(\/[A-Za-z_]+)?\/dataset\/[\w-]+\/resource\/[\w-]+'), 'total': 0},
        'dataset-search':
            {'regex': re.compile(r'(\/[A-Za-z_]+)?\/dataset\?(.*)'), 'total': 0},
        'dataset':
            {'regex': re.compile(r'(\/[A-Za-z_]+)?\/dataset\/[\w-]+'), 'total': 0},
        'datasets':
            {'regex': re.compile(r'(\/[A-Za-z_]+)?\/dataset(\/)?$'), 'total': 0},
        'harvest':
            {'regex': re.compile(r'(\/[A-Za-z_]+)?\/harvest\/[\w-]'), 'total': 0},
        'harvests':
            {'regex': re.compile(r'(\/[A-Za-z_]+)?\/harvest(\/)?$'), 'total': 0},
        'api-pkg-search':
            {'regex': re.compile(r'/api(/3)?/action/package_search.*'), 'total': 0},
        'api-pkg-show':
            {'regex': re.compile(r'/api(/3)?/action/package_show.*'), 'total': 0},
        'api-search':
            {'regex': re.compile(r'/api/search.*'), 'total': 0},
        'organization':
            {'regex': re.compile(r'(\/[A-Za-z_]+)?\/organization\/[\w-]+'), 'total': 0},
        'organization-search':
            {'regex': re.compile(r'(\/[A-Za-z_]+)?\/organization\?(.*)'), 'total': 0},
        'organizations':
            {'regex': re.compile(r'(\/[A-Za-z_]+)?\/organization(\/)?$'), 'total': 0},
        'group':
            {'regex': re.compile(r'(\/[A-Za-z_]+)?\/group\/[\w-]+'), 'total': 0},
        'group-search':
            {'regex': re.compile(r'(\/[A-Za-z_]+)?\/group\?(.*)'), 'total': 0},
        'groups':
            {'regex': re.compile(r'(\/[A-Za-z_]+)?\/group(\/)?$'), 'total': 0},
        'home':
            {'regex': re.compile(r'(\/[A-Za-z_]+)?\/$'), 'total': 0},
    }

    c = 0
    for line in f:
        c += 1
        if limit > 0 and c > limit:
            break
        logger.debug('Parsing {}'.format(line))
        data = parse_line(line)
        if data is None:
            continue
        out.write(data['request_path'] + "\n")

        found = False
        for name in weigths:
            print(name)
            rgx = weigths[name]['regex']
            match = rgx.match(data['request_path'])

            if match is not None:
                weigths[name]['total'] += 1
                found = True
                break

        if not found:
            nf.write(data['request_path'] + '\n')

    f.close()
    out.close()
    nf.close()

    print([{k: weigths[k]['total']} for k in weigths])


parser = argparse.ArgumentParser()
parser.add_argument("--apache_logs_path", type=str, default="apache.log", help="Path for the apache log file")
parser.add_argument("--output_path", type=str, default="results.txt", help="Destination file for URLs")
parser.add_argument("--limit", type=int, default=0, help="Limit lines to read from logs")
args = parser.parse_args()

parse_file(args.apache_logs_path, output_path=args.output_path, limit=args.limit)
