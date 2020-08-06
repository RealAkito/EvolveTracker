from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.forms import ModelForm
from django import forms
from datetime import datetime
from EvolveTracker.apps.bugs.models import Issue, Comment

class TicketForm(ModelForm):
	text = forms.CharField(widget=forms.Textarea(attrs={'rows': 15, 'cols': 90, 'class': 'textarea'}))
	class Meta:
		model = Issue
		fields = "__all__"

# Create your views here.
def index(request):
	issues = Issue.objects.all()
	return render(request, "bugs/index.html", {'issues': issues, 'time': timezone.now()})

def ticketcommon(request, tktobj):
	comments = Comment.objects.filter(issue=tktobj)
	return render(request, "bugs/viewticket.html", {'time': timezone.now(), 'issue': tktobj, 'comments': comments})

def ticketid(request, id):
	return ticketcommon(request, get_object_or_404(Issue, pk=id))

def ticketuuid(request, uuid):
	return ticketcommon(request, get_object_or_404(Issue, issueuuid=uuid))

def newticket(request):
	data = request.POST.dict()
	if request.user.is_authenticated:
		data['username'] = request.user.username

	form = TicketForm(data=data, initial=request.GET)

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
		if request.user.is_authenticated:
			# make the form read-only and pre-populate the value
			form.fields['username'].widget.attrs['disabled'] = True
		return render(request, "bugs/newticket.html", {'form': form, 'time': timezone.now()})