import argparse
import sys
import transaction

from pyramid.paster import get_appsettings, setup_logging

from ..models import get_engine, get_session_factory, get_tm_session, Article


def main(argv=sys.argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('config_uri')
    args = parser.parse_args()

    setup_logging(args.config_uri)
    settings = get_appsettings(args.config_uri)

    engine = get_engine(settings)

    session_factory = get_session_factory(engine)

    with transaction.manager:
        session = get_tm_session(session_factory, transaction.manager)

        session.query(Article).update(
            {Article.popularity: Article.popularity * 0.9}
        )
