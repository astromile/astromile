import datetime
import logging
import os

import pandas as pd
import psycopg2
from sqlalchemy import create_engine

from ukr.util import init_logging


class DataBean:
    def get_reports(self):
        raise NotImplementedError

    def add_new_reports(self, data):
        raise NotImplementedError

    def get_monthly(self):
        raise NotImplementedError

    def add_new_monthly(self, monthly):
        raise NotImplementedError

    def get_current_info(self):
        raise NotImplementedError

    def add_new_current_info(self, subregions, cm, regional):
        raise NotImplementedError


class FileDataBean(DataBean):
    def __init__(self, root='.'):
        self.root = root

    def get_reports(self):
        last = self.get_last_file('un')
        if last is None:
            logging.info(f'No report files found in {self.root}')
            return pd.DataFrame()
        else:
            logging.info(f'Loading reports from {last}')
            df = self.load_from_file(last)
            logging.info(f'successfully loaded {len(df)} reports')
            return df

    def add_new_reports(self, data):
        logging.info(f'Saving {len(data)} reports')
        data.to_csv(fname := os.path.join(self.root, f'un-{datetime.date.today()}.csv'))
        logging.info(f'successfully stored reports in {fname}')

    def get_monthly(self):
        last = self.get_last_file('monthly')
        if last is None:
            logging.info(f'No monthly files found in {self.root}')
            return pd.DataFrame()
        else:
            logging.info(f'Loading monthly data from {last}')
            df = pd.read_csv(last)
            logging.info(f'successfully loaded {len(df.date.unique())} monthly tables')
            return df

    def add_new_monthly(self, monthly):
        logging.info(f'Saving {len(monthly)} monthly records')
        monthly.to_csv(fname := os.path.join(self.root, f'monthly-{datetime.date.today()}.csv'), index=False)
        logging.info(f'successfully stored monthly in {fname}')

    def get_current_info(self):
        last = self.get_last_file('cm')
        if last is None:
            logging.info(f'No current month info found in {self.root}')
            cm = pd.DataFrame()
        else:
            logging.info(f'Loading current month info from {last}')
            cm = pd.read_csv(last)

        if len(cm) > 0:
            aux_cols = ['label', 'rus_subregions', 'ukr_subregions']
            subregions = cm[aux_cols].rename(columns={c: c.split('_')[0] for c in aux_cols[1:]})
            cm.drop(columns=aux_cols, inplace=True)
            cm.set_index('date', inplace=True)
            cm.columns = pd.MultiIndex.from_tuples([c.split('_')[::-1] for c in cm.columns])
        else:
            subregions = pd.DataFrame()

        last = self.get_last_file('reg')
        if last is None:
            logging.info(f'No regional info found in {self.root}')
            regional = pd.DataFrame()
        else:
            logging.info(f'Loading regional info from {last}')
            regional = pd.read_csv(last)

        return subregions, cm, regional

    def add_new_current_info(self, subregions, cm, regional):
        DB.flatten_report_columns(cm)
        subregions = subregions.rename(columns={g: f'{g}_subregions' for g in ['rus', 'ukr']})
        cm = pd.concat([subregions, cm], axis=1)
        logging.info(f'Saving {len(cm)} current month records')
        cm.to_csv(fname := os.path.join(self.root, f'cm-{datetime.date.today()}.csv'), index_label='date')
        logging.info(f'successfully stored current month info in {fname}')

        logging.info(f'Saving {len(regional)} regional records')
        regional.to_csv(fname := os.path.join(self.root, f'reg-{datetime.date.today()}.csv'), index=False)
        logging.info(f'successfully stored regional data in {fname}')

    def get_last_file(self, prefix):
        files = sorted([f for f in os.listdir(self.root)
                        if f.startswith(prefix + '-') and f.endswith('.csv')])
        if len(files) == 0:
            return None
        else:
            return os.path.join(self.root, files[-1])

    @staticmethod
    def load_from_file(fname):
        df = pd.read_csv(
            fname,  # os.path.join(self.root, fname),
            header=[0, 1],
            index_col=0,
            parse_dates=[0]
        )
        return df.astype('Int64')


