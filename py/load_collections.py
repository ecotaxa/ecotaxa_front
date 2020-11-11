# -*- coding: utf-8 -*-
# This file is part of Ecotaxa, see license.md in the application root directory for license informations.
# Copyright (C) 2015-2020  Picheral, Colin, Irisson (UPMC-CNRS)
#
# LOV collections creation via API.
#
import io
import zipfile
from typing import Union, IO

from urllib3.exceptions import HTTPWarning

from datasets import CollectionDescription, tara_bongo, moose1, tara_multinet
from ecotaxa_model import *
from simple_client import SimpleClient
import logging

BASE_URL = "http://localhost:5001"

# production
BASE_URL = "https://ecotaxa.obs-vlfr.fr"

logging.basicConfig(level=logging.INFO)


class EcoTaxaApiClient(SimpleClient):
    """
        An API client wrapper class for Ecotaxa.
    """

    def __init__(self, url: str, email: str, password: str):
        super().__init__(url)
        self.email = email
        self.password = password

    def open(self):
        """
            Open a connection to the API by loging in.
        """
        token = self.login()
        assert token is not None, "Auth failed!"
        self.token = token

    def login(self):
        req = LoginReq(username=self.email,
                       password=self.password)
        try:
            rsp = self.post(str, "/login", json=req)
        except HTTPWarning:
            return None
        return rsp

    def whoami(self):
        """
            Example API call for fetching own name.
        """
        rsp: UserModel = self.get(UserModel, "/users/me")
        logging.info("You are %s", rsp)

    def search_user(self, user_name: str) -> List[UserModel]:
        rsp = self.get(List[UserModel], "/users/search?by_name=%s" % user_name)
        return rsp

    def search_collection(self, title: str):
        rsp: List[CollectionModel] = self.get(List[CollectionModel], "/collections/search?title=%s" % title)
        return rsp

    def create_collection(self, title: str, project_ids: List[int]):
        req = CreateCollectionReq(title=title,
                                  project_ids=project_ids)
        rsp = self.post(int, "/collections/create", json=req)
        return rsp

    def query_collection(self, coll_id: int) -> CollectionModel:
        rsp: CollectionModel = self.get(CollectionModel, "/collections/%d" % coll_id)
        return rsp

    def update_collection(self, collection: CollectionModel):
        rsp = self.put("/collections/%d" % collection.id, json=collection)
        return rsp

    def delete_collection(self, coll_id: int):
        rsp = self.delete("/collections/%d" % coll_id)
        return rsp

    def export_collection(self, coll_id: int, dry_run: bool) -> EMODnetExportRsp:
        rsp = self.get(EMODnetExportRsp, "/collections/%d/export/emodnet?dry_run=%s" % (coll_id, dry_run))
        return rsp

    def get_task_file(self, task_id: int):
        rsp = self.get(IO, "/tasks/%d/file" % task_id, stream=False)
        return rsp


def user_lookup(client: EcoTaxaApiClient, user_name: str) -> Optional[UserModel]:
    # Look for a user from its name
    srch = client.search_user(user_name)
    if len(srch) == 0:
        logging.error("Cannot find user '%s' in system", user_name)
    elif len(srch) > 1:
        logging.error("Several matches for user '%s' in system", user_name)
    else:
        ret = srch[0]
        # TODO: For some reason, the date does not serialize.
        ret.usercreationdate = None
        return ret


OK_LICENSES = {'CC0 1.0', 'CC BY 4.0', 'CC BY-NC 4.0'}


def de_chunk_if_needed(blob: bytes):
    """
0000000  34  30  30  0d  0a  50  4b  03  04  14  00  00  00  08  00  f4
          4   0   0  \r  \n   P   K 003 004 024  \0  \0  \0  \b  \0 364
0000020  66  6a  51  38  6d  b7  a5  14  0b  00  00  ce  50  00  00  07
          f   j   Q   8   m 267 245 024  \v  \0  \0 316   P  \0  \0  \a
    """
    if blob[0:2] == b"PK":
        return blob
    fd = io.BytesIO(blob)
    ret = b""
    while True:
        ln = fd.readline()
        ln = ln.strip()
        ln = int(ln, 16)
        if ln == 0:
            break
        ret += fd.read(ln)
        _dumm = fd.read(2)  # Chunks end with \r\n
    return ret


