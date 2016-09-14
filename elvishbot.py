#! /usr/bin/env python2
# coding: utf8

from __future__ import division
    
import random
import sys

try:
    import weechat
except ImportError:
    print "This script must be run from within the WeeChat IRC client"
    sys.exit(1)

VERSION = "1.0.0"

weechat.register("elvishbot", # name
                 "Elvish_Hunter", # author
                 VERSION, # version
                 "GPL v3", #license
                 "A IRC bot based on WeeChat, useful for organizing the Wesnoth Italian Forum's tournaments", # description
                 "", # shutdown function
                 "utf8") # charset

# custom data types, global variables and constants

class BufferInfos(object):
    def __init__(self):
        self.list_a = []
        self.list_b = []
    def clear_list_a(self):
        if sys.version_info.major > 3 or \
           sys.version_info.major == 3 and sys.version_info.minor >= 3:
            self.list_a.clear()
        else:
            del self.list_a[:]
    def clear_list_b(self):
        if sys.version_info.major > 3 or \
           sys.version_info.major == 3 and sys.version_info.minor >= 3:
            self.list_b.clear()
        else:
            del self.list_b[:]
    def clear_lists(self):
        self.clear_list_a()
        self.clear_list_b()

buffer_data = {}
server_status_allowed = True
cached_server_result = False
A, B = "A", "B"

# command handlers
# each command is associated to a handler
# said handler must always return a string with a message
# IRC commands can be returned with the usual slash syntax
# multiline strings are automatically split in more messages
# and are sent out respecting WeeChat's antiflood

def _help(nick):
    # it is more polite for bots to use /NOTICE instead of /MSG or /QUERY
    return """{0}: I'm sending you the command list in private
/NOTICE {0} Currently supported commands:
/NOTICE {0} help: shows this message
/NOTICE {0} about: infos about me
/NOTICE {0} coin: tosses a coin
/NOTICE {0} server: prints the address of the Italian server and checks its status (updated to the last 5 minutes)
/NOTICE {0} coffee: makes a cup of coffee, duh!
/NOTICE {0} dice <n>: throws a n-sided dice, if n is not supplied throws a six-sided dice
/NOTICE {0} rps <choice>: plays a game of rock, paper, scissors (replace <choice> with one of them)
/NOTICE {0} This bot can also handle two lists (each of them can contain up to 99 items), called 'A' and 'B'. These are the related commands:
/NOTICE {0} list clear <optional list>: deletes the content of the supplied list; if no list is specified, deletes the content of both lists
/NOTICE {0} list show: shows the content of both lists, assigning an index to each element
/NOTICE {0} list add <list> <items>: adds the specified items, separated by commas, to the specified list
/NOTICE {0} list remove <list> <items>: removes the specified items, separated by commas, from the specified list
/NOTICE {0} list extract <list>: returns and removes one item from the specified list
/NOTICE {0} list makepairs: associates each item from list A with one element from list B; both lists must have the same number of items
/NOTICE {0} list makepairs <list>: if the number of items of the specified list is even, creates pairs with the elements of said list 
/NOTICE {0} list pair: extracts a pair of elements, picking one element from each list if both contain at least one element, otherwise picks both elements from the same list
/NOTICE {0} list pop <list> <index>: removes the item matching the specified index from the specified list; to see the indexes, use the 'list show' command
/NOTICE {0} End of command list""".format(nick)

def _coin():
    return random.choice(("Heads", "Tails"))

def _dice(arg):
    if not arg: # empty string
        return str(random.randint(1,6))
    else:
        try:
            limit = int(arg)
            if not 2 <= limit <= 1000:
                raise ValueError
        except ValueError:
            return "Invalid argument, it must be an integer number between 2 and 1000"
        return str(random.randint(1,limit))

def _allow_server_check(data, remaining_calls):
    global server_status_allowed
    server_status_allowed = True

    return weechat.WEECHAT_RC_OK

