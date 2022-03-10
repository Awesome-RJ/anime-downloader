import logging
import json
import re
from anime_downloader.sites.anime import Anime, AnimeEpisode, SearchResult
from anime_downloader.sites import helpers
from anime_downloader.extractors import get_extractor

logger = logging.getLogger(__name__)


class AnimeBinge(Anime, sitename='animebinge'):
    sitename = 'animebinge'

    @classmethod
    def search(cls, query):
        response = helpers.get('https://animebinge.net/search', params={'term': query})
        soup = helpers.soupify(response)
        results = soup.select('a#epilink')

        return [
            SearchResult(
                title=x.text,
                url=x['href']
            )
            for x in results
        ]

    def _scrape_episodes(self):
        eps = helpers.soupify(helpers.get(self.url)).select('div.episode-wrap > a')
        eps = [x['href'] for x in eps]
        eps.reverse()
        return eps

    def _scrape_metadata(self):
        self.title = helpers.soupify(helpers.get(self.url)).select_one('div.contingo > p').text


class AnimeBingeEpisode(AnimeEpisode, sitename='animebinge'):
    def _get_sources(self):
        html = helpers.get(self.url).text
        # Matches:
        # var episode = {"id":"187961",
        #                "url":"https:\/\/animebinge.net\/episode\/187961-yakusoku-no-neverland-episode-1",
        #                "lang":"dubbed"}; </script>
        # And parses the json in the script.
        episode_regex = r'var\s*episode\s*=\s*({[\W\w]*?);\s*<\/script>'

        if source := re.search(episode_regex, str(html)):
            source_json = json.loads(source.group(1))['videos']
        else:
            return ''

        logger.debug('Sources: {}'.format(source_json))

        mappings = {
            'mp4upload': 'https://www.mp4upload.com/embed-{}.html',
            'trollvid': 'https://trollvid.net/embed/{}',
            'xstreamcdn': 'https://xstreamcdn.com/v/{}'
        }

        sources_list = []
        for i in source_json:
            if mappings.get(i.get('host')):
                extractor = i['host'] if get_extractor(i['host']) else 'no_extractor'
                sources_list.append({
                    'extractor': extractor,
                    'url': mappings[i['host']].format(i['id']),
                    'server': i['host'],
                    'version': i.get('type', 'subbed')
                })

        return self.sort_sources(sources_list)
