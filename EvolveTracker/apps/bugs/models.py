from django.db import models
import uuid

STATUS_CHOICES = (
	(0, "Closed"),
	(1, "Open")
)

RESOLUTION_CHOICES = (
	(0, "Won't-Fix"),
	(1, "Fixed"),
	(2, "Rejected"),
	(3, "External Bug"),
	(4, "Not A Bug"),
	(5, "Duplicate")
)

TYPE_CHOICES = (
	(0, "Bug"),
	(1, "Feature")
)

SEVERITY_CHOICES = (
	(0, "Minor"),
	(1, "Medium"),
	(2, "High"),
	(3, "URGENT")
)

# Create your models here.
class Issue(models.Model):
	# by default django already has `pk` or `id` for database IDs we can use
	# Our issues are based on sha256sums
	issueuuid = models.CharField(max_length=64, verbose_name=u"Ticket UUID", default=uuid.uuid1())
	# The time our ticket was created
	date = models.DateTimeField(verbose_name=u"Creation Date", auto_now=True)
	# Our title
	title = models.CharField(max_length=256, verbose_name=u"Title");
	# Our status (choice field)
	status = models.IntegerField(verbose_name=u"Status", choices=STATUS_CHOICES)
	# Our resolution choices
	resolution = models.IntegerField(verbose_name=u"Resolution", choices=RESOLUTION_CHOICES)
	# Our type choices (`type` is a reserved keyword in python so we use issuetype instead)
	issuetype = models.IntegerField(verbose_name=u"Type", choices=TYPE_CHOICES)
	# Our Severity Choices
	severity = models.IntegerField(verbose_name=u"Severity", choices=SEVERITY_CHOICES)

	###
	# From here we would have comments normally but that is a different table.

class Comment(models.Model):
	# When it was created 
	date = models.DateTimeField(verbose_name=u"Creation Date", auto_now=True)
	# What this comment is associated with (only used internally in Django)
	issue = models.ForeignKey('Issue', on_delete=models.CASCADE)
	# User's name
	name = models.CharField(max_length=64, verbose_name=u"Username")
	# The comment's content
	text = models.TextField(verbose_name=u"Comment")

