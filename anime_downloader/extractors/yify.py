import re
from anime_downloader.extractors.base_extractor import BaseExtractor
from anime_downloader.sites import helpers
import logging

logger = logging.getLogger(__name__)


class Yify(BaseExtractor):
    def _get_data(self):
        api_id = re.search(r'id=([^&]*)', self.url).group(1)
        api = f'https://api.streammp4.net/api/backup.php?id={api_id}'
        data = helpers.get(api).json()
        logger.debug('Data: {}'.format(data))

        return next(
            (
                {'stream_url': i['file']}
                for i in data
                if self.quality in i.get('label', '')
            ),
            {'stream_url': ''},
        )
