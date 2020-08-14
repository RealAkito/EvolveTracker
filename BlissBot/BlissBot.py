#!/usr/bin/env python

from telegram.ext import Updater, CommandHandler, MessageHandler, filters
from prettytable import PrettyTable
from pathlib import Path
import logging, re, os, sys, django

# Allow us to use our Django project/models
sys.path.append(str(Path.cwd().parent))
os.environ['DJANGO_SETTINGS_MODULE'] = 'EvolveTracker.settings'
# Initialize django first before imports.
django.setup()

from EvolveTracker.apps.bugs.models import Comment, Issue
from django.urls import reverse

MESSAGEREGEX = re.compile(r"^\#bug_(.*)")

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s [%(levelname)s]: %(message)s', level=logging.INFO)
logger = logging.getLogger("BlissBot")

def Escape(text, restricted):
	for char in restricted:
		text = text.replace(char, f"\\{char}")
	return text

def EscapeMarkdownLink(text):
	return Escape(text, [')', '\\'])

def EscapeMarkdownCode(text):
	return Escape(text, ['`', '\\'])

def EscapeMarkdown(text):
	return Escape(text, ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!'])

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

			issue = Issue.objects.get(issueuuid=uuid)
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
			title = EscapeMarkdown(issue.title)
			link = EscapeMarkdownLink(reverse('bugs:ticketuuid', kwargs={'uuid': issue.issueuuid}))
			device = EscapeMarkdown(issue.device)
			updated = EscapeMarkdown(issue.updated.strftime("%a, %b %-d %Y %H:%M"))

			# Our actual message
			msg = f"\N{Lady beetle} *Bug Report* from _{issue.username}_\n\n"
			msg += "```\n" + EscapeMarkdownCode(x.get_string()) + "\n```\n"
			msg += f"*Device*: {device}\n*Modified*: {updated}\n\n"
			msg += f"*Title*: [{title}]({link})\n\n"
			msg += EscapeMarkdown(comment.text)
			print(msg)
			update.message.reply_markdown_v2(msg)

def MessageReceiver(update, context):
	logger.info(f"Received update {update.update_id}!")
	if update.message:
		logger.info(f"From User: {update.message.from_user.username} - {update.message.from_user.id}")
		logger.info(f" `- Message: {update.message.text}")

def main():
	# hahaha nice try you aint getting my bot token!
	with open(Path.home() / ".telegram_token") as a:
		logger.info("Hello! Starting Bliss Bot...")
		updater = Updater(a.readline().strip(), use_context=True)

		commands = [
			CommandHandler('start', Start),
			MessageHandler(filters.Filters.all, MessageReceiver),
			MessageHandler(filters.regex(r'^\#bug_(.*)'), RegexReceiver)
		]

		for c in commands:
			logger.info(f"Adding new command: {str(c)}")
			updater.dispatcher.add_handler(c)

		updater.start_polling()
		logger.info("Entering event loop")
		updater.idle()

# Start the bot.
if __name__ == '__main__':
	main()
