# Discord Time Trial Bot
A discord bot to track time trials for various games that do not support native leaderboards. This bot assumes time entry is manual and will help manage ranks and records for a discord server.

## Tools
- discord.py

## Features
- Configure new games.
- Role based permissions.
- Add/View/Remove times.

## Usage
- 

## Build/Dev
- 

## Notes
---
* Issue with custom openssl package. Need to fix this at the system level. 

(Correct)
python3
> import ssl
> print(ssl.get_default_verify_paths()
DefaultVerifyPaths(cafile='/etc/pki/tls/cert.pem', capath='/etc/pki/tls/certs', openssl_cafile_env='SSL_CERT_FILE', openssl_cafile='/etc/pki/tls/cert.pem', openssl_capath_env='SSL_CERT_DIR', openssl_capath='/etc/pki/tls/certs')

(Observed)
DefaultVerifyPaths(cafile=None, capath='/opt/tools/openssl/openssl-3.2.0/certs', openssl_cafile_env='SSL_CERT_FILE', openssl_cafile='/opt/tools/openssl/openssl-3.2.0/cert.pem', openssl_capath_env='SSL_CERT_DIR', openssl_capath='/opt/tools/openssl/openssl-3.2.0/certs')

Solution:
- Symlinked the system certs directory and ca to the custom openssl install.
```sh
cd /opt/tools/openssl/openssl-3.2.0/
ln -s /etc/pki/tls/cert.pem cert.pem
ln -s /etc/pki/tls/certs certs
```

- Can probably extend the config for a list of games supported. On message can check that channel to see if it has an active game associated with it (May be inefficient). This would fire on every message and not lock the script into searching for one game. Another posibility would be maybe a decorator that searches for a specific channel, but this could get very jank very quickly.
  - Need to consider how the loop will work with multiple games activate. Especially in a scenario where a channel has more than one game. A quick avoidance of very complex logic could be to restrict a channel to having more than one game, but this could suck.
  - Another option is to have a required field for the game when working through commands. Ideally though, the user should just be able to do basic commands and the channel registers the game. 
  - How the game is selected should determine the layout of the config and the datastore. project should be able to dynamic search for this path based on the config. In other words, the game should have a key associated with the config.
  - Perhaps a multi channel flag/toggle that would enforce an additional arg [game name] to the command if a specific game is enabled for multichannel. 
