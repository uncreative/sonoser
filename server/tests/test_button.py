from flask import json

from sonoser.button_accessor import ButtonAccessor
from .conftest import generate_expected_actions, assert_buttons_for_zone, assert_button_properties, \
    zone_9, zone_4, all_zones_names, all_playlist_titles, new_zone, get_soco_queue_fake


def test_configure_get(client, app):
    response = client.get('/configuration')

    set_playlists = "playlists = " + json.dumps(all_playlist_titles)
    assert set_playlists.encode() in response.data
    set_zones = "zones = " + json.dumps(all_zones_names)
    assert set_zones.encode() in response.data

    with app.app_context():
        button_accessor = ButtonAccessor()
        # noinspection PyPep8Naming
        set_buttonsByZone = "buttonsByZone = " + json.dumps(button_accessor.get_all_buttons_by_zone())
        assert set_buttonsByZone.encode() in response.data
        # noinspection PyPep8Naming
        set_lastModifiedZone = "lastModifiedZone = " + json.dumps(button_accessor.last_modified_button().zone)
        assert set_lastModifiedZone.encode() in response.data


def test_configure_post_new_buttons(client, app):
    expected_playlists = generate_expected_actions(new_zone)
    submitted_data = {'zone': new_zone}
    for i, expected_playlist in enumerate(expected_playlists):
        submitted_data["new_{}".format(i+1)] = expected_playlist
    with app.app_context():
        response = client.post(
            '/configuration',
            data=submitted_data
        )
        button_accessor = ButtonAccessor()
        buttons = button_accessor.get_buttons_for_zone(new_zone)
        assert len(buttons) == 9
        assert_buttons_for_zone(buttons,
                                generate_expected_actions(new_zone),
                                new_zone)
        assert b"updated action for 0 buttons" in response.data
        assert b"created 9 new buttons" in response.data


def test_configure_post_update_all_buttons(client, app):
    submitted_data = {'zone': zone_9}
    with app.app_context():
        button_accessor = ButtonAccessor()
        buttons = button_accessor.get_buttons_for_zone(zone_9)
        for button in buttons:
            submitted_data["button_id_{}".format(button.id)] = button.action + "_v2"
        response = client.post(
            '/configuration',
            data=submitted_data
        )

        buttons = button_accessor.get_buttons_for_zone(zone_9)
        assert len(buttons) == 9
        assert_buttons_for_zone(buttons,
                                generate_expected_actions(zone_9 + "_v2"),
                                zone_9)
        assert b"updated action for 9 buttons" in response.data
        assert b"created 0 new buttons" in response.data


def test_configure_post_update_some_buttons(client, app):
    submitted_data = {'zone': zone_9}
    with app.app_context():
        button_accessor = ButtonAccessor()
        orig_buttons = button_accessor.get_buttons_for_zone(zone_9)
        submitted_data["button_id_{}".format(orig_buttons[0].id)] = orig_buttons[0].action + "_v2"
        submitted_data["button_id_{}".format(orig_buttons[1].id)] = orig_buttons[1].action + "_v2"
        submitted_data["button_id_{}".format(orig_buttons[7].id)] = orig_buttons[7].action + "_v2"
        response = client.post(
            '/configuration',
            data=submitted_data
        )

        buttons = button_accessor.get_buttons_for_zone(zone_9)
        assert len(buttons) == 9
        for i, (button, orig_button) in enumerate(zip(buttons, orig_buttons)):
            if i in [0, 1, 7]:
                assert_button_properties(button, orig_button.action + "_v2", orig_button.zone, orig_button.position)
            else:
                assert_button_properties(button, orig_button.action, orig_button.zone, orig_button.position)
        assert b"updated action for 3 buttons" in response.data
        assert b"created 0 new buttons" in response.data


def test_configure_post_updates_and_creates_buttons(client, app):
    submitted_data = {'zone': zone_4}
    expected_playlists = generate_expected_actions("added_" + zone_4)
    with app.app_context():
        button_accessor = ButtonAccessor()
        orig_buttons = button_accessor.get_buttons_for_zone(zone_4)
        submitted_data["button_id_{}".format(orig_buttons[0].id)] = orig_buttons[0].action + "_v2"
        submitted_data["button_id_{}".format(orig_buttons[1].id)] = orig_buttons[1].action + "_v2"
        submitted_data["button_id_{}".format(orig_buttons[3].id)] = orig_buttons[3].action + "_v2"
        modified_ids = [orig_buttons[0].id, orig_buttons[1].id, orig_buttons[3].id]

        for i, expected_playlist in enumerate(expected_playlists[4:]):
            submitted_data["new_{}".format(i)] = expected_playlist

        response = client.post(
            '/configuration',
            data=submitted_data
        )

        buttons = button_accessor.get_buttons_for_zone(zone_4)
        buttons_by_id = {button.id: button for button in buttons}
        assert len(buttons) == 9
        for i, orig_button in enumerate(orig_buttons):
            button = buttons_by_id[orig_button.id]
            if orig_button.id in modified_ids:
                assert_button_properties(button, orig_button.action + "_v2", orig_button.zone, orig_button.position)
            else:
                assert_button_properties(button, orig_button.action, orig_button.zone, orig_button.position)
        assert b"updated action for 3 buttons" in response.data
        assert b"created 5 new buttons" in response.data


def test_play_playlist_in_zone(client, app):
    with app.app_context():
        response = client.get('/play?zone={}&button_position={}'.format(zone_9, 3))
        button_accessor = ButtonAccessor()
        button = button_accessor.get_button_by_zone_and_position(zone_9, 3)
        soco_queue = get_soco_queue_fake()
        assert button.action in soco_queue[0]
        assert len(soco_queue) == 1
        assert b'Playing "three_zone_9" from button at position 3' in response.data


def test_play_non_existent_playlist_in_zone(client, app):
    with app.app_context():
        button_accessor = ButtonAccessor()
        button = button_accessor.get_button_by_zone_and_position(zone_9, 3)

        button_accessor.db.execute(
            "UPDATE button "
            "SET action = ?, last_modified=datetime('now') "
            "WHERE id = ?", ("does_not_exist", button.id))
        button_accessor.db.commit()

        response = client.get('/play?zone={}&button_position={}'.format(zone_9, 3))

        assert len(get_soco_queue_fake()) == 0
        assert b"Playlist 'does_not_exist' not found" in response.data
        assert b"Could not play 'does_not_exist' from button at position 3 for zone zone_9" in response.data


def test_play_playlist_in_non_existent_zone(client, app):
    with app.app_context():
        button_accessor = ButtonAccessor()
        button = button_accessor.get_button_by_zone_and_position(zone_9, 3)

        button_accessor.db.execute(
            "UPDATE button "
            "SET zone = ?, last_modified=datetime('now') "
            "WHERE id = ?", ("does_not_exist", button.id))
        button_accessor.db.commit()

        response = client.get('/play?zone={}&button_position={}'.format("does_not_exist", 3))

        assert len(get_soco_queue_fake()) == 0
        assert b"player name 'does_not_exist' not found" in response.data
        assert b"Could not play 'three_zone_9' from button at position 3 for zone does_not_exist" in response.data


def test_play_playlist_in_non_existent_button_position(client):
    response = client.get('/play?zone={}&button_position={}'.format(zone_4, 7))
    assert len(get_soco_queue_fake()) == 0
    assert b"button at position 7 for zone zone_4 not configured." in response.data