def _server():
    global server_status_allowed
    global cached_server_result

    if server_status_allowed:
        # allow running the command at most every 5 minutes
        # otherwise rely on the cached result
        server_status_allowed = False
        weechat.hook_timer(5 * 60 * 1000, 60, 1, "_allow_server_check", "")

        # this is an extremely condensed version of the Valen script
        # https://github.com/shikadilord/valen/blob/master/bin/valen.pl
        try:
            # format:
            # first 4 bytes are connection ID
            # second 4 bytes are the length of the following packet
            # eveything else is the gzipped packet itself
            sock = socket.create_connection(("laltromondo.mooo.com", 15000), 10)
            # handshake
            sock.send(struct.pack(">I", 0))
            # discard connection number
            sock.recv(4)
            # check the actual packet's length
            packet_length = struct.unpack(">I", sock.recv(4))[0]
            answer = sock.recv(packet_length)
            sock.close()
            # check if the server answered in gzipped WML
            if re.match(br'\[(version|mustlogin)\]\n\[/\1\]\n',
                        gzip.decompress(answer)):
                cached_server_result = True
            else:
                cached_server_result = False
        except (IOError, OSError): # raised both on connection issues and gzip problems
            cached_server_result = False

    # these are mIRC color codes; green when the server is active, red otherwise
    # a good reference is available here: https://github.com/myano/jenni/wiki/IRC-String-Formatting
    res = "\x02\x0303ONLINE\x0f" if cached_server_result else "\x0304OFFLINE\x0f"

    return "The Italian Wesnoth MP server is: laltromondo.mooo.com:15000 | Current status: " + res

def _about():
    return "elvishbot {0} - a GPL v3 IRC bot based on WeeChat - by Elvish_Hunter, 2016".format(VERSION)

def _rps(nick, player_choice):
    if not player_choice:
        return "No choice made, it must be one of 'rock', 'paper' or 'scissors'"
    ROCK, PAPER, SCISSORS = "rock", "paper", "scissors"
    choices = (ROCK, PAPER, SCISSORS)
    player_choice = player_choice.lower()
    if player_choice not in choices:
        return "Invalid choice, it must be one of 'rock', 'paper', 'scissors"
    bot_choice = random.choice(choices)
    # nine possible choices
    # three lead to a tie
    if player_choice == bot_choice:
        return "I chose {0}. {1} chose {2}. It's a tie".format(bot_choice, nick, player_choice)
    # three lead to a player's win
    # tuples are compared by number of elements, elements position and element values
    if (player_choice, bot_choice) in ((ROCK, SCISSORS),(PAPER, ROCK),(SCISSORS, PAPER)):
        return "I chose {0}. {1} chose {2}. You win".format(bot_choice, nick, player_choice)
    # and these three lead to the computer's victory
    if (bot_choice, player_choice) in ((ROCK, SCISSORS),(PAPER, ROCK),(SCISSORS, PAPER)):
        return "I chose {0}. {1} chose {2}. I win".format(bot_choice, nick, player_choice)
    # We're not even supposed to reach this point!
    return "An error has occurred"

