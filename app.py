import json
from ibm_watson import AssistantV2
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator

from flask import Flask, render_template, request, jsonify
from werkzeug.contrib.cache import SimpleCache
import csv

uploads_dir = './uploads/'

info = {
    'iam_auth': 'Wx-EWLZ954sS2vz0Tb9x2YZldRNX3E-uKqa4wNTrSlIa',
    'api_version': '2020-04-01',
    'service_url': 'https://api.us-south.assistant.watson.cloud.ibm.com/instances/148f5128-447c-4fa3-a050-26e716eeca8b',
    'assistant_id': 'ebf621df-297a-4ee5-9b7e-5f82bf790a4e',
    'workspace_id': '87651692-6bd8-420c-922f-47547ffe6e7b'
}

authenticator = IAMAuthenticator(info['iam_auth'])
assistant = AssistantV2(version=info['api_version'], authenticator=authenticator)
assistant.set_service_url(info['service_url'])
assistant_id = info['assistant_id']
info['session_id'] = assistant.create_session(assistant_id=assistant_id).get_result()['session_id']

entity_items = []
with open('data/entity_items.csv') as csvfile:
    spamreader = csv.reader(csvfile, delimiter=',')
    for row in spamreader:
        entity_items.append(row)

ingr_item_dict = {}
for i, v in enumerate(entity_items):
    for ingr in v[1].split(' '):
        if ingr not in ingr_item_dict:
            ingr_item_dict[ingr] = []
        ingr_item_dict[ingr].append(v[1])


class MyCache:

    def __init__(self):
        MyCache.cache = SimpleCache()
        MyCache.cache.set("cart", {})

    @staticmethod
    def cart_list():
        return MyCache.cache.get("cart")

    @staticmethod
    def cart_add(item, count=1):
        cart = MyCache.cache.get("cart")
        if cart is None or not cart:
            cart = {item: count}
        elif item not in cart:
            cart[item] = count
        else:
            cart[item] = cart[item] + count
        MyCache.cache.set("cart", cart)
        return True

    @staticmethod
    def cart_delete(item):
        cart = MyCache.cache.get("cart")
        if cart is None or not cart or item not in cart:
            return False
        else:
            del cart[item]
            MyCache.cache.set("cart", cart)
            return True

    @staticmethod
    def cart_clear():
        MyCache.cache.set("cart", {})
        return True


MyCache()

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route('/chat', methods=['GET', 'POST'])
def chat():
    data = json.loads(request.data)
    bot_response = assistant.message(
        assistant_id=info['assistant_id'],
        session_id=info['session_id'],
        workspace_id=info['workspace_id'],
        input={
            'message_type': 'text',
            'text': data['msg'],
            'options': {
                'return_context': True
            }
        },
        context={
            'skills': {
                'hungerai-skill': {
                    'user_defined': {
                        'cart': '',
                        'ref_item': None,
                        'ref_ingredient': None
                    }
                }
            }
        }
    )

    try:
        output = bot_response.get_result()['output']
        context = bot_response.get_result()['context']
        return jsonify(handle_output(output))

    except:
        return None


def handle_output(output):
    try:

        intent = output['intents'][0]['intent']

        count = 1
        try:
            count = int([v for i, v in enumerate(output['entities']) if v['entity'] == 'sys-number'][0]['value'])
        except:
            pass

        if intent == "cart_list":

            cart_list = MyCache.cart_list()  # TODO : DATA CHANGE
            if cart_list is None or len(cart_list) == 0:
                return {"type": "generic", "value": "You have not ordered anything yet"}

            return {"type": "generic", "value": "You have ordered {}".format(natural_list(cart_list))}

        if intent == 'cart_add':

            candidates = [v for i, v in enumerate(output['entities']) if v['entity'] == 'Item']
            if candidates is not None and candidates[0] is not None:
                item = candidates[0]['value']
                if MyCache.cart_add(item, count):
                    return {"type": "generic", "value": "{} has been added to your cart!".format(item)}

            return {
                "type": "generic",
                "value": "Apologies, I do not understand what item you're referring to. Could you please repeat?"
            }

        if intent == 'cart_delete':

            candidates = [v for i, v in enumerate(output['entities']) if v['entity'] == 'Item']
            if candidates is not None and candidates[0] is not None:
                item = candidates[0]['value']
                if MyCache.cart_delete(item):
                    return {"type": "generic", "value": "I've removed {} from your cart!".format(item)}
                return {"type": "generic", "value": "But haven't ordered a {}".format(item)}

            return {
                "type": "generic",
                "value": "Apologies, I do not understand what item you're referring to. Could you please repeat?"
            }

        if intent == 'item_list':

            candidates = [v for i, v in enumerate(output['entities']) if v['entity'] == 'Ingredient']
            if candidates is not None and candidates[0] is not None:
                ingredient = candidates[0]['value']
                if ingredient in ingr_item_dict:
                    items = ", ".join(ingr_item_dict[ingredient])  # TODO : Better enlist
                    return {
                        "type": "generic",
                        "value": "Within {}, we have {}. What would you like?".format(ingredient, items)
                    }
                return {"type": "generic", "value": "I'm sorry, but we have nothing within {}".format(ingredient)}

            return {
                "type": "generic",
                "value": "Apologies, I do not understand what item you're referring to. Could you please repeat?"
            }

        if intent == 'cart_clear':

            if MyCache.cart_clear():
                return {
                    "type": "generic",
                    "value": "A fresh start. Is there anything else you need?"
                }

            return {
                "type": "generic",
                "value": "Apologies, I do not understand. Could you please repeat?"
            }

        return {"type": "generic", "value": output['generic'][0]['text']}

    except:

        return {"type": "generic", "value": output['generic'][0]['text']}


def natural_list(items):
    content = ''
    for item, count in items.items():
        content += ' {} {}{},'.format(count, item, 's' if count > 1 else '')
    return content[:-1]


if __name__ == "__main__":
    app.run(debug=True)
