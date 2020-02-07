let buttonsByZone = window.sonoser.buttonsByZone;
let zones = window.sonoser.zones;
let lastModifiedZone = window.sonoser.lastModifiedZone;
let playlists = window.sonoser.playlists;


function generateNumButtonsSelect() {
  let select = document.createElement("select");
  select.setAttribute("id", "numButtonsSelector");
  select.setAttribute("onchange", "buildButtonTable()");
  for (let i = 2; i < 6; ++i) {
    let option = document.createElement("option");
    option.setAttribute("value", i);
    let txt = document.createTextNode(i*i);
    option.appendChild(txt);
    if (i === 3) {
      option.selected = true;
    }
    select.appendChild(option);
  }
  return select;
}


function generateZoneSelect() {
  let select = document.createElement("select");
  select.setAttribute("id", "zoneSelector");
  select.setAttribute("name", "zone");
  select.setAttribute("onchange", "buildButtonTable()");
  for (let i = 0; i < zones.length; ++i) {
    let zone = zones[i];
    let option = document.createElement("option");
    option.setAttribute("value", zone);
    let txt = document.createTextNode(zone);
    option.appendChild(txt);
    if (zone === lastModifiedZone) {
      option.selected = true;
    }
    select.appendChild(option);
  }
  return select;
}


function generatePlaylistSelect(name, selected) {
  let select = document.createElement("select");
  select.setAttribute("name", name);
  for (let i = 0; i < playlists.length; ++i) {
    let playlist = playlists[i];
    let option = document.createElement("option");
    option.setAttribute("value", playlist);
    let txt = document.createTextNode(playlist);
    option.appendChild(txt);
    if (playlist === selected) {
      console.log("selecting", playlist);
      option.selected = true;
    }
    select.appendChild(option);
  }
  return select;
}

function buildButtonTable() {
  let BUTTONS_PER_ROW = document.getElementById("numButtonsSelector").value;;
  let NUM_BUTTONS = BUTTONS_PER_ROW*BUTTONS_PER_ROW;
  let selectedZone = document.getElementById("zoneSelector").value;

  let buttonTable = document.getElementById("buttons_table");
  buttonTable.innerHTML = "";

  let buttonsData = [];
  if (selectedZone in buttonsByZone) {
    buttonsData = buttonsByZone[selectedZone];
  }
  let row = document.createElement("tr");
  for (let i = 1; i <= NUM_BUTTONS; ++i) {
    let cell = document.createElement("td");
    let playlist_selection = undefined;
    if (i < buttonsData.length) {
      let buttonData = buttonsData[i-1];
      console.log(buttonData);
      playlist_selection = generatePlaylistSelect("button_id_" + buttonData['id'], buttonData['action']);
    }
    else {
      playlist_selection = generatePlaylistSelect("new_" + i, undefined)
    }
    cell.appendChild(playlist_selection);
    row.appendChild(cell);
    if (i % BUTTONS_PER_ROW === 0) {
      buttonTable.appendChild(row);
      row = document.createElement("tr");
    }
  }
  if (row.hasChildNodes()) {
    buttonTable.appendChild(row);
  }
}

document.addEventListener('DOMContentLoaded',
  function () {
  let optionDiv = document.getElementById("options");
  let zoneSelect = generateZoneSelect();
  let numButtonsSelect = generateNumButtonsSelect();
  optionDiv.appendChild(zoneSelect);
  optionDiv.appendChild(numButtonsSelect)
  buildButtonTable()
  }, false
);