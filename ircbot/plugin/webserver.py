"""Provides a basic Flask server to handle webhooks and help information"""
import collections
import os
import threading
from types import ModuleType
from typing import DefaultDict
from typing import Set
from typing import TYPE_CHECKING

from flask import Flask
from flask import render_template

if TYPE_CHECKING:
    from ircbot.ircbot import Listener

app = Flask(__name__)


def register(bot):
    web_server_thread = threading.Thread(target=start_server, args=(bot,), daemon=True)
    web_server_thread.start()
    bot.threads.append(web_server_thread)


@app.route('/', methods=['GET'])
def route_base():
    plugins: DefaultDict[ModuleType, Set[Listener]] = collections.defaultdict(set)
    for listener in app.bot.listeners:
        plugins[app.bot.plugins[listener.plugin_name]].add(listener)

    return render_template(
        'help.html',
        plugins=sorted(plugins.items(), key=lambda p: p[0].__name__),
    )


@app.route('/macros', methods=['GET'])
def route_macros():
    return render_template(
        'macros.html',
        macros=app.bot.plugins['macros'].list(app.bot),
    )


def start_server(bot):
    port = os.getenv('HTTP_PORT', 8888)
    app.bot = bot
    app.run(host='0.0.0.0', port=int(port))
