# EcoTaxa python client
A minimal python client example for accessing EcoTaxa, with an example app for creating and exporting collections.

## Preparation

First you have to generate the python models which will use openapi entry points in the application.

```shell script
python generate_models.py
```

A new file 'ecotaxa_model.py' should appear in current directory.
If working with a IDE then add it to source directories.

The API entry points are not used, only the models which are quite handy.

## Usage

You have to provide a file "creds.txt", in current directory, which will be used for authenticating in the API.

First line is your username (generally your email)
Second line is your password.

_Note_: Many of the API entry points are for administrators only.

## Data

The source code expects a `datasets.py` which is not included for privacy reason.

By running `load_collections.py`, a connection to the API will be established, and then the corresponding archives will be produced.

The dwca archives should be ready for import into an IPT.
