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

# noinspection PyUnresolvedReferences
from browser import websocket
# noinspection PyUnresolvedReferences
from browser import ajax
from tesouro.main import GUI, SPRITES, Sprite


# noinspection PyMethodMayBeStatic
class WebSocket:
    def __init__(self, handler, address="ws://127.0.0.1:8000/ws"):
        self.handler = handler
        self.address = address
        self.ws = None

    def inicia(self):
        self.ws = ws = websocket.WebSocket(self.address)
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

    def send(self, msg):
        print("open(self)", msg)
        self.ws.send(msg)


class Jogador(Sprite):
    ME = "YOU ME".split()
    PL = "NO GO".split()

    def __init__(self, grupo, img="aposta", user="user_00", is_me=False):
        super().__init__(**SPRITES[img])
        self.face = "aposta"
        self.is_me = is_me
        self.user = user
        self.play = False
        self.grupo = grupo
        self.do_mostra()
        self.vai = self.grupo.play_no

    def do_mostra(self):
        isme, play = self.ME[self.is_me], self.PL[self.play]
        self.mostra(f"{self.user}:{isme}:{play}")

    def do_play(self, sense, do_fw=False):
        # print("self.play = ", sense)
        self.play = sense
        self.grupo.play(self, sense, do_fw=do_fw)
        self.do_mostra()


class Inca:
    def __init__(self):
        self.players = []
        self.face = "aposta"
        self.users = {}
        self.jogador: Jogador = Jogador(self)
        self.cenario = None
        self.ws = WebSocket(self)
        self.handlers = dict(ROOM_JOIN=self.me_join, USER_JOIN=self.you_join,
                             USER_LEAVE=self.you_leave, MESSAGE=self.message, )

    def play(self, player, message, do_fw=True):
        self.players.append(player)
        self.ws.send(str(message)) if do_fw else None

    def message(self, data):
        print("me_join", data)  # , data["user_id"])
        oid = data["user_id"]
        sense = data["msg"] == "True"
        self.users[oid].do_play(sense)

    def me_join(self, data):
        print("me_join", data)  # , data["user_id"])
        oid = data["user_id"]
        self.append_user(oid, is_me=True)
        self.jogador = self.users[oid]
        # self.users[oid].mostra(f"{oid}:ME") if oid in self.users else None

    def you_join(self, oid):
        print("you_join", oid)  # , data["user_id"])
        self.append_user(oid)
        # self.users[oid].mostra(f"{oid}:YOU") if oid in self.users else None

    def you_leave(self, oid):
        print("you_leave", oid)  # , data["user_id"])
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

    def play_go(self, *_):
        self.jogador.do_play(True, do_fw=True)

    def play_no(self, *_):
        self.jogador.do_play(False, do_fw=True)

    def inicia(self):
        GUI.inicia()
        self.cenario = GUI.fases(0)
        self.cenario.vai()
        self.ws.inicia()
        self.get_users()
        self.cenario.labirinto.vai = self.play_go

    def append_user(self, user, is_me=False):
        if user in self.users:
            return
        # user_card = GUI.carta(self.face)
        user_card = Jogador(self, self.face, user, is_me)
        self.users[user] = user_card
        # user_card.mostra(f"{user}:{is_me}")
        GUI.admite(user_card)

    def remove_user(self, oid):
        if oid in self.users:
            self.users[oid].remove()
            self.users.pop(oid)


def main():
    Inca().inicia()