class DBConfig:
    def __init__(
            self,
            host='ec2-44-206-197-71.compute-1.amazonaws.com',
            port=5432,
            database='df5sec0ooaj9gg',
            user='idsbvwaiyxagtt',
            password='155d61af0b4ab4d57' + '8186b084ecf9e7196b529472aa1e3a7d292b77d4b7a3ff4a'[:-1]
    ):
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password

    def connect(self):
        return psycopg2.connect(host=self.host,
                                port=self.port,
                                database=self.database,
                                user=self.user,
                                password=self.password)


class DB(DataBean):
    def __init__(self, config=DBConfig()):
        self.config = config
        self.engine = create_engine(
            f'postgresql+psycopg2://{config.user}:{config.password}@{self.log_url}'
        )

    def get_reports(self):
        with self.engine.connect() as conn:
            logging.info(f'Loading reports from {self.log_url}')
            df = pd.read_sql_table(table_name='report', con=conn, index_col='date').drop(columns=['id'])
            column_map = {c: c.upper() for c in ['u', 'dl', 'ldnr']}
            df.columns = pd.MultiIndex.from_tuples([
                (c[1], column_map.get(c[0], c[0])) for c in [c.split('_') for c in df.columns]
            ])
            logging.info(f'successfully loaded {len(df)} reports')

        return df

    def add_new_reports(self, data):
        df = data.dropna()
        db_dates = self.get_report_dates()
        df = df.loc[~df.index.isin(db_dates)]
        if len(df) == 0:
            logging.info(msg := 'no new reports to save')
            return msg

        self.flatten_report_columns(df)
        df = df.astype(int).copy()
        df.index = df.index.date

        with self.engine.connect() as conn:
            logging.info(f'Persisting new reports to {self.log_url}')
            result = df.to_sql('report', con=conn, if_exists='append', index=True, index_label='date')
            logging.info(f'successfully inserted {len(df)} new reports')
        return result

    def get_report_dates(self):
        with self.engine.connect() as conn:
            return pd.read_sql_table('report', conn, columns=['date'], index_col='id').date

    def add_new_current_info(self, subregions, cm, regional):
        assert len(subregions) == len(cm)
        if len(subregions) == 0:
            logging.info(msg := 'No current month info to save')
            return msg
        db_dates = self.get_report_dates()
        db_subregions, db_cm, db_regional = self.get_current_info(db_dates=db_dates)

        subregions.index = pd.to_datetime(subregions.index)
        subregions = subregions.loc[~subregions.index.isin(db_subregions.index)].copy()  ## filter new data
        if len(subregions) == 0:
            logging.info('No new current month info to save')
        else:
            subregions.rename(columns={c: f'{c}_subregions' for c in ['rus', 'ukr']}, inplace=True)
            cm.index = pd.to_datetime(cm.index)
            cm = cm.loc[~cm.index.isin(db_cm.index)]
            self.flatten_report_columns(cm)

            cm = pd.concat([subregions, cm], axis=1).reset_index().rename(columns={'index': 'date'})
            idmap = db_dates[db_dates.isin(cm.date)].to_frame().reset_index().set_index('date')['id']
            cm['report_id'] = idmap.loc[cm.date].values
            cm.drop(columns=['date'], inplace=True)
            with self.engine.connect() as conn:
                logging.info(f'Persisting current month data to {self.log_url}')
                result = cm.fillna(0).to_sql('current_month', con=conn, if_exists='append', index=False)
                logging.info(f'successfully inserted {len(cm)} current month entries')

        if len(regional) == 0:
            logging.info(msg := 'No regional data to save')
            return result + '; ' + msg
        regional['date'] = pd.to_datetime(regional.date)
        regional = regional[~regional.date.isin(db_regional.date.unique())].copy()  ## filter new entries
        idmap = db_dates[db_dates.isin(regional.date.unique())].to_frame().reset_index().set_index('date')['id']
        regional['report_id'] = idmap.loc[regional.date].values
        regional.drop(columns=['date'], inplace=True)
        if len(regional) == 0:
            logging.info(msg := 'No new regional data to save')
            return f'{result}; {msg}'
        with self.engine.connect() as conn:
            logging.info(f'Persisting regional data to {self.log_url}')
            result2 = regional.to_sql('region', con=conn, if_exists='append', index=False)
            logging.info(f'successfully inserted {len(regional)} new regional entries')

        return f'{result}; {result2}'

    def add_new_monthly(self, monthly):
        if len(monthly) == 0:
            logging.info(msg := 'No monthly data to save')
            return msg
        db_dates = self.get_report_dates()
        db_monthly = self.get_monthly(db_dates=db_dates)
        monthly['date'] = pd.to_datetime(monthly.date)
        monthly = monthly[~monthly.date.isin(db_monthly.date.unique())].copy()  ## filter new entries
        db_dates = db_dates[db_dates.isin(monthly.date.unique())].to_frame().reset_index().set_index('date')['id']
        monthly['report_id'] = db_dates.loc[monthly.date].values
        monthly.drop(columns=['date'], inplace=True)
        if len(monthly) == 0:
            logging.info(msg := 'No new monthly data to save')
            return msg
        with self.engine.connect() as conn:
            logging.info(f'Persisting monthly data to {self.log_url}')
            self.flatten_report_columns(monthly)
            result = monthly.to_sql('monthly', con=conn, if_exists='append', index=False)
            logging.info(f'successfully inserted {len(monthly)} new monthly entries')
        return result

    def get_monthly(self, db_dates=None):
        with self.engine.connect() as conn:
            logging.info(f'Loading monthly data from {self.log_url}')
            df = pd.read_sql_table('monthly', conn)
            logging.info(f'successfully loaded {len(df)} monthly entries')
        return self.link_to_dates(df, db_dates)

    def link_to_dates(self, df, db_dates=None, by='report_id'):
        if db_dates is None:
            db_dates = self.get_report_dates()
        df['date'] = db_dates.loc[df[by]].values
        return df.drop(columns=[by])

    def get_current_info(self, db_dates=None):
        with self.engine.connect() as conn:
            logging.info(f'Loading current month infos from {self.log_url}')
            cm = pd.read_sql_table('current_month', conn)
            logging.info(f'successfully loaded {len(cm)} current month infos')

            logging.info(f'Loading regional numbers from {self.log_url}')
            regional = pd.read_sql_table('region', conn)
            logging.info(f'successfully loaded {len(regional)} regional entries')

        if db_dates is None:
            db_dates = self.get_report_dates()

        cm = self.link_to_dates(cm, db_dates).set_index('date')
        aux_cols = ['label', 'rus_subregions', 'ukr_subregions']
        subregions = cm[aux_cols].rename(columns={c: c.split('_')[0] for c in aux_cols[1:]})

        cm.drop(columns=aux_cols, inplace=True)
        cm.columns = pd.MultiIndex.from_tuples([c.split('_')[::-1] for c in cm.columns])

        regional = self.link_to_dates(regional, db_dates).sort_values('killed', ascending=False)

        return subregions, cm, regional

    @staticmethod
    def flatten_report_columns(df):
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = [c[1].lower() + '_' + c[0].lower() for c in df.columns]
        else:
            df.columns = [c.lower() for c in df.columns]

    @property
    def log_url(self):
        return f'{self.config.host}:{self.config.port}/{self.config.database}'


# def execute(self, sql, fetch=True):
#     conn = None
#     try:
#         conn = self.config.connect()
#         cur = conn.cursor()
#
#         cur.execute(sql)
#
#         if fetch:
#             return cur.fetchall()
#
#         conn.commit()
#         return cur.statusmessage
#
#     except (Exception, psycopg2.DatabaseError) as error:
#
#         print(error)
#
#     finally:
#
#         if conn is not None:
#             conn.close()


def test_db():
    init_logging(level=logging.DEBUG)
    db = DB()
    # data = db.get_reports()
    monthly = db.get_monthly()
    print(monthly)

    # unhr = UNHR()
    # r = db.get_report_dates()
    # r = db.add_reports(unhr.data)
    # r = db.get_reports()
    # print(r)
    # print(r['killed'])
    # print(db.execute('select * from yearly'))


if __name__ == '__main__':
    test_db()
