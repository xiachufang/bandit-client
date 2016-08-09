# coding: utf-8
import requests
import datetime
import simplejson
import hashlib


def compute_sign(d, secret_key):
    md5_str = ''
    for key, value in sorted(d.items(), key=lambda x: x[0]):
        if isinstance(value, unicode):
            value = value.encode('utf8')
        else:
            value = str(value)
        if isinstance(value, str):
            md5_str += "%s%s" % (key, value)
    md5_str += str(secret_key)
    sign = hashlib.md5(md5_str).hexdigest()
    return sign


class PostError(Exception):

    def __init__(self, arg):
        self.args = [arg]


class BanditClient(object):

    def __init__(self, host, public_key, secret_key, max_queue_length=100, max_seconds=86400):
        self.public_key = public_key
        self.secret_key = secret_key
        self.host = host
        self.max_queue_length = max_queue_length
        self.max_seconds = max_seconds

    def create_instance(self):
        return BanditClientInstance(self)


class BanditSendQueue(object):

    def __init__(self, url):
        self.url = url
        self.clear()

    def clear(self):
        self.queue = []
        self.last_send_time = datetime.datetime.now()


class BanditClientInstance(object):

    def __init__(self, bc):
        self.host_info = bc
        self.click_queue = BanditSendQueue("%s/api/click.json" % self.host_info.host)
        self.show_queue = BanditSendQueue("%s/api/show.json" % self.host_info.host)
        self.adjust_url = "%s/api/adjust.json" % self.host_info.host
        self.max_queue_length = bc.max_queue_length
        self.max_seconds = bc.max_seconds

    def __del__(self):
        if self.click_queue.queue:
            self.push(self.click_queue)
        if self.show_queue.queue:
            self.push(self.show_queue)

    def _signature(self, data):
        return dict(zip(data.keys() + ['signature'],
                        data.values() + [compute_sign(data, self.host_info.secret_key)]))

    def click(self, query, query_time, target, sk):
        if type(query_time) != str:
            query_time = query_time.strftime("%Y-%m-%d %H:%M:%S")
        self.add_queue(self.click_queue, {'query': query,
                                     'query_time': query_time,
                                     'target': target,
                                     'session_key': sk})

    def show(self, query, query_time, target, sk):
        if type(query_time) != str:
            query_time = query_time.strftime("%Y-%m-%d %H:%M:%S")
        self.add_queue(self.show_queue, {'query': query,
                                    'query_time': query_time,
                                    'target': target,
                                    'session_key': sk})

    def push(self, q):
        data = {'content': simplejson.dumps(q.queue),
                'total': len(q.queue),
                'public_key': self.host_info.public_key}
        ret = requests.post(q.url, self._signature(data)).json()
        if ret['status'] != 'ok':
            raise PostError(ret)
        q.clear()

    def add_queue(self, q, data):
        q.queue.append(data)
        if len(q.queue) == self.max_queue_length or (datetime.datetime.now() - q.last_send_time).seconds > self.max_seconds:
            self.push(q)

    def adjust(self, hits, query):
        data = {'hits': simplejson.dumps(hits),
                'query': query,
                'public_key': self.host_info.public_key}
        ret = requests.post(self.adjust_url, self._signature(data)).json()
        if ret['status'] != 'ok':
            raise PostError(ret)
        return ret['content']['hits']
