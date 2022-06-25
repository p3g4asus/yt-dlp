from datetime import datetime

from .common import InfoExtractor
from ..utils import int_or_none


class MFZHomePlaylistIE(InfoExtractor):
    IE_NAME = 'mfzhome:Playlist'
    _VALID_URL = r'''https?://mfzhome.ddns.net/(?P<host>[^/]+)/(?P<user>[^/]+)/(?P<pl>[^/]+)'''
    _TESTS = []

    def call_api(self, host, user, pl, **kwargs):
        url = f'https://mfzhome.ddns.net/{host}/m3u'
        dlr = self._download_json(url, pl, query=dict(username=user, fmt='json', name=pl), **kwargs)
        return dict() if not dlr else dlr

    def _extract_playlist(self, host, user, pl):
        info = self.call_api(host, user, pl, note='Downloading playlist information', fatal=False)
        if not info:
            return info

        playlist_title = info.get('name')
        playlist_description = ''
        playlist_timestamp = info.get('dateupdate') / 1000
        channel = info.get('type')
        channel_id = info.get('typei')
        id = info.get('rowid')
        items = info.get('items')
        thumbnail = ''
        entries = []
        types = info.get('type')
        if items:
            for e in items:
                datepubi = datetime.strptime(e['datepub'], '%Y-%m-%d %H:%M:%S.%f').timestamp()
                if types == 'youtube':
                    ei = self.url_result(e['link'])
                else:
                    ei = {
                        'id': str(e['rowid']),
                        'display_id': e.get('uid'),
                        'url': e['link'],
                        'title': e['title'],
                        'description': e['title'],
                        'thumbnail': e['img'],
                        'timestamp': datepubi,
                        'duration': int_or_none(e['dur']),
                    }
                    if not thumbnail:
                        thumbnail = ei['thumbnail']
                entries.append(ei)

        return self.playlist_result(
            entries, id, playlist_title, playlist_description,
            timestamp=playlist_timestamp, channel=channel, channel_id=channel_id, thumbnail=thumbnail)

    def _real_extract(self, url):
        host, user, pl = self._match_valid_url(url).group('host', 'user', 'pl')
        return self._extract_playlist(host, user, pl)
