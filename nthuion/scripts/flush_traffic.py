import argparse
import sys
import transaction

from pyramid.paster import get_appsettings, setup_logging

from ..traffic import TrafficStore
from ..models import get_engine, get_session_factory, get_tm_session


def main(argv=sys.argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('config_uri')
    args = parser.parse_args()

    setup_logging(args.config_uri)
    settings = get_appsettings(args.config_uri)

    engine = get_engine(settings)

    session_factory = get_session_factory(engine)

    traffic_store = TrafficStore(settings['redis.unixsocket'])

    with transaction.manager:
        session = get_tm_session(session_factory, transaction.manager)

        traffic_store.flush_traffic(session)
