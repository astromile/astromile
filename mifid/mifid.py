import re

import urllib3


def url_bloomberg_base():
    return 'https://www.bloombergapa.com'


def url_bloomberg_history():
    return f'{url_bloomberg_base()}/historyfiles'


def url_bloomberg_file(fname):
    return f'{url_bloomberg_base()}/download?key={fname}'


def history():
    print('Requesting Bloomberg history files')
    http = urllib3.PoolManager()
    r: urllib3.response.HTTPResponse = http.request(method='GET', url=url_bloomberg_history())
    print('List of files received')
    for fname in re.findall('<a href="/download\\?key=(?P<name>BAPA-POST-\\d{8}-\\d{2}:\\d{2}\\.csv)">',
                            r.data.decode()):
        print(f'Loading {fname}')
        csv = http.request(method='GET', url=url_bloomberg_file(fname)).data.decode()
        print(csv)


if __name__ == '__main__':
    history()
