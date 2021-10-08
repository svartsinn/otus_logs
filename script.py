import argparse
import glob
import json
import os
import re
from collections import Counter

parser = argparse.ArgumentParser(description='Processing log access.log')
parser.add_argument('-d', dest='dir', action='store', help='Path to directory with logfiles')
args = parser.parse_args()

files = []
current_dir = os.getcwd()
stat_dir = os.getcwd() + '/statistics'

ip_regex = r"\d{1,4}\.\d{1,3}\.\d{1,3}\.\d{1,3}"
method_regex = r"\] \"(POST|GET|PUT|DELETE|HEAD|OPTIONS)"
time_regex = r"(\[.*\])"
url_regex = r"(POST|GET|PUT|DELETE|HEAD|OPTIONS) (.*) HTTP"
duration_regex = r"(\d*)$"

if not os.path.exists(stat_dir):
    os.makedirs(stat_dir)

if args.dir is None:
    os.chdir(current_dir)
    for file in glob.glob("*.log"):
        files.append(os.path.abspath(file))
elif os.path.isfile(args.dir):
    files.append(os.path.abspath(args.dir))
elif os.path.isdir(args.dir):
    os.chdir(args.dir)
    for file in glob.glob("*.log"):
        files.append(os.path.abspath(file))

methods_sum = {'GET': 0, 'POST': 0, "PUT": 0, 'DELETE': 0, 'HEAD': 0, 'OPTIONS': 0}


def fields_stat(logfile):
    """
    The function counts the number of methods in the file and the number of requests with different durations.
    :param logfile:
    :return:
    """
    url_list = []
    line_count = 0
    global methods_sum
    methods_sum = dict.fromkeys(methods_sum.keys(), 0)
    for line in logfile:
        method = re.search(method_regex, line)
        ip = re.search(ip_regex, line)
        time = re.search(time_regex, line)
        url = re.search(url_regex, line)
        duration = re.search(duration_regex, line)
        if ip is not None:
            line_count += 1
        if method is not None:
            methods_sum[method.groups()[0]] += 1
        if (ip is not None) and (url is not None) and (time is not None) and (method is not None):
            url_dict = {'ip': ip.group(),
                        'date': time.groups()[0],
                        'method': method.groups()[0],
                        'url': url.groups()[1],
                        'duration': int(duration.groups()[0])}
            url_list.append(url_dict.copy())
    return url_list, line_count


for file in files:
    with open(file, 'r') as f:
        result_stat, line_count = fields_stat(f)

    longest_request = sorted(result_stat, key=lambda k: k['duration'], reverse=True)

    collect = Counter(k['ip'] for k in result_stat)

    file_name = os.path.basename(file)
    print(f"Statistics for file {file}:\n")
    print("Top 3 IP addresses from which requests were made:\n")
    for elem in collect.most_common(3):
        print(f"For {elem[0]} were made {elem[1]} requests")
    print("\nTop 3 the longest request:\n")
    for elem in longest_request[0:3]:
        print(f"{json.dumps(elem, indent=4)}")
    print("\nStatistics for METHODS:\n")
    print(f"{json.dumps(methods_sum, indent=4)}")
    print("\nTotal number of requests:")
    print(line_count, end='\n')
    print("======================\n\n\n")

    result_file = {'most_frequent': collect.most_common(3),
                   'most_longest': longest_request[0:3],
                   'requests_stat': methods_sum,
                   'overall_requests': line_count}

    with open(stat_dir + '/' + f'stat_for_{file_name}.json', 'w') as f:
        f.write(json.dumps(result_file, indent=4))
