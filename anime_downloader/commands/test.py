import logging
import sys
import threading
import os
import click

from anime_downloader.sites import get_anime_class, ALL_ANIME_SITES
from anime_downloader import util
from anime_downloader.__version__ import __version__

logger = logging.getLogger(__name__)

echo = click.echo
sitenames = [v[1] for v in ALL_ANIME_SITES]


class SiteThread(threading.Thread):
    def __init__(self, site, *args, **kwargs):
        self.site = site
        self.exception = None
        super().__init__(*args, **kwargs)

    def run(self):
        try:
            ani = get_anime_class(self.site)

            # this should be more dynamic
            sr = ani.search('naruto')[0]

            anime = ani(sr.url)

            stream_url = anime[0].source().stream_url
        except Exception as e:
            self.exception = e


@click.command()
@click.argument('test_query', default='naruto')
def command(test_query):
    """Test all sites to see which ones are working and which ones aren't. Test naruto as a default."""
    util.print_info(__version__)
    logger = logging.getLogger("anime_downloader")
    logger.setLevel(logging.ERROR)

    threads = []

    for site in sitenames:
        t = SiteThread(site, daemon=True)
        t.start()
        threads.append(t)

    for thread in threads:
        p, f = ('Works: ', "Doesn't work: ") if os.name == 'nt' else ('✅ ', '❌ ')
        thread.join(timeout=10)
        if thread.is_alive():
            logging.debug('timeout during testing')
            echo(click.style(f, fg='red') + thread.site)

        elif thread.exception:
            logging.debug('Error occurred during testing')
            logging.debug(thread.exception)
            echo(click.style(f, fg='red') + thread.site)
        else:
            # echo(click.style('Works ', fg='green') + site)
            echo(click.style(p, fg='green') + thread.site)
