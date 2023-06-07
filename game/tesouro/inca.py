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
# SPDX-License-Identifier: GPL-3.0-or-later
""" Jogo de Exploração do Tesouro Inca - Multiusuário.

.. codeauthor:: Carlo Oliveira <carlo@ufrj.br>

    Classes neste módulo:
        - :py:class:`WebSocket` Módulo de comunicação entre instâncias.
        - :py:class:`Jogador`   Personagem principal do jogo.
        - :py:class:`Inca`      Representa o jogo, montando o tabuleiro.

Changelog
---------
.. versionadded::    21.08
        Classe :py:class:`WebSocket` .
        Classe :py:class:`Jogador` .
        Classe :py:class:`Inca` .

.. versionchanged::    21.08
        FUNC: Vira as cartas.

.. versionchanged::    21.08.a
        FIX: Cartas de aposta funcionando, precisa estado.
        FUNC: Novo protocolo de mensagem <action argument>

"""
__version__ = "21.08.a"
import json

# noinspection PyUnresolvedReferences
from browser import websocket
# noinspection PyUnresolvedReferences
from browser import ajax
from tesouro.main import GUI, SPRITES, Sprite, CRDW


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
        print("send(self)", msg)
        self.ws.send(msg)


class Jogador(Sprite):
    ME = "HE ME".split()
    PL = "NO GO".split()

    def __init__(self, grupo, img="aposta", user="user_00", is_me=False):
        super().__init__(**SPRITES[img])
        self.face = "aposta"
        self.is_me = is_me
        self.user = user
        self.play = False
        self.decidiu = False
        self.grupo = grupo
        self.do_mostra()
        self.vai = self.grupo.play_no

    def turn_bet(self, face="decide", *_):
        index = 1 if self.play else 0
        self.play = False if face == "aposta" else self.play
        self.decidiu = False if face == "aposta" else self.decidiu
        img = SPRITES[face]
        img["index"], img["tit"] = index, ""
        self.reface(**img)
        self.do_mostra()

    # noinspection PyUnusedLocal
    def reface(self, img, index, tit=""):
        w, h = self.siz
        self.img = img
        self.siz = (w, h)
        cw = -int(CRDW) if self.decidiu else -int(w/2)
        print("reface user, w, h, cw, index ", self.user, w, h, cw, index)
        self.pos = (cw*index, 0)

    def do_mostra(self):
        # print("isme, play = self.ME[", self.is_me, " self.PL[", self.play)
        is_me, play = self.ME[self.is_me], self.PL[self.decidiu]
        # print("isme, play = self.ME[", is_me, " self.PL[", play)
        self.mostra(f"{self.user}:{is_me}:{play}")

    def decide(self, sense):
        self.decidiu = True
        self.play = True if sense in "True" else False
        print("def decide -> user, self.play, sense= ", self.user, self.play, sense)
        self.do_mostra()

    def do_play(self, sense):
        # print("self.play = ", sense)
        self.play = sense
        self.grupo.play(sense)
        self.do_mostra()


class Inca:
    def __init__(self):
        self.explorers = {}
        self.action = dict(decide=self.decide, explora=self.explora)
        self.face = "aposta"
        self.users = {}
        self.jogador: Jogador = Jogador(self)
        self.cenario = None
        self.ws = WebSocket(self)
        self.handlers = dict(ROOM_JOIN=self.me_join, USER_JOIN=self.you_join,
                             USER_LEAVE=self.you_leave, MESSAGE=self.message, )

    def decide(self, player, message):
        self.users[player].decide(message)
        face = "decide"
        decidiram = all(user.decidiu for user in self.users.values())
        [user.turn_bet(face) for user in self.users.values()] if decidiram else None

    def explorar(self, *_):
        self.ws.send("explora True")

    def explora(self, player, _):
        self.explorers[player] = True
        face = "aposta"
        [user.turn_bet(face) for user in self.users.values()]

    def play(self, message):
        self.ws.send(f"decide {str(message)}")

    # noinspection PyArgumentList
    def parse_message(self, player, message):
        action, argument = message.split()
        self.action[action](player, argument)

    def message(self, data):
        print("message", data)  # , data["user_id"])
        self.parse_message(data["user_id"], data["msg"])
        # oid = data["user_id"]
        # sense = data["msg"] == "True"
        # self.users[oid].do_play(sense)

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
        self.jogador.do_play(True)

    def play_no(self, *_):
        self.jogador.do_play(False)

    def inicia(self):
        GUI.inicia()
        self.cenario = GUI.fases(0)
        self.cenario.vai()
        self.ws.inicia()
        self.get_users()
        self.cenario.labirinto.vai = self.play_go
        self.cenario.acampamento.vai = self.explorar

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
