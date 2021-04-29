import json
from django.db import models
from celery import shared_task
from .base_functions import send_email, send_notification
from datetime import datetime, timedelta
from django_mysql.models import JSONField
# Create your models here.


class TubbrUser(models.Model):
    name = models.CharField(max_length=250)
    email = models.EmailField(default="xyz@gmail.com")

    def __str__(self):
        return self.name


noun_choices = (
    ('bill', 'bill'),
    ('fdbk', 'fdbk'),
)
verb_choices = (
    ('pay', 'pay'),
    ('post', 'post'),
)


class Event(models.Model):
    user_id = models.ForeignKey(TubbrUser, on_delete=models.CASCADE)
    ts = models.CharField(max_length=20, default="20210428 160608")
    lat_long = models.CharField(max_length=100, null=True)
    noun = models.CharField(max_length=10, choices=noun_choices)
    verb = models.CharField(max_length=10, choices=verb_choices)
    time_spent_on_screen = models.IntegerField(null=True)
    # properties = models.TextField(null=True)
    properties = models.JSONField(null=True)

    def __str__(self):
        return self.user_id.name

    def save(self, *args, **kwargs):
        super(Event, self).save(*args, **kwargs)

        if self.noun == "bill":
            eta1 = datetime.now()+timedelta(seconds=20)  # Change to minutes
            check_for_feedback_in_time.apply_async(args=(self.id, ), eta=eta1)  # Background Task to check for feedback

        check_if_amount_exceded_in_a_given_time.delay(self.user_id)  # Task 2


@shared_task
def check_if_amount_exceded_in_a_given_time(user_id, amount=20000, mins=5):
    user = TubbrUser.objects.get(id=user_id)
    events = list(Event.objects.filter(noun="bill", verb='pay', user_id=user.id).order_by('-id')[:5])

    # Only if 5 or more than 5 events of bill pay in less than 5 mins.
    if len(events) >= 5:
        total = 0
        for event in events:
            # Converting event properties to dict/json for accessing values if JSON field not valid.
            if type(event.properties) == str:
                d1 = json.loads(event.properties)
            else:
                d1 = event.properties
            amt = float(d1['value'])  # Convert the value to float
            total = total+amt

        if total >= amount:
            ts1 = datetime.strptime(events[-1].ts, "%Y%m%d %H%M%S")  # This one is the latest and bigger in time.
            ts2 = datetime.strptime(events[0].ts, "%Y%m%d %H%M%S")

            # Checking the time difference between first and last event.
            if ts2-ts1 <= timedelta(minutes=mins):
                # Send Email
                message = "Payment of Total Rs."+str(total)+" was made under "+str(mins)+"mins from your account."
                subject = "Unusual Activity"
                send_email(to=user.email, message=message, subject=subject)  # Send EMail
                send_notification(to=user.email, message=message, subject=subject)  # Send Notification
            else:
                print("All okay")


@shared_task
def check_for_feedback_in_time(event_id):
    event = Event.objects.get(id=event_id)  # This should be a bill pay event
    events = list(Event.objects.filter(noun="fdbk", verb="post", user_id=event.user_id))  # Getting all the fdbk events.
    ts1 = datetime.strptime(event.ts, "%Y%m%d %H%M%S")  # Change to proper datetime format for processing

    for evnt in events:
        ts2 = datetime.strptime(evnt.ts, "%Y%m%d %H%M%S")
        if ts2 < ts1:  # CHeck if the feedback timing is for the previous event.
            events.remove(event)

    # If no events left
    if not len(events):
        subject = "Notification for no feedback"
        message = "No feedback received from"+str(event.user_id)+"yet."
        send_email(to="TUBBRoperator@gmail.com", message=message, subject=subject)  # Send EMail
        send_notification(to="TUBBRoperator@gmail.com", message=message, subject=subject)  # Send Notification



