# Sonoser

Play some sonos playlists by clicking on buttons (arduino)

## Getting Started

Flask server on OS X
install latest sqlite and pyenv using homebrew

```brew upgrade sqlite pyenv```

create a python 3.8 environment with latest sqlite
```
export PATH="/usr/local/opt/sqlite/bin:$PATH"
export LDFLAGS="-L/usr/local/opt/sqlite/lib"
export CPPFLAGS="-I/usr/local/opt/sqlite/include"
export PKG_CONFIG_PATH="/usr/local/opt/sqlite/lib/pkgconfig"
pyenv install 3.8.1
pyenv local 3.8.1 
rm ~/.pyenv/versions/.DS_Store
eval "$(pyenv init -)"
pip install pipenv

cd server
pipenv install
pipenv shell
export FLASK_APP=sonoser
export FLASK_ENV=development
flask init-db
flask run
```
go to

http://127.0.0.1:5000/configuration

then

http://127.0.0.1:5000/play?zone=Play%205&button_position=2

## Running the tests

```
cd server
pytest tests/
```

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

