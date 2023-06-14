from pathlib import Path
import sys
path_root = Path(__file__).parents[2]
sys.path.append(str(path_root))
# print(sys.path)

from helpers.setup_openai import OPENAI_MODULE as openai
from helpers.get_completion_llm import (
    get_completion_from_messages
)
import json

import panel as pn  # GUI
pn.extension()

panels = [] # collect display
bot_context = [ {'role':'system', 'content':"""
You are OrderBot, an automated service to collect orders for a pizza restaurant. \
You first greet the customer, then collects the order, \
and then asks if it's a pickup or delivery. \
You wait to collect the entire order, then summarize it and check for a final \
time if the customer wants to add anything else. \
If it's a delivery, you ask for an address. \
Finally you collect the payment.\
Make sure to clarify all options, extras and sizes to uniquely \
identify the item from the menu.\
You respond in a short, very conversational friendly style. \
The menu includes: \
pepperoni pizza  12.95, 10.00, 7.00 \
cheese pizza   10.95, 9.25, 6.50 \
eggplant pizza   11.95, 9.75, 6.75 \
fries 4.50, 3.50 \
greek salad 7.25 \
Toppings: \
extra cheese 2.00, \
mushrooms 1.50 \
sausage 3.00 \
canadian bacon 3.50 \
AI sauce 1.50 \
peppers 1.00 \
Drinks: \
coke 3.00, 2.00, 1.00 \
sprite 3.00, 2.00, 1.00 \
bottled water 5.00 \
Make sure to add 'Thank you for using OrderBot' at the end when the customer completed their order.
"""} ]  # accumulate messages

# Finally format your response for the customer as a JSON object with 'orderbot_response' and 'order_is_completed' as keys. \
# The key 'order_is_completed' must be a boolean indicating the user completed their order.

# Create a chatgpt response from user prompt and context, as well as adding
# the visual elements to the page
def collect_messages(_):
    prompt = input.value_input
    input.value = ''
    bot_context.append({'role':'user', 'content':f"{prompt}"})
    response = get_completion_from_messages(openai, bot_context)
    # print(response)
    # response_dict = json.loads(response)
    bot_context.append({'role':'assistant', 'content':f"{response}"})
    panels.append(
        pn.Row('User:', pn.pane.Markdown(prompt, width=600)))
    panels.append(
        pn.Row('Assistant:', pn.pane.Markdown(response, width=600, style={'background-color': '#F6F6F6'})))

    return pn.Column(*panels)

# Create the layout for the page
def create_layout(input, row, panel):
    return pn.Column(
        input,
        pn.Row(row),
        pn.panel(panel, loading_indicator=True, height=300),
    )

input = pn.widgets.TextInput(value="Hi", placeholder='Enter text here…')
button_conversation = pn.widgets.Button(name="Chat!")
interactive_conversation = pn.bind(collect_messages, button_conversation)
dashboard_layout = create_layout(input, button_conversation, interactive_conversation)

# Setup panel server
def run_panel_server(layout):
    pn.template.FastListTemplate(
        site="Panel", title="Example", main=[layout],
    ).servable()

run_panel_server(dashboard_layout)

# After the order is done, request a json format with the summary of it
def get_formatted_order():
    messages =  bot_context.copy()
    messages.append(
    {'role':'system', 'content':'create a json summary of the previous food order. Itemize the price for each item\
     The fields should be 1) pizza, include size 2) list of toppings 3) list of drinks, include size   4) list of sides include size  5)total price '},
    )
    # The fields should be 1) pizza, price 2) list of toppings 3) list of drinks, include size include price  4) list of sides include size include price, 5)total price '},
    response = get_completion_from_messages(openai, messages, temperature=0)
    print(response)
