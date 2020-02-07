from flask import (
    Blueprint, flash, render_template, request
)
from werkzeug.exceptions import abort
from sonoser.button_accessor import ButtonAccessor
from sonoser.sonos_accessor import SonosAccessor, SonoserException

bp = Blueprint('button', __name__)

@bp.route('/configuration', methods=('GET', 'POST'))
def configure():
    button_accessor = ButtonAccessor()
    if request.method == 'POST':
        updated = 0
        zone = request.form['zone']
        buttons = button_accessor.get_buttons_for_zone(zone)
        for button in buttons:
            button_id_form_name = "button_id_{}".format(button.id)
            if button_id_form_name in request.form:
                action = request.form[button_id_form_name]
                updated += button_accessor.update_action(button, action)
            else:
                flash("missing action for button id {}".format(button.id))

        new_buttons = []
        for key in request.form.keys():
            if key.startswith("new_"):
                button_index = key[len("new_"):]
                if not button_index.isdigit():
                    flash("button index must be a number {}".format(key))
                else:
                    new_buttons.append((int(button_index), request.form[key]))

        new_buttons.sort()
        for new_button_num, action in new_buttons:
            button_accessor.new(zone, new_button_num, action)
        flash("updated action for {} buttons. created {} new buttons".format(updated, len(new_buttons)))

    buttons_by_zone = button_accessor.get_all_buttons_by_zone()
    #
    sonoser = SonosAccessor()
    playlist_titles = [p.title for p in sonoser.playlists]
    playlist_titles.sort()
    zone_names = [z.player_name for z in sonoser.zones]
    zone_names.sort()

    last_modified_button = button_accessor.last_modified_button()
    last_modified_zone = last_modified_button.zone if last_modified_button else zone_names[0]

    return render_template(
        'button/configure.html',
        buttons_by_zone=buttons_by_zone,
        playlists=playlist_titles,
        zones=zone_names,
        selected_zone=last_modified_zone
    )


@bp.route('/play', methods=['GET'])
def play():
    button_accessor = ButtonAccessor()
    zone = request.args.get('zone', type=str)
    button_position = request.args.get('button_position', type=int)

    button = button_accessor.get_button_by_zone_and_position(zone, button_position)
    if not button:
        abort(404, "button at position {} for zone {} not configured.".format(button_position, zone))
    sonoser = SonosAccessor()
    try:
        sonoser.play_playlist_at_zone(button.action, button.zone)
    except SonoserException as e:
        abort(404, "Could not play '{}' from button at position {} for zone {}. {}".format(
            button.action, button_position, zone, str(e)))
    return render_template('button/play.html', button=button)

