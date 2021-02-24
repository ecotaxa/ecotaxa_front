from load_collections import EcoTaxaApiClient, create_all
from datasets import *

BASE_URL = "http://localhost:5001"


# production
# BASE_URL = "https://ecotaxa.obs-vlfr.fr"


def main():
    try:
        username, password = open("creds.txt").read().split()[:2]
    except FileNotFoundError:
        print("Need a creds.txt, first line username, second line password.")
        return
    # /!\ Don't hardcode credentials in source code, especially if it goes to GH /!\
    client = EcoTaxaApiClient(url=BASE_URL,
                              email=username,
                              password=password)
    client.open()
    client.whoami()
    collections_to_export = [tara_regent,
                             tara_wp2,
                             tara_multinet,
                             tara_bongo,
                             pnmir_cruises,  # TODO: occurences only
                             point_b_juday_bogorov,
                             point_b_regent,
                             point_b_wp2,
                             dyfamed,
                             moose1,
                             #        mini_point_b_wp2
                             ]
    create_all(client, collections_to_export)


if __name__ == '__main__':
    main()
