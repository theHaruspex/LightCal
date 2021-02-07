from flask import Flask, request, redirect
from twilio.twiml.messaging_response import MessagingResponse

import calendar_manipulation as f

app = Flask(__name__)


@app.route("/sms", methods=['GET', 'POST'])
def sms_reply():
    number = request.form['From']
    message_body = request.form['Body'].lower()

    # See today's events.
    if message_body == 'today':
        resp = MessagingResponse()
        events_str = f.today_events()
        resp.message(events_str)
        return str(resp)

    # See tomorrow's events.
    elif message_body == 'tomorrow':
        resp = MessagingResponse()
        events_str = f.tomorrow_events()
        resp.message(events_str)
        return str(resp)

    # Add event.
    elif message_body.startswith('add'):
        resp = MessagingResponse()
        function_input = message_body[4:]
        event = f.create_event(function_input)
        response = f'Created: {f.display_event(event)}'
        resp.message(response)
        return str(resp)

    # Delete most recent event.
    elif message_body == 'del':
        resp = MessagingResponse()
        event = f.get_most_recent_added_event()
        if event == None:
            response = 'No events found.'
            resp.message(response)
            return str(resp)
        else:
            deleted_event = f.delete_event(event)
            response = f'Deleted: {f.display_event(deleted_event)}'
            resp.message(response)
            return str(resp)

    # Delete a selected event.
    elif message_body.startswith('del'):
        search_term = ' '.join(message_body.split(' ')[1:-2])
        resp = MessagingResponse()
        function_input = message_body[4:]
        try:
            deleted_event = f.delete_from_user_input(function_input)
            if deleted_event == None:
                response = f"No events found under '{search_term}.'"
                resp.message(response)
                return str(resp)
            else:
                response = f'Deleted: {f.display_event(deleted_event)}'
                resp.message(response)
                return str(resp)
        except ValueError:
            error_message = '''Valid month entries:
            jan, feb, mar, apr, may, jun, jul, aug, sep, oct, nov, dev'''
            resp.message(error_message)
            return str(resp)

    # Otherwise, if the text doesn't match any commands.
    else:
        resp = MessagingResponse()
        error_message = '''Valid Commands:
        [today ],
        [add ],
        [del ]'''
        resp.message(error_message)
        return str(resp)


if __name__ == "__main__":
    app.run(debug=True)
