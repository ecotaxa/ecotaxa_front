# -*- coding: utf-8 -*-
# This file is part of Ecotaxa, see license.md in the application root directory for license informations.
# Copyright (C) 2015-2026  Picheral, Colin, Irisson (UPMC-CNRS)
#
# Development server launcher


import logging

from appli import app
from logging_conf import setup_logging

if __name__ == "__main__":
    setup_logging(app)
    werkzeug_logger = logging.getLogger('werkzeug')
    werkzeug_logger.setLevel(logging.CRITICAL)  # Basically turn off Werkzeug logging
    app.logger.info("EcoTaxa (dev) Startup")
    import ssl

    # context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
    context.load_cert_chain("localhost+3.pem", "localhost+3-key.pem")
    context.verify_mode = ssl.CERT_OPTIONAL
    context.load_verify_locations("localhost+3.pem")
    app.run(
        host="0.0.0.0",
        port=5001,
        threaded=True,
        debug=True,
        ssl_context=context,
    )
