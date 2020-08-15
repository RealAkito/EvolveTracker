from django.db import models
from django.urls import reverse
import uuid

STATUS_CHOICES = ((0, "Open"), (1, "Closed"))

RESOLUTION_CHOICES = ((0, "Won't-Fix"), (1, "Fixed"), (2, "Rejected"),
                      (3, "External Bug"), (4, "Not A Bug"), (5, "Duplicate"),
                      (6, "Confirmed"))

TYPE_CHOICES = ((0, "Bug"), (1, "Feature"))

SEVERITY_CHOICES = ((0, "Minor"), (1, "Medium"), (2, "High"), (3, "URGENT"))


# Create your models here.
class Issue(models.Model):
    # by default django already has `pk` or `id` for database IDs we can use
    # Our issues are based on sha256sums
    issueuuid = models.CharField(max_length=64,
                                 verbose_name=u"Ticket UUID",
                                 default=uuid.uuid4().hex,
                                 blank=True)
    # The time our ticket was created
    date = models.DateTimeField(verbose_name=u"Creation Date", auto_now=True)
    # The time our ticket was modified
    updated = models.DateTimeField(verbose_name=u"Update Date", auto_now=True)
    # Our title
    title = models.CharField(max_length=256, verbose_name=u"Title")
    # Our status (choice field)
    status = models.IntegerField(verbose_name=u"Status",
                                 choices=STATUS_CHOICES,
                                 default=1)
    # Our resolution choices
    resolution = models.IntegerField(verbose_name=u"Resolution",
                                     choices=RESOLUTION_CHOICES,
                                     null=True,
                                     blank=True)
    # Our type choices (`type` is a reserved keyword in python so we use issuetype instead)
    issuetype = models.IntegerField(verbose_name=u"Type",
                                    choices=TYPE_CHOICES,
                                    default=0)
    # Our Severity Choices
    severity = models.IntegerField(verbose_name=u"Severity",
                                   choices=SEVERITY_CHOICES,
                                   default=0)
    # Whether the user is rooted or not
    rooted = models.BooleanField(verbose_name=u"Device is Rooted",
                                 default=False)
    # What the user's device is
    device = models.CharField(max_length=64, verbose_name=u"Device")
    # The user's name
    username = models.CharField(max_length=64, verbose_name=u"Username")
    # Whether this issue allows comments
    locked = models.BooleanField(default=False, verbose_name=u"Locked")

    def __str__(self):
        return f"{self.username}: {self.title}"

    def get_absolute_url(self):
        return reverse("bugs:ticketuuid", kwargs={"uuid": self.issueuuid})

    def GetShortUUID(self):
        return self.issueuuid[:10]

    # Get the color that should be displayed
    def GetColor(self):
        # if the bug is closed, mark it green.
        if self.status == 1:
            return "#C7FFCC"
        else:
            # if the bug is a feature, mark it blue
            if self.issuetype == 1:
                return "#5C6BFF"
            # if the bug is minor severity, do red
            if self.severity == 0:
                return "#FFC9C7"
            # Medium severity is Yellow
            elif self.severity == 1:
                return "#FFFEC7"
            # Major severity is Orange
            elif self.severity == 2:
                return "#FFC25C"
            # URGENT severity is bright red
            elif self.severity == 3:
                return "#FF5C78"
        # if no color was picked, mark it grey
        return None

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

    def __str__(self):
        return f"{self.name}: {self.text[:64]}"
