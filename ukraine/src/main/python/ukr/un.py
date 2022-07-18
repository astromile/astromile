import datetime
import os
import re
from typing import Union

import pandas as pd
import requests


class UNHR:
    NEX = r'\d+|\d+,\d+'

    EX = re.compile(
        fr'(a total of)?\s+(?P<total>{NEX})\s+' +
        fr'(?P<kind>killed|injured)\s+' +
        fr'\((?P<details>[a-z0-9,\s]+)\)'
    )

    DEX = re.compile(fr'(?P<n>{NEX})\s+(?P<kind>[a-z]+)')

    REX = fr'(\s|&nbsp;)+({NEX})\scasualties\s\((?P<killed>{NEX})\s+killed\s+and\s+(?P<injured>{NEX})\s+injured\)'

    DLEX = re.compile(fr'Government-controlled\sterritory:{REX}')
    LDNREX = re.compile(fr'territory\scontrolled.+:{REX}')
    UEX = re.compile(fr'other\sregions\sof\sUkraine.+:{REX}')

    def __init__(self, root='c:/data/ukr', load=True):
        self.root = root
        self.data = self.load_last_file() if load else pd.DataFrame()

    def last(self):
        last_date = self.data.last_valid_index()
        return last_date, self.data.loc[last_date]

    def update(self, silent=True, store=True, ndays=30):
        today = pd.to_datetime(datetime.date.today())
        if len(self.data) == 0:
            self.data = self.extract_all(
                dend=pd.to_datetime('2022-03-07') + pd.Timedelta(days=ndays),
                silent=silent
            )
        else:
            self.data = pd.concat([
                self.data.loc[:self.data.last_valid_index()],
                self.extract_all(
                    dstart=self.data.last_valid_index() + pd.Timedelta(days=1),
                    dend=min(today, self.data.last_valid_index() + pd.Timedelta(days=ndays))
                )
            ], axis=0)

        if store:
            self.store()

        return self.data

    def store(self):
        self.data.to_csv(os.path.join(self.root, f'un-{datetime.date.today()}.csv'))

    def load_last_file(self):
        files = sorted([f for f in os.listdir(self.root) if f.endswith('.csv')])
        if len(files) == 0:
            return pd.DataFrame()
        else:
            return self.load_from_file(os.path.join(self.root, files[-1]))

    @staticmethod
    def load_from_file(fname):
        df = pd.read_csv(
            fname,
            header=[0, 1],
            index_col=0,
            parse_dates=[0]
        )
        return df.astype('Int64')

    @staticmethod
    def url_at(d: Union[datetime.date, pd.Timestamp]):
        """
        Builds URL for a given date.
        E.g. for d = 2022-04-05:

        https://www.ohchr.org/en/news/2022/04/ukraine-civilian-casualty-update-3-april-2022

        :param d: Date.
        :return: URL for a given date.
        """
        fmt = 'https://www.ohchr.org/en/news/%Y/%m/ukraine-civilian-casualty-update-' \
              + f'%{"-" if os.name == "posix" else "#"}d-%B-%Y'
        return d.strftime(fmt).lower()

    @staticmethod
    def s2n(s):
        return int(s.replace(',', ''))

    @classmethod
    def extract(cls, d, silent=True):
        url = cls.url_at(d)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) '
                          + 'AppleWebKit/537.36 (KHTML, like Gecko) '
                          + 'Chrome/39.0.2171.95 Safari/537.36'
        }
        if not silent:
            print('getting content from', url)
        data = {}
        r = requests.get(url, headers=headers)
        if r.url != url:  ## => page redirected => ignore
            return data

        s = r.content.decode()

        end = 0
        for _ in range(2):
            m = cls.EX.search(s, pos=end)
            if m is None:
                return data
            end = m.end()
            kind = m.group('kind')
            data[kind] = {'total': cls.s2n(m.group('total'))}
            dm = cls.DEX.search(m.group('details'))
            while dm:
                data[kind][dm.group('kind')] = cls.s2n(dm.group('n'))
                dm = cls.DEX.search(m.group('details'), pos=dm.end())

        for region, rex in [('DL', cls.DLEX),
                            ('LDNR', cls.LDNREX),
                            ('U', cls.UEX)]:
            m = rex.search(s, pos=end)
            if m is None:
                print(s[end:end + 300], region, rex)
                raise RuntimeError
            end = m.end()
            for kind in ['killed', 'injured']:
                if kind not in data:
                    print(d)
                data[kind][region] = cls.s2n(m.group(kind))

        return data

    @classmethod
    def extract_all(cls, dstart=datetime.date(2022, 3, 7),
                    dend=pd.to_datetime(datetime.date.today()),
                    silent=False):
        one_day = pd.Timedelta(days=1)
        d = pd.to_datetime(dstart)
        today = dend
        data = {}
        missing = []
        while d <= today:
            dd = cls.extract(d)
            if len(dd) == 0:
                if 'k' in locals():
                    data.setdefault(k, pd.DataFrame()).at[d, :] = None
                else:
                    missing.append(d)
            else:
                for k, v in dd.items():
                    data.setdefault(k, pd.DataFrame()).at[
                        d, v.keys()
                    ] = v.values()
            if not silent:
                print(d, 'processed')
            d += one_day
        df = pd.DataFrame() if len(data) == 0 else pd.concat(data, axis=1)
        if len(missing) > 0:
            df = pd.concat([df, pd.DataFrame(index=missing)], axis=0).sort_index()
        return df.astype('Int64')


def ex_extract():
    print('testing UNHR capabilities')
    d = datetime.date(2022, 6, 13)
    df = UNHR.extract(d)
    print('data on', d, ':\n', df)

    df = UNHR().load_last_file()
    print('data cached:\n', df)


def load_all_and_store():
    UNHR(load=False).update(silent=False, store=True)


def update():
    UNHR(load=True).update(silent=False, store=True)


if __name__ == '__main__':
    UNHR().data.stack()
    # load_all_and_store()