def _list(target, nick, command):
    global buffer_data
    # WARNING: we can't be sure that the data has been created by now!
    # This may be due to a script reload, or to some event not yet bound
    # so the bot is already in the channel without joining
    if target not in buffer_data:
        buffer_data[target] = BufferInfos() # no data for any reason, create it now
    # since lists are a mutable type, they're handled by reference
    list_a = buffer_data[target].list_a
    list_b = buffer_data[target].list_b

    command = command.lstrip()
    s = command.split(" ", 2)
    mode = s[0].lower() # in the worst case, this will be an empty string
    list_name = s[1].upper() if (len(s) > 1 and s[1] in ("a","A","b","B")) else None
    args = s[2] if len(s) > 2 else None

    if mode == "clear":
        if not list_name:
            buffer_data[target].clear_lists()
            return "Both lists are now empty"
        elif list_name == A:
            buffer_data[target].clear_list_a()
            return "List A is now empty"
        elif list_name == B:
            buffer_data[target].clear_list_b()
            return "List B is now empty"
        else:
            return "Invalid list name, it must be either 'A' or 'B'"
    elif mode == "show":
        out_msg = ["{0}: I'm sending you the lists' content in private".format(nick)]
        if list_a: # don't forget that empty lists cast as False
            out_msg.append("/NOTICE {0} Content of list A:".format(nick))
            for index, value in enumerate(list_a, start = 1):
                out_msg.append("/NOTICE {0} {1:02d}) {2}".format(nick, index, value))
        else:
            out_msg.append("/NOTICE {0} List A is empty".format(nick))
        if list_b:
            out_msg.append("/NOTICE {0} Content of list B:".format(nick))
            for index, value in enumerate(list_b, start = 1):
                out_msg.append("/NOTICE {0} {1:02d}) {2}".format(nick, index, value))
        else:
            out_msg.append("/NOTICE {0} List B is empty".format(nick))
        out_msg.append("/NOTICE {0} End of lists' content".format(nick))
        return "\n".join(out_msg)
    elif mode == "add":
        if list_name not in (A, B):
            return "Missing or invalid list name, it must be either 'A' or 'B'"
        if not args:
            return "No elements to add to list"
        # if args is empty, so will be the list
        # split list on commas and add elements stripped of whitespaces
        # discard empty elements and elements made only of whitespaces
        new_elems = [elem.strip() for elem in args.split(",") if (elem and not elem.isspace())]
        if not new_elems:
            return "No elements to add to list"
        if list_name == A:
            # limit length of lists
            if (len(list_a) + len(new_elems)) > 99:
                return "Each list can contain, at most, 99 elements"
            list_a += new_elems
            return "Added elements to list A: " + ", ".join(new_elems)
        elif list_name == B:
            if (len(list_b) + len(new_elems)) > 99:
                return "Each list can contain, at most, 99 elements"
            list_b += new_elems
            return "Added elements to list B: " + ", ".join(new_elems)
    elif mode == "makepairs":
        # check if list name is supplied, and make pairs from it if so
        # require that the list's lenght is even
        if list_name:
            if list_name not in (A, B):
                return "Invalid list name, it must be either 'A' or 'B'"
            elif (list_name == A and len(list_a) % 2 != 0) or \
               (list_name == B and len(list_b) % 2 != 0):
                return "Cannot make pairs, as the chosen list must have an even amount of elements"
            elif (list_name == A and not list_a) or (list_name == B and not list_b):
                return "Cannot make pairs, since the chosen list is empty"
        # otherwise make pairs from both lists
        else:
            if not (list_a or list_b):
                return "Cannot make pairs, since both lists are empty"
            elif len(list_a) != len(list_b):
                return "Cannot make pairs, as both lists must have the same amount of elements"
        if list_name == A:
            random.shuffle(list_a)
            half = len(list_a)//2
            pairs = [pair for pair in zip(list_a[:half], list_a[half:])]
        elif list_name == B:
            random.shuffle(list_b)
            half = len(list_b)//2
            pairs = [pair for pair in zip(list_b[:half], list_b[half:])]
        else:
            random.shuffle(list_a)
            random.shuffle(list_b)
            pairs = [pair for pair in zip(list_a, list_b)]
        out_msg = ["Pairs:"]
        for num, pair in enumerate(pairs, start=1):
            out_msg.append("{0:02d}) {1} - {2}".format(num, pair[0], pair[1]))
        if list_name == A:
            buffer_data[target].clear_list_a()
            out_msg.append("End of pairs, list A is now empty")
        elif list_name == B:
            buffer_data[target].clear_list_b()
            out_msg.append("End of pairs, list B is now empty")
        else:
            buffer_data[target].clear_lists()
            out_msg.append("End of pairs, both lists are now empty")
        return "\n".join(out_msg)
    elif mode == "pair":
        # case 1: no name in both lists
        # case 2: only one name between the two lists, so no pairings
        # case 3: if both lists contain at least one name, pick one from both
        # case 4: list B is empty, pick both names from list A
        # case 5: list A is empty, pick both names from list B
        if not (list_a or list_b):
            return "Cannot create a pair: both lists are empty"
        elif len(list_a) + len(list_b) == 1:
            return "Cannot create a pair: one of the lists is empty and the other contains only one item"
        elif list_a and list_b:
            index_a = random.randint(0, len(list_a)-1)
            index_b = random.randint(0, len(list_b)-1)
            return "Pair extracted: {0} (list A) - {1} (list B)".format(list_a.pop(index_a), list_b.pop(index_b))
        elif list_a:
            item_1st = list_a.pop(random.randint(0, len(list_a)-1))
            item_2nd = list_a.pop(random.randint(0, len(list_a)-1))
            return "Pair extracted: {0} - {1} (both from list A)".format(item_1st, item_2nd)
        elif list_b:
            item_1st = list_b.pop(random.randint(0, len(list_b)-1))
            item_2nd = list_b.pop(random.randint(0, len(list_b)-1))
            return "Pair extracted: {0} - {1} (both from list B)".format(item_1st, item_2nd)
        else:
            return "An error has occurred"
    elif mode == "pop": # remove single element based on index
        if list_name not in (A, B):
            return "Missing or invalid list name, it must be either 'A' or 'B'"
        try:
            index = int(args)
        except ValueError:
            return "The pop command requires an integer number as argument"
        if (list_name == A and not list_a) or (list_name == B and not list_b):
            return "The selected list is empty"
        if list_name == A:
            upper_limit = len(list_a)
        elif list_name == B:
            upper_limit = len(list_b)
        if not 0 < index <= upper_limit:
            return "The supplied index must be greater than 0 and equal, at most, to the list's length"
        if list_name == A:
            value = list_a.pop(index - 1)
        elif list_name == B:
            value = list_b.pop(index - 1)
        return "The element {0} at index {1:d} was succesfully removed from list {2}".format(value, index, list_name)
    elif mode == "remove":
        if list_name not in (A, B):
            return "Missing or invalid list name, it must be either 'A' or 'B'"
        if (list_name == A and not list_a) or (list_name == B and not list_b):
            return "The selected list is empty"
        if not args:
            return "No elements to delete from list"
        del_elems = [elem.strip() for elem in args.split(",") if (elem and not elem.isspace())]
        if not del_elems:
            return "No elements to delete from list"
        removed = []
        missing = []
        for elem in del_elems:
            try:
                if list_name == A:
                    list_a.remove(elem)
                elif list_name == B:
                    list_b.remove(elem)
                removed.append(elem)
            except ValueError:
                missing.append(elem)
        out_msg = []
        if removed:
            out_msg.append("Elements successfully removed: " + ", ".join(removed))
        if missing:
            out_msg.append("Elements not present in list: " + ", ".join(missing))
        return "\n".join(out_msg)
    elif mode == "extract":
        if list_name not in (A, B):
            return "Missing or invalid list name, it must be either 'A' or 'B'"
        if (list_name == A and not list_a) or (list_name == B and not list_b):
            return "The selected list is empty"
        out_msg = []
        if list_name == A:
            elem = list_a.pop(random.randint(0,len(list_a)-1))
            out_msg.append("Element extracted: {0}".format(elem))
            if len(list_a) == 1:
                out_msg.append("List A now contains only one item")
            elif not list_a:
                out_msg.append("List A is now empty")
        elif list_name == B:
            elem = list_b.pop(random.randint(0,len(list_b)-1))
            out_msg.append("Element extracted: {0}".format(elem))
            if len(list_b) == 1:
                out_msg.append("List B now contains only one item")
            elif not list_b:
                out_msg.append("List B is now empty")
        return "\n".join(out_msg) 
    else:
        return "Missing or invalid arguments for list command"

