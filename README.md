# Deverick
## In this social network you can find truly highly qualified developers!

## [Deverick](http://91.218.195.45:8004)
## [Documentation](app.swaggerhub.com/apis/SeniorVolodymyr/Deverick)
## [API](http://91.218.195.45:8003)

### Server setup
1. `mkdir programs/Deverick`
1. `nano programs/Deverick/docker-compose.yaml`
1. `nano programs/Deverick/.env`
1. `sudo nano //etc/systemd/system/deverick.service`
1. `sudo systemctl daemon-reload`
1. `sudo systemctl enable deverick.service`
1. `sudo systemctl start deverick.service`
1. `sudo systemctl status deverick.service`

### Dev setup
1. Optional PowerShell permitions: `Set-ExecutionPolicy unrestricted`
1. `python -m venv venv`
1. `.\venv\Scripts\activate`
1. `pip install -r .\requirements.txt`
1. Create `.env` from `.env_example`
1. `flask --app run_server.py --debug run --host=0.0.0.0 --port=5005`
1. `pylint --disable=C0116,C0115,C0114,W1514,C0301 ./src`
