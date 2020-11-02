#!/usr/bin/env python
# -*- coding: utf-8 -*-

import fire
import logging
import random
import sys
from mwt import mwt
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from nemesiskarutachan.ingresskaruta import IngressKaruta
from nemesiskarutachan.score import Score
from nemesiskarutachan.singleton import Singleton


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)

logger = logging.getLogger(__name__)


class GameMaster(Singleton):
    def init(self):
        self._game = {}

    def start(self, id, kind, level, mondaisuu):
        g = IngressKaruta()
        s = Score()
        s.init()
        self._game[id] = (g, s, mondaisuu)

    def get(self, id):
        if id not in self._game:
            raise Exception

        return self._game[id]


@mwt(timeout=10*60)
def get_admin_ids(bot, chat_id):
    return [admin.user.id for admin in bot.get_chat_administrators(chat_id)]


def start_IngressKaruta(update, context):
    user_id = update.message.from_user.id
    chat_id = update.effective_chat.id
    message_id = update.message.message_id
    chat_type = update.effective_chat.type

    if chat_type == "group" or chat_type == "supergroup":
        if user_id not in get_admin_ids(context.bot, chat_id):
            return

    context.bot.delete_message(chat_id, message_id)
    _start(update, context, chat_id, 'IngressKaruta')


def _start(update, context, chat_id, kind):
    args = context.args
    if len(args) > 2:
        mondaisuu = int(args[0])
        if mondaisuu < 1 or 47 < mondaisuu:
            mondaisuu = 5
        interval = int(args[1])
        if interval < 15 or 120 < interval:
            interval = 15
        level = int(args[2])
        if level < 1 or 8 < level:
            level = 4
    elif kind == 'IngressKaruta':
        mondaisuu = 47
        interval = 20
        level = 4
    else:
        mondaisuu = 47
        interval = 20
        level = 4

    context.bot.send_message(
        chat_id=chat_id,
        text='''\
ゲームを開始しますー
{}問勝負です。
英字数字の２文字でお答えください。
(例: A1)

※ 非公式Ingressかるたとは
https://sites.google.com/view/ingresskaruta2020/'''.format(mondaisuu))
    GameMaster().start(chat_id, kind, level, mondaisuu)

    _nextMondai(chat_id, context, None)


def answer(update, context):
    chat_id = update.effective_chat.id
    g, s, max_mondai = GameMaster().get(chat_id)

    mondai = g.mondai()
    if mondai is not None:
        seikai = s.succ(mondai['num'])
        if len(seikai) == 0:
            context.bot.send_message(
                chat_id=chat_id,
                text='正解者はまだいません')
            return
        else:
            for i, seikaisya in enumerate(seikai):
                if i == 0:
                    msg = '{}位 {} さん！おめでとうございます！'.format(
                        i + 1, seikaisya[1])
                    f = seikaisya[2]
                else:
                    delta = (seikaisya[2] - f).total_seconds()
                    msg += '\n{}位 {} さん +{:.3f}秒'.format(
                        i+1, seikaisya[1], delta)

                if i > 4:
                    break
            context.bot.send_message(chat_id=chat_id, text=msg)
        context.bot.send_photo(
            chat_id=chat_id,
            caption='{}\n正解は [{}]でした'.format(
                mondai['name'], mondai['location']),
            photo=open(g.seikai(), 'rb'))


def nextMondai(update, context):
    chat_id = update.effective_chat.id

    _nextMondai(chat_id, context, None)


def _nextMondai(chat_id, context, job):
    g, _, max_mondai = GameMaster().get(chat_id)

    mondai = g.next()

    num = mondai['num']
    if num > max_mondai and job is not None:
        job.schedule_removal()
        context.bot.send_message(chat_id=chat_id, text='全問終了です！\nお疲れ様でした〜')
        _score(chat_id, context)
        return

    if num == max_mondai:
        msg = '最後の問題です！'
    else:
        msg = '{} 問目！'.format(num)
    context.bot.send_message(chat_id=chat_id, text=msg)

    board_path = 'output.jpg'
    g.draw(board_path)

    caption = mondai['name']
    context.bot.send_photo(
        chat_id=chat_id,
        caption=caption,
        photo=open(board_path, 'rb'))


def take(update, context):
    chat_id = update.effective_chat.id
    user_id = update.message.from_user.id
    name = update.message.from_user.first_name
    text = update.message.text

    g, s, _ = GameMaster().get(chat_id)

    mondai = g.mondai()

    if ' ' in text:
        fuda = text.split()[1]
    else:
        fuda = text

    if fuda.upper() == mondai['location'].upper():
        succ = True
    else:
        succ = False

    s.add(user_id, name, mondai['num'], succ)


def score(update, context):
    chat_id = update.effective_chat.id
    _score(chat_id, context)


def _score(chat_id, context):
    _, s, _ = GameMaster().get(chat_id)

    msg = 'スコア\n'
    rank = 0
    score = -1
    for u in s.total():
        if score != u['score']:
            rank += 1
        msg += '{}位 {}点 {}\n'.format(rank, u['score'], u['name'])
        score = u['score']

    context.bot.send_message(chat_id=chat_id, text=msg)


def echigoseika(update, context):
    if random.choice([True, False]):
        update.message.reply_text('＼正解は／越後製菓')
    else:
        update.message.reply_text(
            '正解は・・・越後製菓！\nhttps://www.echigoseika.co.jp/')


def bot(telegram_api_token):
    updater = Updater(telegram_api_token, use_context=True)

    dispatcher = updater.dispatcher

    GameMaster().init()

    dispatcher.add_handler(MessageHandler(
        Filters.regex(r'^越後製菓$'), echigoseika))
    dispatcher.add_handler(MessageHandler(
        Filters.regex(r'^[abcdefghijABCDEFGHIJ][123456789]$'), take))
    dispatcher.add_handler(
        CommandHandler(
            'start', start_IngressKaruta,
            filters=~Filters.update.edited_message, pass_args=True))
    dispatcher.add_handler(CommandHandler('next', nextMondai))
    dispatcher.add_handler(CommandHandler('answer', answer))
    dispatcher.add_handler(CommandHandler('score', score))

    updater.start_polling()

    updater.idle()


def run():
    fire.Fire(bot)
