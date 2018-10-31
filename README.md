About
-----

[it-dojo](https://it-dojo.io/) frontend, python + flask + mongodb

Usage
-----

    #development
    $ echo 'APP_DOMAIN=it-dojo.io'      > .env
    $ echo 'API_KEY=default'           >> .env
    $ echo 'MAILGUN_DOMAIN=domain.tld' >> .env
    $ echo 'MAILGUN_API=key-api'       >> .env
    $ ./setup.sh [docker-compose-file]

    #production
    $ ./deploy.sh

Access http://localhost:5000

Dependencies
------------

- [docker](https://www.docker.com/)
- [docker-compose](https://docs.docker.com/compose/)
