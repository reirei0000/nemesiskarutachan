#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import pandas as pd
import random
from nemesiskarutachan.board import draw_board


logger = logging.getLogger(__name__)


class IngressKaruta(object):

    def __init__(self):
        self._mondai = None
        self._num = 1
        self._W = 10
        self._H = 5

        self._cards = pd.read_csv('resources/ingresskaruta.csv')
        self._cards.astype(
            dtype={
                'no': int, 'filename': str, 'moji': str,
                'yomi': str, 'text': str})

        self._narabi = [(i + 1) for i in range(self._cards.shape[0])]
        random.shuffle(self._narabi)
        self._nokori = [(i + 1) for i in range(self._cards.shape[0])]

    @property
    def W(self):
        return self._W

    @property
    def H(self):
        return self._H

    @property
    def num(self):
        return self._num

    def next(self):
        if self._mondai is not None:
            self._nokori.remove(self._mondai['no'])
            for i, _ in enumerate(self._narabi):
                if self._narabi[i] == self._mondai['no']:
                    self._narabi[i] = -1
                    break
            self._num += 1

        # random.shuffle(self._narabi)

        sel = random.randint(1, len(self._nokori)) - 1
        mondai_no = self._nokori[sel]
        for n, _ in enumerate(self._narabi):
            if self._narabi[n] == mondai_no:
                break

        ichi = '{}{}'.format(chr(int(n % self._W + 65)), int(n / self._W) + 1)

        name = '「{}」 {}'.format(
            self._cards[self._cards.no == mondai_no]['moji'].values[0],
            self._cards[self._cards.no == mondai_no]['yomi'].values[0])
        # txt = self._cards[self._cards.no == mondai_no]['text'].values[0]
        logger.debug('name={}/{}/{}'.format(ichi, sel, name))

        self._mondai = {
            'num': self._num, 'no': mondai_no, 'name': name, 'location': ichi}
        return self._mondai

    def mondai(self):
        return self._mondai

    def seikai(self):
        fuda = self._cards[
            self._cards.no == self._mondai['no']]['filename'].values[0]
        return 'resources/{}.jpg'.format(fuda)

    def draw(self, output_path):
        draw_board(
            output_path,
            ['{}'.format(
                self._cards[self._cards.no == i]['filename'].values[0]
                ) if i >= 0 else '' for i in self._narabi],
            self.W, self.H, 160, 200)
