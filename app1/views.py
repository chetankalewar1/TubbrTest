from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import EventSerializer
from rest_framework import status
from .models import Event

# Create your views here.


class AddEvent(APIView):
    def post(self, request):
        # Add Event
        event = EventSerializer(data=request.data)  # Data received from the client sent in the serializer
        if event.is_valid():
            e = event.save()  # Saving the events if data received is valid.
            data = event.data  # Get the JSON
            data['message'] = "Event Created."
            if check_for_first_bill(e.user_id):
                data['message2'] = "Congrats on your first bill pay."  # Notification on first bill
            data['status'] = status.HTTP_200_OK
        else:
            data = {'error': event.errors, 'status': status.HTTP_403_FORBIDDEN}

        return Response(data)


def check_for_first_bill(user_id):
    e = Event.objects.filter(user_id=user_id, noun='bill', verb='pay')
    if len(e) == 1:
        return True
    else:
        return False

