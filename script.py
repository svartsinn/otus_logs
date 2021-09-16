import argparse
import glob
import json
import os
import re
from collections import defaultdict
from collections import Counter

parser = argparse.ArgumentParser(description='Processing log access.log')
parser.add_argument('-d', dest='dir', action='store', help='Path to directory with logfiles')
args = parser.parse_args()

files = []
current_dir = os.getcwd()
stat_dir = os.getcwd() + '/statistics'

ip_regex = r"\d{1,4}\.\d{1,3}\.\d{1,3}\.\d{1,3}"
method_regex = r"\] \"(POST|GET|PUT|DELETE|HEAD)"
time_regex = r"(\[.*\])"
url_regex = r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"
duration_regex = r"(\d*)$"

if not os.path.exists(stat_dir):
    os.makedirs(stat_dir)

os.chdir(args.dir)
for file in glob.glob("*.log"):
    files.append(file)

dict_ip = defaultdict(
    lambda: {'GET': 0, 'POST': 0, "PUT": 0, 'DELETE': 0, 'HEAD': 0}
)


def collect_statistics(logfile):
    """
    The function parses the file with regular expressions and counts the values of the fields
    :param logfile: a log file is sent to the input
    :return: returns a dictionary with the statistics of requests by the method and a list
    of dictionaries with the duration of requests
    """
    url_dict = {}
    url_list = []
    for line in logfile:
        ip_match = re.search(ip_regex, line)
        if ip_match is not None:
            ip = ip_match.group()
            method = re.search(method_regex, line)
            time = re.search(time_regex, line)
            url = re.search(url_regex, line)
            duration = re.search(duration_regex, line)
            if method is not None:
                dict_ip[ip][method.groups()[0]] += 1
            if (url is not None) and (time is not None) and (method is not None):
                url_dict['URL'] = ' '.join([method.groups()[0], url.group(), ip, time.groups()[0]])
                url_dict['TIME'] = int(duration.groups()[0])
                url_list.append(url_dict.copy())
    return dict_ip, url_list


for file in files:
    with open(file, 'r') as f:
        dict_ip, url_list = collect_statistics(f)

    longest_request = sorted(url_list, key=lambda k: k['TIME'], reverse=True)

    for key, values in dict_ip.items():
        c = Counter(values)
        values['TOTAL'] = sum(c.values())

    ip_list = []
    for key, value in sorted(dict_ip.items(), key=lambda x: x[1]['TOTAL'], reverse=True):
        ip_list.append([key, value['TOTAL']])

    result_file = {'most_frequent': ip_list[0:3],
                   'most_longest': longest_request[0:3],
                   'requests_stat': dict_ip}

    file_name = os.path.splitext(file)[0]
    print(f"Statistics for file {file}:\n")
    print("Top 3 IP addresses from which requests were made:\n")
    for el in ip_list[0:3]:
        print(f"For {el[0]} were made {el[1]} requests")
    print("\nTop 3 the longest request:\n")
    for el in longest_request[0:3]:
        print(el['URL'])
    print(f"{json.dumps(dict_ip, indent=4)}")
    print("======================\n\n\n")

    with open(stat_dir + '/' + f'stat_for_{file_name}.json', 'w') as f:
        f.write(json.dumps(result_file, indent=4))