def _coffee():
    return "c[_]"

def _8ball():
    # answers are taken from the Atheme project, which is released as open source
    # https://github.com/atheme/atheme
    # another set of answers is available here: https://en.wikipedia.org/wiki/Magic_8-Ball
    answers = (
        "Absolutely yes!",
        "Prospect looks hopeful.",
        "I'd like to think so.",
        "Yes, yes, yes, and yes again.",
        "Most likely.",
        "All signs point to yes.",
        "Yes.",
        "Without a doubt.",
        "Sometime in the near future.",
        "Of course!",
        "Definitely.",
        "Answer hazy.",
        "Prospect looks bleak.",
        "That's a question you should ask yourself.",
        "Maybe.",
        "That question is better remained unanswered.",
        "The stars would have to align for that to happen.",
        "No.",
        "Not even on a GOOD day.",
        "It would take a disturbed person to even ask.",
        "You wish.",
        "Not bloody likely.",
        "No way.",
        "Never.",
        "NO!",
        "Over my dead body.",
        "We won't go there",
        "No chance at all!"
        )
    return random.choice(answers)

# signal handlers
# each of them must have the data, signal, signal_data arguments
# and must be hooked to a WeeChat signal

def handle_query(data, signal, signal_data):
    global buffer_data
    # data: empty string
    # signal: <server>,irc_in_PRIVMSG
    # signal_data: whole message unparsed
    # parse the message
    parsed = weechat.info_get_hashtable("irc_message_parse",
                                        {"message": signal_data})
    # where should we answer?
    server = signal.split(",")[0]
    channel = parsed["channel"]
    current_nick = weechat.info_get("irc_nick", server)
    user = parsed["nick"]
    message = parsed["text"]

    if channel == current_nick:
        # we got a message through a private query, refuse it
        buffer_out = weechat.info_get("irc_buffer", server + "," + user)
        # close private buffers, but not server buffers
        # localvar_type can assume five values: private, channel, server, weechat and ""
        if weechat.buffer_get_string(buffer_out,"localvar_type") == "private":
            weechat.command(buffer_out, "How about speaking to me in public?")
            weechat.buffer_close(buffer_out)
    else:
        # query came from public channel
        if message.startswith(current_nick + ":"): # it's a command to our bot
            query = message.split(":")[1].strip() # remove the part before the colon, and lead/trail whitespaces
            s = query.split(" ", 1)
            command = s[0].lower() # command is case-insensitive
            args = s[1] if len(s) == 2 else ""
            target = "{0},{1}".format(server, channel) # this is the key to the dict containing the lists
            if command == "coin":
                out_msg = _coin()
            elif command == "help":
                out_msg = _help(user)
            elif command == "dice":
                out_msg = _dice(args)
            elif command == "server":
                out_msg = _server()
            elif command == "about":
                out_msg = _about()
            elif command == "rps":
                out_msg = _rps(user, args)
            elif command == "list":
                out_msg = _list(target,user,args)
            elif command == "coffee":
                out_msg = _coffee()
            elif command == "eightball":
                out_msg = _8ball()
            else:
                out_msg = "Unrecognized command. Type '{0}: help' to get a list of commands".format(current_nick)

            buffer_out = weechat.info_get("irc_buffer", server + "," + channel)
            if weechat.buffer_get_string(buffer_out,"localvar_type") == "channel":
                weechat.command(buffer_out, out_msg)

    return weechat.WEECHAT_RC_OK # must always return this or WEECHAT_RC_ERROR

