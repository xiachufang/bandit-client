# coding: utf-8
import requests
import datetime
import simplejson
import hashlib


class BanditApiError(Exception):

    def __init__(self, arg):
        self.args = [arg]


class BanditSendPool(object):

    def __init__(self, url):
        self.url = url
        self.clear()

    def clear(self):
        self.pool = []
        self.last_send_time = datetime.datetime.now()


class BanditInterface(object):

    def sign(self, d):
        md5_str = ''
        for key, value in sorted(d.items(), key=lambda x: x[0]):
            if isinstance(value, unicode):
                value = value.encode('utf8')
            else:
                value = str(value)
            if isinstance(value, str):
                md5_str += "%s%s" % (key, value)
        md5_str += str(self.secret_key)
        sign = hashlib.md5(md5_str).hexdigest()
        return sign

    def session(self):
        if not self._session:
            self._session = requests.session()
        return self._session

    def post(self, *args, **kwargs):
        return self.session().post(*args, timeout=self.timeout, **kwargs)

    def get(self, *args, **kwargs):
        return self.session().get(*args, timeout=self.timeout, **kwargs)

    def verify(self, d):
        sign = d.pop('signature')
        if sign == self.sign(d):
            return True
        return False

    def _signature(self, data):
        return dict(zip(data.keys() + ['signature'], data.values() + [self.sign(data)]))

    def _strftime(self, date_time):
        if type(date_time) == str:
            return date_time
        return date_time.strftime("%Y-%m-%d %H:%M:%S")


class BanditAdjust(BanditInterface):

    def __init__(self, host, public_key, secret_key, timeout=5):
        self.host = host
        self.public_key = public_key
        self.secret_key = secret_key
        self.timeout = timeout
        self.adjust_url = "%s/api/adjust.json" % self.host
        self._session = None

    def adjust(self, hits, query, limit=0, offset=0, show_simul=False, ver=''):
        data = {'query': query,
                'hits': simplejson.dumps(hits),
                'offset': offset,
                'limit': limit,
                'public_key': self.public_key,
                'show_simul': show_simul,
                'ver': ver}

        resp = self.post(self.adjust_url, data=self._signature(data))
        if resp.status_code == requests.codes.ok:
            return resp.json()['content']
        raise BanditApiError(resp.text)


class BanditClick(BanditInterface):

    def __init__(self, host, public_key, secret_key, timeout=5, max_pool_length=100):
        self.host = host
        self.public_key = public_key
        self.secret_key = secret_key
        self.timeout = timeout
        self.max_pool_length = max_pool_length
        self.click_pool = BanditSendPool("%s/api/click.json" % self.host)
        self.show_pool = BanditSendPool("%s/api/show.json" % self.host)
        self._session = None

    def __del__(self):
        self.flush()

    def flush(self):
        if self.click_pool.pool:
            self.send(self.click_pool)
        if self.show_pool.pool:
            self.send(self.show_pool)

    def click(self, query, query_time, target, sk):
        self.add_pool(self.click_pool, {'query': query,
                                        'query_time': self._strftime(query_time),
                                        'target': target,
                                        'session_key': sk})

    def show(self, query, query_time, target, sk):
        self.add_pool(self.show_pool, {'query': query,
                                       'query_time': self._strftime(query_time),
                                       'target': target,
                                       'session_key': sk})

    def send(self, q):
        data = {'content': simplejson.dumps(q.pool),
                'total': len(q.pool),
                'public_key': self.public_key}

        resp = self.post(q.url, data=self._signature(data))
        if resp.status_code != requests.codes.ok:
            raise BanditApiError(resp.text)
        q.clear()

    def add_pool(self, q, data):
        q.pool.append(data)
        if len(q.pool) == self.max_pool_length:
            self.send(q)
