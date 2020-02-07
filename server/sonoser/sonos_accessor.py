import soco


class SonoserException(Exception):
    pass


class SonoserPlaylistNotFoundException(SonoserException):
    pass


class SonoserZoneNotFoundException(SonoserException):
    pass


class SonosAccessor:
    def __init__(self):
        self.zones = [zone for zone in soco.discover()]
        self.playlists = [p for p in self.zones[0].get_sonos_playlists()]

    def play_playlist_at_zone(self, playlist_name, zone_name):
        matching_zones = [zone for zone in self.zones if zone.player_name == zone_name]
        if not matching_zones:
            raise SonoserZoneNotFoundException("player name '{}' not found".format(zone_name))
        zone = matching_zones[0]

        playlists = [p for p in self.playlists if p.title == playlist_name]
        if not playlists:
            raise SonoserPlaylistNotFoundException("Playlist '{}' not found".format(playlist_name))
        playlist = playlists[0]

        zone.clear_queue()
        zone.add_uri_to_queue(playlist.get_uri())
        zone.play_from_queue(0)
        # zone.volume = 35