def on_join(data, signal, signal_data):
    # create a dict entry in buffer_data on each join
    # and delete it on each part
    # the key will be the server's name, a comma, then the channel's name
    # the value will be an instance of BufferInfos
    global buffer_data
    server = signal.split(",")[0]
    channel = signal_data.split("JOIN :")[1]
    nick = signal_data.split("!")[0].strip(":")
    current_nick = weechat.info_get("irc_nick", server)
    if nick == current_nick: # the bot joined a channel
        buffer_data["{0},{1}".format(server, channel)] = BufferInfos()
    return weechat.WEECHAT_RC_OK

def on_part(data, signal, signal_data):
    global buffer_data
    server = signal.split(",")[0]
    channel = signal_data.split(" ")[2]
    nick = signal_data.split("!")[0].strip(":")
    current_nick = weechat.info_get("irc_nick", server)
    if nick == current_nick: # the bot left a channel
        try:
            del buffer_data["{0},{1}".format(server, channel)]
        except KeyError:
            weechat.prnt("","No buffer data for {0},{1}, skipping".format(server, channel))
    return weechat.WEECHAT_RC_OK

def on_kick(data, signal, signal_data):
    global buffer_data
    server = signal.split(",")[0]
    channel = signal_data.split(" ")[2]
    nick = signal_data.split(" ")[3]
    current_nick = weechat.info_get("irc_nick", server)
    if nick == current_nick: # the bot was kicked from a channel
        try:
            del buffer_data["{0},{1}".format(server, channel)]
        except KeyError:
            weechat.prnt("","No buffer data for {0},{1}, skipping".format(server, channel))
    return weechat.WEECHAT_RC_OK

# signal hooks
# the in2 part avoids the answer appearing before the query in the weechat instance
weechat.hook_signal("*,irc_in2_privmsg","handle_query","")
weechat.hook_signal("*,irc_in2_join","on_join","")
weechat.hook_signal("*,irc_in2_part","on_part","")
weechat.hook_signal("*,irc_in2_kick","on_kick","")
