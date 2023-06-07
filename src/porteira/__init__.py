#! /usr/bin/env python
# -*- coding: UTF8 -*-
# This file is part of  program Porteira
# Copyright © 2023  Carlo Oliveira <carlo@nce.ufrj.br>,
# `Labase <http://labase.selfip.org/>`__; `GPL <http://is.gd/3Udt>`__.
# SPDX-License-Identifier: (GPLv3-or-later AND LGPL-2.0-only) WITH bison-exception

"""Version and configurations.

    This module serves version information for the site.

"""
from collections import namedtuple
from dataclasses import dataclass
# import pathlib

__version__ = "23.06"


ServerKind = namedtuple("ServerKind", "porteira1 porteira2")(0, 1)


@dataclass
class GameMainCfg:
    passwd = None
    data_base = "alite_game",
    collection = "score",
    db_url = "alitelabase.b1lm6fr.mongodb.net"
    username = "carlotolla9"
    con_string = f"mongodb+srv://{username}:{passwd}@{db_url}/?retryWrites=true&w=majority"
    version = __version__
