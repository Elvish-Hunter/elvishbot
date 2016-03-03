Elvishbot
=========

What's this thing?
------------------

**Elvishbot** is a simple IRC bot written in Python and based on the [WeeChat](https://weechat.org) client. It's licensed under the General Public License version 3, a copy of which is included in this repository.

It is inspired from the [Minosse](http://wif.altervista.org/index.php/topic,2910.0.html) bot, which is made by Nobun. Just like its predecessor, its main purpose is to help organizing the Wesnoth Italian Forum tournaments - but it isn't its only one!

How do I use it?
----------------

If the bot is already in the channel, type `<bot nick>: help` to receive a series of notices with all the supported commands. Or you can just read the list of commands in the _help() function.

It is worth mentioning that the bot doesn't answer to private queries - this is a deliberate choice.

How do I install it?
--------------------

First of all, you'll need a copy of WeeChat (I used the 1.4 version).

If you're on Linux, be careful about using the version available in your package manager: given WeeChat's rapid development cycle, your version may very well be outdated, so you should open their website and install the latest stable version from there. They also have a repository for Ubuntu and Debian users.  
If you compile WeeChat on your own, please note that the script works on Python 2, and it *should* work on Python 3 by removing the `from __future__ import division` line.

If you're on Windows, you'll have to install [Cygwin](https://www.cygwin.com/) and choose at least the `weechat-1.4-1` and `weechat-python-1.4-1` packages, as well as a Python version (like the `python-2.7.10-1` package).  
**WARNING:** *you must install Python 2 from within Cygwin.* A normal Windows installation of Python won't work with WeeChat.

After you installed your copy of WeeChat, start it with the command

	weechat -d ~/.elvishbot

This will create a hidden `.elvishbot` directory in your home directory; you can change `.elvishbot` with any other directory name, as you like. After fixing WeeChat's settings to suit your needs, you have two choices:

1. You can copy the `elvishbot.py` file in your `~/.elvishbot/python` directory. This way, you'll be able to start the bot by typing `/script load elvishbot` in WeeChat.
2. You can copy the `elvishbot.py` file in your `~/.elvishbot/python/autoload` directory. This way, the bot will start each time that you open WeeChat.

In both cases, you can also place the `elvishbot.py` file elsewhere and create a symlink (`ln -s`) in one of the aforementioned directories.

After starting the script, you can use the usual commands to connect to a network and join a channel. *Be sure, however, to use the bot only in networks and channels that allow you to do so!*

It is recommended to *not* install the bot in your main WeeChat data directory (usually `~/.weechat`), hence the reason for creating and using a separate data directory. You don't want to create confusion by having both your messages and the bot's answers coming from the same nick, do you?

What if I have a suggestion, or I found a bug?
----------------------------------------------

In that case, please remember that *it doesn't work* is not a valid bug report. Be clear in your report, and don't forget to include the necessary steps to reproduce the problem (what IRC message caused it, for example).

That said, you can open an issue or a pull request on GitHub; if you choose to do so, please write in English.

Alternatively, you can post in the official thread in the [Wesnoth Italian Forum](http://wif.altervista.org/index.php/topic,3157.0.html); there, you'll have to write in Italian.

Have fun,  
Elvish_Hunter
