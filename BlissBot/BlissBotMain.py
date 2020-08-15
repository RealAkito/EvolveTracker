#!/usr/bin/env python

import logging, re, os, sys, django, json
# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s [%(levelname)s]: %(message)s', level=logging.INFO)
logger = logging.getLogger("BlissBot")

from telegram.ext import Updater, CommandHandler, MessageHandler, filters
from twisted.application import service, internet
from twisted.internet import reactor
from prettytable import PrettyTable
from pathlib import Path
from threading import Thread
#from BlissBot import Markdown, Conch, Delivery
import Markdown, Conch, Delivery

################################################################
# Allow us to use our Django project/models
sys.path.append(str(Path.cwd().parent))
os.environ['DJANGO_SETTINGS_MODULE'] = 'EvolveTracker.settings'
# Initialize django first before imports.
django.setup()
################################################################

from EvolveTracker.apps.bugs.models import Comment, Issue
from django.urls import reverse

# Set our message regex to be compiled
MESSAGEREGEX = re.compile(r"^\#bug_(.*)")

# for Twisted
application = service.Application("BlissBot")

# For the bot itself
updater = None

################################################################
# Functions
################################################################

def Start(update, context):
	logger.info(f"User start: {update.message.from_user.id}")
	update.message.reply_text(f"Hello!")

def RegexReceiver(update, context):
	logger.info(f"Received new message which matched our regex!")
	if update.message and update.message.text:
		m = MESSAGEREGEX.match(update.message.text)
		if m:
			uuid = m.group(1)
			logger.info(f"Found match: \"{uuid}\"")

			issue = Issue.objects.get(issueuuid__startswith=uuid)
			# if the UUID didnt come back, try and find by the id
			if not issue:
				issue = Issue.objects.get(pk=uuid)

			if not issue:
				logger.info(f"No such issue {uuid}")
				update.message.reply_markdown_v2(f"I cannot find `{uuid}`.")
				return

			# We also need to get the first comment from the issue.
			comment = Comment.objects.filter(issue=issue)[0]

			x = PrettyTable()
			# We don't need field headers
			x.header = False
			# We do need field names though
			x.field_names = ["Item", "State"]
			x.add_row(["Type", issue.get_issuetype_display()])
			x.add_row(["Status", issue.get_status_display()])
			x.add_row(["Severity", issue.get_severity_display()])
			x.add_row(["Resolution", issue.get_resolution_display()])
			x.add_row(["Rooted", ("Yes" if issue.rooted else "No")])
			#x.add_row(["Device", issue.device])
			#x.add_row(["Modified", issue.updated])
			# Set alignment of the string inside the table
			x.align["State"] = "l"
			x.align["Item"] = "r"

			# Begin forming our message.
			title = Markdown.EscapeMarkdown(issue.title)
			link = Markdown.EscapeMarkdownLink(reverse('bugs:ticketuuid', kwargs={'uuid': issue.issueuuid}))
			device = Markdown.EscapeMarkdown(issue.device)
			updated = Markdown.EscapeMarkdown(issue.updated.strftime("%a, %b %-d %Y %H:%M"))
 
			# Our actual message
			msg = f"\N{Lady beetle} *Bug Report* from _{issue.username}_\n\n"
			msg += "```\n" + Markdown.EscapeMarkdownCode(x.get_string()) + "\n```\n"
			msg += f"*Device*: {device}\n*Modified*: {updated}\n\n"
			msg += f"*Title*: [{title}]({link})\n\n"
			msg += Markdown.EscapeMarkdown(comment.text)
			print(msg)
			update.message.reply_markdown_v2(msg)

def MessageReceiver(update, context):
	logger.info(f"Received update {update.update_id}!")
	if update.message:
		logger.info(f"From User: {update.message.from_user.username} - {update.message.from_user.id}")
		logger.info(f" `- Message: {update.message.text}")

################################################################
# Main
################################################################

def main():
	global updater, MESSAGEREGEX
	# hahaha nice try you aint getting my bot token!
	with open(Path.home() / ".telegram_token") as a:
		logger.info("Hello! Starting Bliss Bot...")
		updater = Updater(a.readline().strip(), use_context=True)

	commands = [
		CommandHandler('start', Start),
		MessageHandler(filters.Filters.regex(MESSAGEREGEX), RegexReceiver),
		MessageHandler(filters.Filters.all, MessageReceiver),
	]

	for c in commands:
		logger.info(f"Adding new command: {str(c)}")
		updater.dispatcher.add_handler(c)

	logger.info("Starting Twisted reactor")
	# Allow access to certain objects from the admin python shell
	Conch.CreateManhole(application, ({'updater': updater, 'website': Delivery.InitializeDelivery(application)},))
	# Twisted has to run in its own thread.
	# This is the exact reason I hate libraries (like telegram-bot) which
	# just create a .run() or .idle() function as there's no way to add
	# your own external stuff without threading and it's a stupid/bad
	# design for libraries in general. Libraries are not applications.
	t = Thread(target=reactor.run, args=(False,))
	t.start()

	updater.start_polling()
	logger.info("Entering event loop")
	updater.idle()
	logger.info("Shutting down.")
	reactor.callFromThread(reactor.stop)
	t.join()

# Start the bot.
if __name__ == '__main__':
	main()
