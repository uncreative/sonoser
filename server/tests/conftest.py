import os
import tempfile

import soco
from mock import Mock
import pytest
from sonoser import create_app
from sonoser.db import get_db, init_db

#########
#  TODO: move to tests constants file...


def generate_expected_actions(suffix):
    expected_actions = ['one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine']
    return [expected_action + '_' + suffix for expected_action in expected_actions]


def assert_buttons_for_zone(buttons, expected_actions, expected_zone):
    for i, button in enumerate(buttons):
        assert_button_properties(button, expected_actions[i], expected_zone, i + 1)


def assert_button_properties(button, expected_action, expected_zone, expected_position):
    assert button.zone == expected_zone
    assert button.position == expected_position
    assert button.action == expected_action


new_zone = 'test_zone'
zone_4 = 'zone_4'
zone_9 = 'zone_9'
all_zones_names = [new_zone, zone_4, zone_9]

all_playlist_titles = []
for zone_name in all_zones_names:
    all_playlist_titles = all_playlist_titles + generate_expected_actions(zone_name)
all_playlist_titles.sort()
#########
#
#
# def pytest_configure(config):
#     terminal = config.pluginmanager.getplugin('pytest-teamcity')
#     BaseReporter = terminal.TerminalReporter
#
#     class QuietReporter(BaseReporter):
#         def __init__(self, *args, **kwargs):
#             BaseReporter.__init__(self, *args, **kwargs)
#             self.verbosity = 0
#             self.showlongtestinfo = self.showfspath = False
#
#     terminal.TerminalReporter = QuietReporter


with open(os.path.join(os.path.dirname(__file__), 'data.sql'), 'rb') as f:
    _data_sql = f.read().decode('utf8')


@pytest.fixture
def app():
    db_fd, db_path = tempfile.mkstemp()

    app = create_app({
        'TESTING': True,
        'DATABASE': db_path,
    })

    with app.app_context():
        init_db()
        get_db().executescript(_data_sql)

    yield app

    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()


_soco_queue_fake = []

# noinspection PyMethodMayBeStatic,PyUnusedLocal
class FakePlaylist(object):
    def __init__(self, title):
        self.title = title

    def get_uri(self, resource_nr=0):
        return "file:///jffs/settings/savedqueues.rsq#" + self.title


# noinspection PyMethodMayBeStatic,PyUnusedLocal
class FakeZone(object):
    def __init__(self, player_name, playing=False):
        self.player_name = player_name
        self.playing = playing

    def stop(self):
        self.playing = False

    def clear_queue(self):
        global _soco_queue_fake
        _soco_queue_fake = []
        self.playing = False

    def play_from_queue(self, index, start=True):
        self.playing = start

    def get_sonos_playlists(self):
        return [FakePlaylist(title) for title in all_playlist_titles]

    def add_uri_to_queue(self, uri, position=0, as_next=False):
        _soco_queue_fake.append(uri)
        return len(_soco_queue_fake) - 1


@pytest.fixture(autouse=True)
def fake_soco(monkeypatch):
    global _soco_queue_fake
    _soco_queue_fake = []
    soco_discover = Mock(return_value={FakeZone(z) for z in all_zones_names})
    monkeypatch.setattr(soco, 'discover', soco_discover)



def get_soco_queue_fake():
    return _soco_queue_fake[:]