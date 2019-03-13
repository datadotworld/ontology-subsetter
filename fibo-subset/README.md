### data.world FIBO Subset Generation Utility / Webhook Callback

This code was initially developed in March 2019 as part of an effort at Intuit to create ontologies on data.world
by subsetting [FIBO](https://spec.edmcouncil.org/fibo/).  It leverages a Python module maintained by the EDM
Council that takes a list of desired RDF subjects (called a "seeds" file) and a base ontology, and produces
a subset of the ontology containing only those tuples having the seeds as subjects.

This code extends the EDM Council module by allowing the base ontology, seeds file, and subset destination to be
on the data.world platform.

Obtain the EDM Council module here (todo: change this to the base repo, not our fork, once Dean accepts the PR):

https://github.com/datadotworld/ontology-publisher/blob/master/publisher/lib/subset.py

For instance, like:
```
curl -O https://raw.githubusercontent.com/datadotworld/ontology-publisher/master/publisher/lib/subset.py
```

#### Running from the command line

The `ddw_fibo_subset.py` script can be run directly.  Running it with the `-h` option displays the help.  It relies on
a shell environment variable `DW_AUTH_TOKEN` being defined with a value of a data.world API key with appropriate permissions
to the datasets involved.  The help content explains how to reference the inputs and outputs:

```
$ python3 ddw_fibo_subset.py -h
usage: ddw_fibo_subset.py [-h] [-v] [-f FORMAT]
                          ontology_dataset destination_dataset
                          destination_file seeds_dataset seeds_file base

positional arguments:
  ontology_dataset      owner/dataset where ontology files are stored
  destination_dataset   owner/dataset where output subset should be stored
  destination_file      name of file within destination dataset where output
                        subset should be stored
  seeds_dataset         owner/dataset where seeds file is stored
  seeds_file            name of file within seeds dataset where seeds are
                        listed
  base                  Base URI of subset

optional arguments:
  -h, --help            show this help message and exit
  -v, --verbose         Print dianostic/progress info
  -f FORMAT, --format FORMAT
                        Subset format (default is ttl/turtle)
$
```

Note that the three dataset arguments are specified in the standard data.world format `ownerid/dataset`.

#### Running as a webhook

The `webhook_app.py` script runs a [Flask](http://flask.pocoo.org/) application that exposes a callback for
a data.world [webhook](https://apidocs.data.world/toolkit/webhooks).  It can be run from a Python environment with the proper python
dependencies installed and shell environment variables set (see the `pip` install in the Dockerfile for the details on dependencies,
  and the `config.env.template` file for the list of necessary environment variables):

`python3 webhook_app.py`

This will start the http server on port 5000.  For it to be usable by the data.world webhook, it will need to be reachable on the public
Internet (using [ngrok](https://ngrok.com/) or a similar mechanism, or deploying on EC2 or Heroku).

Configure the data.world webhook to `POST` to the endpoint `/refresh-subset`.  It will respond to each `POST` by comparing the seeds file to the
subset file, and refresh the latter if it is older than the former.

The flask app can also be run in Docker with the included docker-compose file.  Save a copy of the `config.env.template` file to `config.env`
and specify the desired values for the environment variables.  Then start the container with `docker-compose up -d`.  Make sure the shell from
which you run `docker-compose` has the `DW_AUTH_TOKEN` environment variable exported.
