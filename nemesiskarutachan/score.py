#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
import logging


logger = logging.getLogger(__name__)


class Score():

    def init(self):
        self._score = {}
        self._log = []

    def succ(self, num):
        seikai_list = []
        for log in self._log:
            if log[2] == num:
                if log[3]:
                    if len([s for s in seikai_list if s[0] == log[0]]) == 0:
                        seikai_list += [(log[0], log[1], log[4])]
        return seikai_list

    def add(self, uid, name, num, succ):
        self._log += [(uid, name, num, succ, datetime.datetime.now())]
        logger.debug(self._log)

        subtotal = []
        for log in self._log:
            if log[2] == num:
                if log[0] not in subtotal and log[3]:
                    subtotal += [log[0]]

        logger.debug('total subtotal')
        logger.debug(subtotal)
        return len(subtotal)

    def log(self):
        return self._log

    def total(self):
        def exist_user(uid, name):
            for u in users:
                if u['uid'] == uid:
                    return True
            return False

        def add_points(subtotal):
            for u in users:
                for s in subtotal:
                    if u['uid'] == s:
                        u['score'] += 1

        users = []
        for log in self._log:
            uid = log[0]
            name = log[1]
            if exist_user(uid, name) is False:
                users += [{'uid': uid, 'name': name, 'score': 0}]
        logger.debug(users)

        num = 0
        subtotal = []
        for log in self._log:
            uid = log[0]
            succ = log[3]

            if log[2] != num:
                add_points(subtotal)

                subtotal = []
                num = log[2]

            if len(subtotal) < 1 and uid not in subtotal and succ:
                subtotal += [uid]

        add_points(subtotal)

        logger.debug(users)
        return sorted(users, key=lambda x: x['score'], reverse=True)
