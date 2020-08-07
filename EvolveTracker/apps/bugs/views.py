from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseNotFound
from django.utils import timezone
from django.forms import ModelForm
from django import forms
from datetime import datetime
from captcha.fields import CaptchaField
from EvolveTracker.apps.bugs.models import Issue, Comment

class TicketForm(ModelForm):
	text = forms.CharField(widget=forms.Textarea(attrs={'rows': 15, 'cols': 90, 'class': 'textarea'}))
	capcha = CaptchaField()
	class Meta:
		model = Issue
		fields = "__all__"

# Create your views here.
def index(request):
	issues = Issue.objects.all()
	return render(request, "bugs/index.html", {'issues': issues, 'time': timezone.now()})

def ticketcommon(request, tktobj):

	data = request.POST.dict()
	# needed or django won't validate.
	data['title'] = tktobj.title
	data['device'] = tktobj.device
	if request.user.is_authenticated:
		data['username'] = request.user.username
	else:
		data['status'] = tktobj.status
		data['issuetype'] = tktobj.issuetype
		data['severity'] = tktobj.severity

	ticket = TicketForm(instance=tktobj, data=data)
	if request.user.is_authenticated and request.method == 'POST':
		ticket.fields['capcha'].required = False

	if request.method == 'POST' and ticket.is_valid():
		text = ticket.cleaned_data['text']
		# only update the fields with the form if the
		# user clicked "Submit & Update"
		if request.user.is_authenticated and "update" in request.POST:
			tktobj = ticket.save(commit=False)
			# Django already updated our object so we have to
			# get the old one before we update.
			oldobj = Issue.objects.get(pk=tktobj.pk)
			# If the user clicked the "Update" button but something
			# wasnt modified, don't add the dumb line.
			if tktobj.resolution != oldobj.resolution or tktobj.severity != oldobj.severity \
				or tktobj.issuetype != oldobj.issuetype or tktobj.status != oldobj.status or \
				tktobj.locked != oldobj.locked:
				text += "\n\n" + "\u2500" * 25 + "\n"

			# Add these to the status sections.
			if tktobj.resolution != oldobj.resolution:
				text += "\u2E30 {0} \u21E8 {1}\n".format(oldobj.get_resolution_display(), tktobj.get_resolution_display())
			if tktobj.severity != oldobj.severity:
				text += "\u2E30 {0} \u21E8 {1}\n".format(oldobj.get_severity_display(), tktobj.get_severity_display())
			if tktobj.issuetype != oldobj.issuetype:
				text += "\u2E30 {0} \u21E8 {1}\n".format(oldobj.get_issuetype_display(), tktobj.get_issuetype_display())
			if tktobj.status != oldobj.status:
				text += "\u2E30 {0} \u21E8 {1}\n".format(oldobj.get_status_display(), tktobj.get_status_display())
			if tktobj.locked != oldobj.locked:
				text += "\u2E30 Locked: {0} \u21E8 {1}\n".format("True" if oldobj.locked else "False", "True" if tktobj.locked else "False")

		# for both, we update the modified time and create a new comment.
		tktobj.updated = datetime.now()
		tktobj.save()

		# TODO: telegram message

		c = Comment(issue=tktobj, name=tktobj.username, text=text)
		c.save()
	
	comments = Comment.objects.filter(issue=tktobj).order_by("date")
	return render(request, "bugs/viewticket.html",
		{
			'time': timezone.now(),
			'issue': tktobj,
			'updateform': ticket,
			'comments': comments,
		})

def ticketid(request, id):
	return ticketcommon(request, get_object_or_404(Issue, pk=id))

def ticketuuid(request, uuid):
	return ticketcommon(request, get_object_or_404(Issue, issueuuid=uuid))

def newticket(request):
	data = request.POST.dict()
	if request.user.is_authenticated:
		data['username'] = request.user.username

	form = TicketForm(data=data, initial=request.GET)
	if request.user.is_authenticated:
		form.fields['capcha'].required = False;
		form.fields['username'].widget.attrs['disabled'] = True

	if request.method == 'POST' and form.is_valid():
		issue = form.save(commit=False)
		issue.updated = datetime.now()
		if request.user.is_authenticated:
			issue.username =  request.user.username
		issue.save()
		# We also need to make a new comment since the first
		# comment is always their description of the bug.
		comment = Comment(issue=issue, name=issue.username, text=form.cleaned_data['text'])
		comment.save()

		# TODO: do telegram message.

		# redirect to the issue page
		return redirect(issue)
	else:
		return render(request, "bugs/newticket.html", {'form': form, 'time': timezone.now()})