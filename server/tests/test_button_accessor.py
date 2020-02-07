import sqlite3

import pytest

from sonoser.button_accessor import get_button_db, ButtonAccessor
from .conftest import zone_4, zone_9, generate_expected_actions, assert_buttons_for_zone, assert_button_properties, \
    new_zone


def test_get_close_db(app):
    with app.app_context():
        db = get_button_db()
        assert db is get_button_db()

    with pytest.raises(sqlite3.ProgrammingError) as e:
        db.execute('SELECT 1')

    assert 'closed' in str(e.value)


def test_update_action_updates_when_action_different(app):
    with app.app_context():
        button_accessor = ButtonAccessor()

        button = button_accessor.get_button_by_zone_and_position(zone_4, 3)
        original_action = 'three_zone_4'
        assert_button_properties(button, original_action, zone_4, 3)

        new_action = 'something_new'
        is_updated = button_accessor.update_action(button, new_action)
        assert is_updated
        button = button_accessor.get_button_by_zone_and_position(zone_4, 3)
        assert_button_properties(button, new_action, zone_4, 3)


def test_update_action_does_not_update_when_action_same(app):
    with app.app_context():
        button_accessor = ButtonAccessor()

        button = button_accessor.get_button_by_zone_and_position(zone_4, 3)
        original_action = 'three_zone_4'
        assert_button_properties(button, original_action, zone_4, 3)

        is_updated = button_accessor.update_action(button, original_action)
        assert not is_updated
        button = button_accessor.get_button_by_zone_and_position(zone_4, 3)
        assert_button_properties(button, original_action, zone_4, 3)


def test_new(app):
    with app.app_context():
        button_accessor = ButtonAccessor()
        new_action = 'something_new'
        new_position = 1
        button = button_accessor.new(new_zone, new_position, new_action)
        assert_button_properties(button, new_action, new_zone, new_position)

        button = button_accessor.get_button_by_zone_and_position(new_zone, new_position)
        assert_button_properties(button, new_action, new_zone, new_position)


def test_get_all_buttons_by_zone(app):
    with app.app_context():
        button_accessor = ButtonAccessor()
        buttons = button_accessor.get_all_buttons_by_zone()
        assert len(buttons[zone_4]) == 4
        assert len(buttons[zone_9]) == 9
        assert set(buttons.keys()) == {zone_4, zone_9}

        assert_buttons_for_zone(buttons[zone_4],
                                generate_expected_actions(zone_4),
                                zone_4)
        assert_buttons_for_zone(buttons[zone_9],
                                generate_expected_actions(zone_9),
                                zone_9)


def test_last_modified_button(app):
    with app.app_context():
        button_accessor = ButtonAccessor()
        button = button_accessor.last_modified_button()
        assert_button_properties(button, 'four_zone_4', zone_4, 4)


def test_get_buttons_for_zone(app):
    with app.app_context():
        button_accessor = ButtonAccessor()
        buttons = button_accessor.get_buttons_for_zone(zone_4)
        assert len(buttons) == 4
        assert_buttons_for_zone(buttons,
                                generate_expected_actions(zone_4),
                                zone_4)


def test_get_button_by_zone_and_position(app):
    with app.app_context():
        button_accessor = ButtonAccessor()
        button = button_accessor.get_button_by_zone_and_position(zone_4, 2)
        assert_button_properties(button, 'two_zone_4', zone_4, 2)

        button_accessor = ButtonAccessor()
        button = button_accessor.get_button_by_zone_and_position(zone_9, 6)
        assert_button_properties(button, 'six_zone_9', zone_9, 6)
