import redis
import transaction

from nthuion.models import Article


UNIQUE_VIEWS = 1


class TrafficStore(redis.StrictRedis):

    def __init__(self, unix_socket_path):
        super().__init__(unix_socket_path=unix_socket_path, db=UNIQUE_VIEWS)

    def article_viewed_by_user(self, article, user):
        self.sadd(article.id, 'user:{}'.format(user.id))

    def article_viewed_by_ip(self, article, ip):
        self.sadd(article.id, 'ip:{}'.format(ip))

    def flush_traffic(self, session):
        for key in self.scan_iter():
            with transaction.manager:
                with self.pipeline() as p:
                    p.scard(key)
                    p.delete(key)
                    count, deleted = p.execute()
                query = session.query(Article).filter(Article.id == int(key))
                query.update({
                    Article.views: Article.views + count,
                    Article.popularity: Article.popularity + count,
                })


def includeme(config):
    settings = config.get_settings()

    unixsocket = settings['redis.unixsocket']

    traffic_store = TrafficStore(unixsocket)

    config.add_request_method(
        lambda r: traffic_store,
        'ts',
        reify=True
    )
