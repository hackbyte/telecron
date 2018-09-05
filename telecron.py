#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
################################################################################
"""
$ python3.6 telecron.py

Simple script to work on timed events for telegram api with telepot.

This is work in progress and only an example,
if you have any use for it,
have fun.

Based on:
https://github.com/nickoala/telepot/blob/master/examples/event/alarma.py

Using python_barebone from:
https://gitlab.com/hackbyte/python_barebone

v20180905164411CEST hackbyte (first variant)
 It's actually dysfunctional and serves only as a testbed.

"""

################################################################################
# first imports
import os, sys, inspect
################################################################################
################################################################################
scriptpath	= os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
scriptname	= os.path.basename(inspect.getfile(inspect.currentframe()))
if 'include' == os.path.basename(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))):
	scriptpath = os.path.dirname(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))))
else:
	scriptpath	= os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
includepath	= scriptpath + '/include'
if os.path.isdir(includepath):
	sys.path.insert(0, includepath)
#else:
#	print("No include path found!")
#	sys.exit(23)
################################################################################
import shutil, time, datetime, locale, asyncio, logging, logging.handlers
import operator, argparse
################################################################################
from pudb import set_trace 
import telepot
from telepot.aio.loop import MessageLoop
from telepot.aio.delegate import (
	per_chat_id,
	per_application,
	per_event_source_id,
	create_open,
	pave_event_space)

################################################################################
################################################################################
# set up and configure python logging.
#
logfilenamepattern = scriptname
# get rid of .py extension
if '.py' in logfilenamepattern:
	logfilenamepattern = logfilenamepattern.replace('.py','')

# create log object
log = logging.getLogger()

#logging.getLogger(__name__).addHandler(logging.NullHandler())

# by default, log all INFO messages. ;)
log.setLevel(logging.DEBUG)

# Formatting for anything not syslog (so we need our own timestamp)
logformatter_main = logging.Formatter(
	'%(asctime)s.%(msecs)03d ' +
	'%(filename)-25s ' +
	'%(module)-23s ' +
	'%(funcName)-23s ' +
	'%(lineno)4d ' +
	'%(levelname)-8s ' +
	'%(message)s',
	'%Y%m%d%H%M%S')
#	'%(processName)-12s ' +
#	'%(threadName)-12s ' +

# for syslog (so we do not need our own timestamp)
logformatter_syslog = logging.Formatter(
	'%(filename)-25s ' +
	'%(module)-23s ' +
	'%(funcName)-23s ' +
	'%(lineno)4d ' +
	'%(levelname)-8s ' +
	'%(message)s')
#	'%(processName)-12s ' +
#	'%(threadName)-12s ' +

# create console log handler (stdout/stderr)
logcons = logging.StreamHandler()
# log even debug stuff to console (if enabled below;))
logcons.setLevel(logging.DEBUG)
# make it fancy
logcons.setFormatter(logformatter_main)
# and add handler to log..
log.addHandler(logcons)

# create file handler which logs debug messages too
logfile = logging.FileHandler(logfilenamepattern + '_allmessages.log')
logfile.setLevel(logging.DEBUG)
logfile.setFormatter(logformatter_main)
log.addHandler(logfile)


################################################################################
log.debug("Program start...")

#class TeleCron(telepot.aio.helper.ChatHandler):
class TeleCron(telepot.aio.helper.Monitor):
	log.debug("Class Load")
	def __init__(self, *args, **kwargs):
		super(AlarmSetter, self).__init__(*args, **kwargs)
		log.debug("alarmsetter:")
		log.debug("args = " + str(args))
		log.debug("kwargs = " + str(kwargs))
		# 1. Customize the routing table:
		#      On seeing an event of flavor `_alarm`, call `self.on__alarm`.
		# To prevent flavors from colliding with those of Telegram messages,
		# events are given flavors prefixed with `_` by convention. Also by
		# convention is that the event-handling function is named `on_`
		# followed by flavor, leading to the double underscore.
		self.router.routing_table['_alarm'] = self.on__alarm

	# 2. Define event-handling function
	async def on__alarm(self, event):
#		print(event)  # see what the event object actually looks like
		log.debug(str(event))
		await self.sender.sendMessage('Beep beep, time to wake up!')

	async def on_chat_message(self, msg):
		log.debug("on_chat_message:")
		log.debug("self = " + str(self))
		log.debug("msg  = " + str(msg))
		try:
			delay = float(msg['text'])

			# 3. Schedule event
			#      The second argument is the event spec: a 2-tuple of (flavor, dict).
			# Put any custom data in the dict. Retrieve them in the event-handling function.
			self.scheduler.event_later(delay, ('_alarm', {'payload': delay}))
			await self.sender.sendMessage('Got it. Alarm is set at %.1f seconds from now.' % delay)
		except ValueError:
			await self.sender.sendMessage('Not a number. No alarm set.')
		log.debug("on_chat_message ended....")

	log.debug("Class Loaded")


TOKEN = sys.argv[1]

bot = telepot.aio.DelegatorBot(TOKEN, [
	pave_event_space()(
#		per_chat_id(), create_open, AlarmSetter, timeout=10),
		per_application(), create_open, AlarmSetter),
#	pave_event_space()(
#		per_event_source_id(1), create_open, TeleCron, timeout=10),
])

loop = asyncio.get_event_loop()
log.debug("loop = " + str(loop))
loop.create_task(MessageLoop(bot).run_forever())

#set_trace()

#delay=2
#bot.router.routing_table['_alarm'] = TeleCron.on__alarm
#bot.scheduler.event_later(delay, ('Telecron.on__alarm', {'payload': delay}))

log.debug('Listening ...')
loop.run_forever()
