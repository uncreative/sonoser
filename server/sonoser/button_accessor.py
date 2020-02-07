import sqlite3
from collections import defaultdict
from flask import g, current_app


def get_button_db():
    if 'button_db' not in g:
        g.button_db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.button_db.row_factory = button_factory
    return g.button_db


# noinspection PyUnusedLocal
def close_button_db(e=None):
    button_db = g.pop('button_db', None)

    if button_db is not None:
        button_db.close()


class Button(object):
    action: str
    zone: str
    position: int

    def __init__(self, id=None, zone=None, position=None, action=None, last_modified=None):
        self.id = id
        self.zone = zone
        self.position = position
        self.action = action
        self.last_modified = last_modified

    def to_json(self):
        return self.__dict__


def button_factory(cursor, row):
    button = Button()
    for idx, col in enumerate(cursor.description):
        setattr(button, col[0], row[idx])
    
    return button


class ButtonAccessor(object):
    def __init__(self):
        self.db = get_button_db()

    def update_action(self, button, action):
        if action != button.action:
            self.db.execute(
                "UPDATE button "
                "SET action = ?, last_modified=datetime('now') "
                "WHERE id = ?", (action, button.id))
            self.db.commit()
            return True
        return False

    def new(self, zone, position, action):
        cursor = self.db.cursor()
        cursor.execute("INSERT INTO button (action, zone, position, last_modified) VALUES(?, ?, ?, datetime('now'))",
                       (action, zone, position))
        self.db.commit()
        print("new {} at {}".format(action, position))
        return Button(id=cursor.lastrowid, zone=zone, position=position, action=action)

    def get_all_buttons_by_zone(self):
        buttons = self.db.execute(
            "SELECT id, action, zone, position, last_modified "
            "FROM button "
            "ORDER BY zone, position").fetchall()
        buttons_by_zone = defaultdict(list)
        for button in buttons:
            buttons_by_zone[button.zone].append(button)
        return buttons_by_zone

    def last_modified_button(self):
        last_modified_button = self.db.execute(
            "SELECT  id, action, zone, position, last_modified "
            "FROM button "
            "ORDER BY last_modified DESC LIMIT 1").fetchone()
        return last_modified_button

    def get_buttons_for_zone(self, zone):
        buttons = self.db.execute(
            "SELECT  id, action, zone, position, last_modified "
            "FROM button "
            "WHERE zone=? "
            "ORDER BY position", (zone,)
        ).fetchall()
        return buttons

    def get_button_by_zone_and_position(self, zone, position):
        button = self.db.execute(
            'SELECT id, position, action, zone '
            ' FROM button '
            ' WHERE position = ? AND zone=?',
            (position, zone)
        ).fetchone()
        return button


def init_app(app):
    app.teardown_appcontext(close_button_db)
