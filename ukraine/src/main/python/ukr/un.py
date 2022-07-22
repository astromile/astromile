import datetime
import logging
import re
from typing import Union

import pandas as pd
import requests

from ukr.data import DataBean, FileDataBean, DB
from ukr.util import i_am_on_server, default_root, init_logging


class UNHR:
    NEX = r'\d+|\d+,\d+'

    EX = re.compile(
        fr'(a total of)?\s*(?P<total>{NEX})\s+' +
        fr'(?P<kind>killed|injured)\s+' +
        fr'\((?P<details>[a-z0-9,\s]+)\)'
    )

    DEX = re.compile(fr'(?P<n>{NEX})\s+(?P<kind>[a-z]+)')

    REX = fr'(\s|&nbsp;)+({NEX})\scasualties\s\((?P<killed>{NEX})\s+killed\s+and\s+(?P<injured>{NEX})\s+injured\)'

    DLEX = re.compile(fr'Government-controlled\sterritory:{REX}')
    LDNREX = re.compile(fr'territory\scontrolled.+:{REX}')
    UEX = re.compile(fr'other\sregions\sof\sUkraine.+:{REX}')

    CMEX = re.compile(r'From\s1\sto\s(?P<end>\d+)\s(?P<month>[A-Z][a-z]+)\s(?P<year>\d+),\s'
                      + fr'OHCHR\srecorded\s({NEX})\scivilian\scasualties:')

    CMRU = re.compile(fr'(?P<killed>{NEX})\skilled\sand\s(?P<injured>{NEX})\sinjured\sin\s'
                      + fr'(?P<subregions>{NEX})\ssettlements.*?Russian')

    CMGO = re.compile(fr'(?P<killed>{NEX})\skilled\sand\s(?P<injured>{NEX})\sinjured\sin\s'
                      + fr'(?P<subregions>{NEX})\ssettlements.*?Government')

    def __init__(self,
                 data_bean: DataBean = FileDataBean(default_root()),
                 load=True):
        self.data_bean = data_bean
        self.root = default_root()
        self.summary = {}
        if load:
            monthly = self.data_bean.get_monthly().rename(columns={'month': 'Period'})
            if len(monthly) > 0:
                self.summary = {
                    pd.to_datetime(d).date(): g.drop('date', axis=1)
                    for d, g in monthly.groupby('date')
                }
            self.data = self.data_bean.get_reports()
        else:
            self.data = pd.DataFrame()
        self.cm = {}

    def last(self):
        last_date = self.data.last_valid_index()
        return last_date, self.data.loc[last_date]

    def update(self, silent=True, store=True, ndays=30):
        # noinspection PyTypeChecker
        today = pd.to_datetime(datetime.date.today())
        if len(self.data) == 0:
            self.data, self.summary, self.cm = self.extract_all(
                dend=pd.to_datetime('2022-03-07') + pd.Timedelta(days=ndays),
                silent=silent
            )
        else:
            lvi = self.data.last_valid_index()
            data, summary, cm = self.extract_all(dstart=lvi + pd.Timedelta(days=1),
                                                 dend=min(today, lvi + pd.Timedelta(days=ndays)))
            self.data = pd.concat([self.data.loc[:lvi], data], axis=0)
            self.summary |= summary
            self.cm |= cm

        if store:
            self.store()

        return self.data

    def store(self):
        self.data_bean.add_new_reports(self.data)

        self.data_bean.add_new_monthly(self.monthly)

    @property
    def monthly(self):
        if len(self.summary) == 0:
            return pd.DataFrame()
        else:
            def cleanup(df):
                df = df[df.Period != 'Total'].set_index('Period')
                df.columns = [c.lower() for c in df.columns]
                return df

            return pd.concat(
                {d: cleanup(s) for d, s in self.summary.items()},
                axis=1
            ).astype('Int64').stack(level=0).reset_index().rename(columns={
                'Period': 'month',
                'level_1': 'date'
            }).sort_values(
                'date'
            )

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
              + f'%{"-" if i_am_on_server() else "#"}d-%B-%Y'
        return d.strftime(fmt).lower()

    @staticmethod
    def s2n(s):
        return int(s.replace(',', ''))

    @classmethod
    def extract_summary(cls, s):
        try:
            df = pd.read_html(s, match='24-28 February', header=0)[0]
            return df.rename(columns={df.columns[0]: 'Period'})
        except ValueError as e:
            logging.debug(f'cannot extract monthly summary: {e}')
            return None

    @classmethod
    def extract_current_month(cls, s):
        m = cls.CMEX.search(s)
        if m is None:
            return None, None, None
        end = m.end()
        last_day = m.group('end')
        month = m.group('month')
        year = m.group('year')
        label = f'{year}-{month}-{last_day}'

        data = {}
        for _ in range(2):
            m = cls.EX.search(s, pos=end)
            if m is None:
                return label, data, None
            end = m.end()

            kind = m.group('kind')
            data[kind] = {'total': cls.s2n(m.group('total'))}
            dm = cls.DEX.search(m.group('details'))
            while dm:
                data[kind][dm.group('kind')] = cls.s2n(dm.group('n'))
                dm = cls.DEX.search(m.group('details'), pos=dm.end())

        groups = ['killed', 'injured', 'subregions']
        m = cls.CMRU.search(s, pos=end)
        if m is None:
            return label, data, None
        end = m.end()
        data['rus'] = {g: cls.s2n(m.group(g)) for g in groups}

        m = cls.CMGO.search(s, pos=end)
        if m is None:
            return label, data, None
        data['ukr'] = {g: cls.s2n(m.group(g)) for g in groups}

        df = pd.read_html(s[m.end():], match='Region', header=0)[0].drop(columns=['Total'])

        return label, data, df

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
        r = requests.get(url, headers=headers)
        if r.url != url:  ## => page redirected => ignore
            return {}, None, {}

        s = r.content.decode()

        data = cls.extract_data(s)
        summary = cls.extract_summary(s)
        lbl, info, regional = cls.extract_current_month(s)
        cm = {'label': lbl, 'info': info, 'regional': regional} if lbl else {}
        return data, summary, cm

    @classmethod
    def extract_data(cls, s):
        end = 0
        data = {}
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
                data[kind][region] = cls.s2n(m.group(kind))

        return data

    # noinspection PyTypeChecker
    @classmethod
    def extract_all(cls, dstart=datetime.date(2022, 3, 7),
                    dend=pd.to_datetime(datetime.date.today()),
                    silent=False):
        one_day = pd.Timedelta(days=1)
        d = pd.to_datetime(dstart)
        today = dend
        data = {}
        summary = {}
        cm = {}
        missing = []
        k = None
        while d <= today:
            dd, dsum, dcm = cls.extract(d)

            if len(dd) == 0:
                if k is not None:
                    data.setdefault(k, pd.DataFrame()).at[d, :] = None
                else:
                    missing.append(d)
            else:
                for k, v in dd.items():
                    data.setdefault(k, pd.DataFrame()).at[
                        d, v.keys()
                    ] = v.values()

            if dsum is not None:
                summary[d.date()] = dsum

            if dcm:
                cm[d.date()] = dcm

            if not silent:
                print(d, 'processed', '' if len(dd) == 0 else 'data',
                      '' if dsum is None or len(dsum) == 0 else 'monthly', '' if len(dcm) == 0 else 'cm')
            d += one_day
        df = pd.DataFrame() if len(data) == 0 else pd.concat(data, axis=1)
        if len(missing) > 0:
            df = pd.concat([df, pd.DataFrame(index=missing)], axis=0).sort_index()
        return df.astype('Int64'), summary, cm


def ex_extract():
    print('testing UNHR capabilities')
    d = datetime.date(2022, 6, 13)
    df = UNHR.extract(d)
    print('data on', d, ':\n', df)

    df = UNHR().data
    print('data cached:\n', df)


def load_all_and_store():
    UNHR(load=False).update(silent=False, store=True)


def update():
    UNHR(load=True).update(silent=False, store=True)


if __name__ == '__main__':
    init_logging()
    # UNHR(DB()).update(store=True)
    DB().add_new_monthly(UNHR().monthly)
    # for c in UNHR().data.columns:
    #     print(c[1] + '_' + c[0], 'INT NOT NULL,')
    # data, monthly, cm = UNHR.extract(pd.to_datetime('2022-07-04'))
    # print(data)
    # s = requests.get(UNHR.url_at(pd.to_datetime('2022-06-18'))).content.decode()
    # lbl, data, df = UNHR.extract_current_month(s)
    # print(lbl, data)
    # print(df)
    # byMonth = UNHR.extract_summary(s)
    # print(byMonth)
    # UNHR().data.stack()
    # load_all_and_store()
