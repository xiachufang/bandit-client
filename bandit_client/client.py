# coding: utf-8
import requests
import datetime
import simplejson
import hashlib


class BanditApiError(Exception):

    def __init__(self, arg):
        self.args = [arg]


class BanditClient(object):

    def __init__(self, host, public_key, secret_key):
        self.host = host
        self.public_key = public_key
        self.secret_key = secret_key

    def create_instance(self, timeout=5, max_queue_length=100, max_seconds=86400):
        return BanditClientInstance(self, timeout=timeout, max_queue_length=max_queue_length, max_seconds=max_seconds)


class BanditSendQueue(object):

    def __init__(self, url):
        self.url = url
        self.clear()

    def clear(self):
        self.queue = []
        self.last_send_time = datetime.datetime.now()


class BanditClientInstance(object):

    def __init__(self, bc, timeout=5, max_queue_length=100, max_seconds=86400):
        self.host_info = bc
        self.timeout = timeout
        self.max_queue_length = max_queue_length
        self.max_seconds = max_seconds
        self.click_queue = BanditSendQueue("%s/api/click.json" % self.host_info.host)
        self.show_queue = BanditSendQueue("%s/api/show.json" % self.host_info.host)
        self.adjust_url = "%s/api/adjust.json" % self.host_info.host
        self._session = None

    def __del__(self):
        if self.click_queue.queue:
            self.send(self.click_queue)
        if self.show_queue.queue:
            self.send(self.show_queue)

    def sign(self, d, salt=None):
        md5_str = ''
        for key, value in sorted(d.items(), key=lambda x: x[0]):
            if isinstance(value, unicode):
                value = value.encode('utf8')
            else:
                value = str(value)
            if isinstance(value, str):
                md5_str += "%s%s" % (key, value)
        md5_str += str(self.host_info.secret_key)
        sign = hashlib.md5(md5_str).hexdigest()
        return sign

    @property
    def session(self):
        if not self._session:
            self._session = requests.session()
        return self._session

    def post(self, *args, **kwargs):
        return self.session.post(*args, timeout=self.timeout, **kwargs)

    def get(self, *args, **kwargs):
        return self.session.get(*args, timeout=self.timeout, **kwargs)

    def verify(self, d):
        sign = d.pop('signature')
        if sign == self.sign(d):
            return True
        return False

    def _signature(self, data):
        return dict(zip(data.keys() + ['signature'], data.values() + [self.sign(data)]))

    def _strftime(self, date_time):
        if type(datetime) == str:
            return date_time
        return date_time.strftime("%Y-%m-%d %H:%M:%S")

    def click(self, list_id, click_time, target, sk):
        self.add_queue(self.click_queue, {'list_id': list_id,
                                          'query_time': self._strftime(click_time),
                                          'target': target,
                                          'session_key': sk})

    def show(self, list_id, click_time, shows, sk):
        self.add_queue(self.show_queue, {'list_id': list_id,
                                         'query_time': self._strftime(click_time),
                                         'shows': shows,
                                         'session_key': sk})

    def send(self, q):
        data = {'content': simplejson.dumps(q.queue),
                'total': len(q.queue),
                'public_key': self.host_info.public_key}

        resp = self.post(q.url, parms=self._signature(data))
        if resp.status_code == requests.codes.ok:
            return resp.json()['content']
        raise BanditApiError(resp.text)

    def add_queue(self, q, data):
        q.queue.append(data)
        if len(q.queue) == self.max_queue_length or (datetime.datetime.now() - q.last_send_time).seconds > self.max_seconds:
            self.send(q)

    def adjust(self, list_id, scores, limit=20, offset=15, **kwargs):
        data = {'list_id': list_id,
                'scores': simplejson.dumps(scores),
                'offset': offset,
                'limit': limit,
                'public_key': self.host_info.public_key}

        for k, v in kwargs.iteritems():
            data[k] = v

        resp = self.post(self.adjust_url, params=self._signature(data))
        if resp.status_code == requests.codes.ok:
            return resp.json()['content']
        raise BanditApiError(resp.text)