def create_collection(client: EcoTaxaApiClient, coll_in: CollectionDescription):
    # If exists with same title then delete it
    existing = client.search_collection(title=coll_in.title)
    if len(existing) > 0:
        client.delete_collection(existing[0].id)
    # Create the base version from 0
    coll_id = client.create_collection(coll_in.title, coll_in.projects)
    logging.info("New collection id:%d from %s", coll_id, coll_in.projects)
    # Get the collection, a few fields should be aggregated from projects e.g. license
    coll = client.query_collection(coll_id)
    if coll.license not in OK_LICENSES:
        logging.error("Collection license '%s' does not make it exportable", coll.license)
    # Update from the description
    # Lookup & set provider
    coll.provider_user = user_lookup(client, coll_in.provider)
    # Lookup & set contact
    coll.contact_user = user_lookup(client, coll_in.contact)
    # Lookup & set associates
    associates = lookup_users(client, "associates", coll.associate_users, coll_in.associates)
    creators = lookup_users(client, "creators", coll.creator_users, coll_in.creators)
    coll.associate_users = [an_assoc for an_assoc in associates if not isinstance(an_assoc, str)]
    coll.associate_organisations = [an_assoc for an_assoc in associates if isinstance(an_assoc, str)]
    coll.creator_users = [a_user for a_user in creators if not isinstance(a_user, str)]
    coll.creator_organisations = [a_user for a_user in creators if isinstance(a_user, str)]
    # Atomic fields
    coll.title = coll_in.title
    coll.citation = coll_in.citation
    coll.abstract = coll_in.abstract
    coll.description = coll_in.description
    client.update_collection(coll)
    # TODO: License
    # Check after update
    coll_reread = client.query_collection(coll_id)
    logging.info("After update: %s", coll_reread)
    export_out = client.export_collection(coll_id, True)
    for a_msg in export_out.warnings:
        logging.warning("(BACK):%s", a_msg)
    for a_msg in export_out.errors:
        logging.error("(BACK):%s", a_msg)
    if export_out.task_id == 0:
        logging.error("Export failed:" + "\n".join(export_out.errors))
    else:
        zipped_blob = client.get_task_file(export_out.task_id)
        # For some reason, thru the proxy we get an http 1.1 chunked content
        zipped_blob = de_chunk_if_needed(zipped_blob)
        dasid = coll_in.ref.split("=")[-1]
        coll_on_disk = "coll_%s_export" % dasid
        zip_file = coll_on_disk + ".zip"
        with open(zip_file, "wb") as fd:
            fd.write(zipped_blob)
        with zipfile.ZipFile(zip_file, 'r') as z:
            z.extractall(coll_on_disk)


def lookup_users(client: EcoTaxaApiClient, list_label: str, present: List[UserModel], names_list: str) \
        -> List[Union[UserModel, str]]:
    """
        Lookup given list of names, cross with present list and return a fresher list.
    """
    ret = []
    present_ids = set([a_present_user.id for a_present_user in present])
    for a_line in names_list.splitlines():
        words = a_line.split()
        nb_words = len(words)
        if nb_words > 4 or "Consortium" in words:
            # Most probably an institution
            if len(ret) > 0 and isinstance(ret[-1], UserModel):
                # The institution is following a name, assume we'll know from EcoTaxa DB
                pass
            else:
                ret.append(a_line)
        else:
            user = user_lookup(client, a_line)
            if user is None:
                continue
            if user.id not in present_ids:
                logging.info("Adding %s into %s list", user.name, list_label)
                ret.append(user)
    return ret


def create_all(client: EcoTaxaApiClient, collections: List[CollectionDescription]):
    for a_coll in collections:
        create_collection(client, a_coll)


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
    create_all(client,
               [  # moose1,  "Net type 'triple_net' in sample triple_35_200_20170907 is not mapped to BODC vocabulary"
                   tara_bongo,
                   tara_multinet])


if __name__ == '__main__':
    main()
