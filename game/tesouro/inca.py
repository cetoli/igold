# ! /usr/bin/env python
# -*- coding: UTF8 -*-
# Este arquivo é parte do programa SuperPython
# Copyright 2013-2015 Carlo Oliveira <carlo@nce.ufrj.br>,
# `Labase <http://labase.selfip.org/>`__; `GPL <http://is.gd/3Udt>`__.
#
# SuperPython é um software livre; você pode redistribuí-lo e/ou
# modificá-lo dentro dos termos da Licença Pública Geral GNU como
# publicada pela Fundação do Software Livre (FSF); na versão 2 da
# Licença.
#
# Este programa é distribuído na esperança de que possa ser útil,
# mas SEM NENHUMA GARANTIA; sem uma garantia implícita de ADEQUAÇÃO
# a qualquer MERCADO ou APLICAÇÃO EM PARTICULAR. Veja a
# Licença Pública Geral GNU para maiores detalhes.
#
# Você deve ter recebido uma cópia da Licença Pública Geral GNU
# junto com este programa, se não, veja em <http://www.gnu.org/licenses/>

"""Módulo que realiza comunicação entre browsers via websocket.
.. moduleauthor:: Carlo Oliveira <carlo@nce.ufrj.br>
"""
import json

from browser import websocket
from tesouro.main import GUI
from browser import ajax

# from browser.widgets.dialog import InfoDialog


class WebSocket:
    def __init__(self, handler, address="ws://127.0.0.1:8000/ws"):
        self.handler = handler
        self.address = address
        self.ws = None

    def inicia(self):
        self.ws = ws = websocket.WebSocket(self.address);
        ws.bind('open', self.open)
        ws.bind('message', self.message)
        ws.bind('close', self.close)
        ws.bind('error', self.error)

    def error(self, evt):
        print("error(self)", evt)

    def close(self, evt):
        print("close(self)", evt)

    def message(self, evt):
        print("message(self)", evt.data)
        self.handler.handle(evt.data)

    def open(self, evt):
        print("open(self)", evt)
        pass


class Inca:
    def __init__(self):
        self.face = "aposta"
        self.users = {}
        self.ws = WebSocket(self)
        self.handlers = dict(ROOM_JOIN=self.me_join, USER_JOIN=self.you_join, USER_LEAVE=self.you_leave, )

    def me_join(self, data):
        print("me_join", data)  # , data["user_id"])
        oid = data["user_id"]
        self.append_user(oid, "ME")
        self.users[oid].mostra(f"{oid}:ME") if oid in self.users else None

    def you_join(self, oid):
        print("you_join", oid)  # , data["user_id"])
        # oid = data["user_id"]
        self.append_user(oid, "YOU")
        self.users[oid].mostra(f"{oid}:YOU") if oid in self.users else None

    def you_leave(self, oid):
        print("you_leave", oid)  # , data["user_id"])
        # oid = data["user_id"]
        self.remove_user(oid) if oid in self.users else None

    # noinspection PyArgumentList
    def handle(self, req):
        response = json.loads(req)
        print("handle", response)
        self.handlers[response["type"]](response["data"])

    def add_users(self, req):
        response = json.loads(req.text)
        print("response", response, response['users'])
        for user in response['users']:
            self.append_user(user)  # , is_me)

    def get_users(self, req="http://localhost:8000/users"):
        ajax.get(req, oncomplete=self.add_users)

    def inicia(self):
        GUI.inicia()
        GUI.fases(0).vai()
        self.ws.inicia()
        # user = GUI.carta(self.face)
        # GUI.admite(user)
        self.get_users()

    def append_user(self, user, is_me="?"):
        if user in self.users:
            return
        user_card = GUI.carta(self.face)
        self.users[user] = user_card
        user_card.mostra(f"{user}:{is_me}")
        GUI.admite(user_card)

    def remove_user(self, oid):
        if oid in self.users:
            self.users[oid].remove()
            self.users.pop(oid)


# noinspection PyStatementEffect
def main():
    Inca().inicia()

