import json, os, csv, glob

from flask import Flask, render_template, request, jsonify
from werkzeug.contrib.cache import SimpleCache

from ibm_watson import AssistantV2
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator

from ibm_watson import TextToSpeechV1
from ibm_watson import SpeechToTextV1

uploads_dir = './uploads/'
resources_dir = './static/resources/'
text_to_speech_file = 'text_to_speech'
speech_to_text_file = 'speech_to_text'

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

text_to_speech_credentials = {
    "apikey": "BLKaQ3nnYTTKruLeb9dL8gtbtxjI856Zx9WFKy0spZET",
    "iam_apikey_description": "Auto-generated for key ed5fac4a-bc22-4d9f-9859-2b248804035e",
    "iam_apikey_name": "wdp-writer",
    "iam_role_crn": "crn:v1:bluemix:public:iam::::serviceRole:Writer",
    "iam_serviceid_crn": "crn:v1:bluemix:public:iam-identity::a/eed7635af9de4ec1a02ed80b7edae9dc::serviceid:ServiceId-d7acec2a-7f78-4eac-ba33-8407e8edca8b",
    "url": "https://api.us-east.text-to-speech.watson.cloud.ibm.com/instances/30ac0c7e-f8e4-48e9-9222-59dbb1f4fc82",
}

text_to_speech_authenticator = IAMAuthenticator(text_to_speech_credentials['apikey'])
text_to_speech_service = TextToSpeechV1(authenticator=text_to_speech_authenticator)
text_to_speech_service.set_service_url(text_to_speech_credentials['url'])


def text_to_speech(msg, filename):
    dialog_counter = MyCache.get_update_dialog_counter()
    os.rename('{}{}_{}.wav'.format(resources_dir, filename, dialog_counter),
              '{}{}_{}.wav'.format(resources_dir, filename, dialog_counter + 1))
    with open('{}{}_{}.wav'.format(resources_dir, filename, dialog_counter + 1), 'wb') as audio_file:
        audio_file.write(
            text_to_speech_service.synthesize(msg, voice='en-US_LisaV3Voice', accept='audio/wav').get_result().content
        )
        audio_file.close()
    return dialog_counter


speech_to_text_credentials = {
    "apikey": "UF2I5P9NXt1HXnmye2fkDeP2kxp_tb9VVSWF3i5qjuZ3",
    "iam_apikey_description": "Auto-generated for key 16171d30-82c7-4b51-8f0e-fe656da5cdcd",
    "iam_apikey_name": "wdp-writer",
    "iam_role_crn": "crn:v1:bluemix:public:iam::::serviceRole:Writer",
    "iam_serviceid_crn": "crn:v1:bluemix:public:iam-identity::a/eed7635af9de4ec1a02ed80b7edae9dc::serviceid:ServiceId-445f4b12-5e0d-45d4-a284-7f2a7138cf52",
    "url": "https://api.us-east.speech-to-text.watson.cloud.ibm.com/instances/687866d5-4515-46ca-8789-9191fb6e41e3",
}

speech_to_text_authenticator = IAMAuthenticator(speech_to_text_credentials['apikey'])
speech_to_text_service = SpeechToTextV1(authenticator=speech_to_text_authenticator)
speech_to_text_service.set_service_url(speech_to_text_credentials['url'])


def speech_to_text(file_name):
    with open(file_name, "rb") as audio_file:
        result = speech_to_text_service.recognize(
            audio_file, content_type="audio/wav",
            continuous=True, timestamps=False,
            max_alternatives=1
        )
    try:
        return result.result['results'][0]['alternatives'][0]['transcript']
    except:
        return None


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
        MyCache.cache.set("context_item", None)
        MyCache.cache.set("context_intent", None)
        MyCache.cache.set("dialog_counter", 0)

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

    @staticmethod
    def get_context_item():
        return MyCache.cache.get("context_item")

    @staticmethod
    def set_context_item(item):
        return MyCache.cache.set("context_item", item)

    @staticmethod
    def get_context_intent():
        return MyCache.cache.get("context_intent")

    @staticmethod
    def set_context_intent(intent):
        return MyCache.cache.set("context_intent", intent)

    @staticmethod
    def get_update_dialog_counter():
        dialog_counter = MyCache.cache.get("dialog_counter")
        MyCache.cache.set("dialog_counter", dialog_counter + 1)
        return dialog_counter

    @staticmethod
    def get_dialog_counter():
        return MyCache.cache.get("dialog_counter")


MyCache()

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route('/refresh', methods=['GET', 'POST'])
def refresh():
    info['session_id'] = assistant.create_session(assistant_id=assistant_id).get_result()['session_id']
    existing_wav = glob.glob('{}{}_*.wav'.format(resources_dir, text_to_speech_file))[0].replace('\\', '/')
    os.replace(existing_wav, '{}{}_0.wav'.format(resources_dir, text_to_speech_file))
    MyCache.cache.set("cart", {})
    MyCache.cache.set("context_item", None)
    MyCache.cache.set("context_intent", None)
    MyCache.cache.set("dialog_counter", 0)

    for filename in glob.glob('{}{}_*.wav'.format(resources_dir, speech_to_text_file)):
        os.remove(filename.replace('\\', '/'))

    return {}


@app.route('/audioUpload', methods=['GET', 'POST'])
def audioUpload():
    dialog_counter = MyCache.get_dialog_counter()
    # file_name = './static/resources/speech_to_text_{}.wav'.format(dialog_counter)
    # request.files['audio-file'].save('./static/resources/speech_to_text_{}.wav'.format(dialog_counter))

    file_name = './static/resources/recorded/{}.wav'.format(dialog_counter)
    msg = speech_to_text(file_name)
    return jsonify({"msg": msg})


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
        handled = handle_output(output, context)

        if handled is not None and 'value' in handled:
            msg = handled['value']
            dialog_counter = text_to_speech(msg, 'text_to_speech')
            handled['dialog_counter'] = dialog_counter

        return jsonify(handled)

    except:
        return None


# prevent cached responses
@app.after_request
def add_header(r):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    r.headers['Cache-Control'] = 'public, max-age=0'
    return r


def handle_output(output, context):
    # try:

    intent = output['intents'][0]['intent'] if len(output['intents']) > 0 else None
    context_intent = MyCache.get_context_intent()

    if context_intent is not None or intent is None:
        intent = context_intent

    if intent == "cart_list":

        cart_list = MyCache.cart_list()
        if cart_list is None or len(cart_list) == 0:
            return {"type": "generic", "value": "You have not ordered anything yet"}

        return {"type": "generic", "value": "You have ordered {}".format(natural_list(cart_list))}

    if intent == 'cart_add':

        order = decipher_order(output)
        context_item = MyCache.get_context_item()

        if context_item is not None and len(order) == 0:

            denied = any([v['entity'] == 'Boolean' and v['value'] == 'no' for i, v in enumerate(output['entities'])])
            if denied:
                MyCache.set_context_intent(None)
                MyCache.set_context_item(None)

                return {
                    "type": "generic",
                    "value": "As you wish. What else would you like?"
                }

            count = 1
            for i, v in enumerate(output['entities']):
                if v['entity'] == 'sys-number':
                    count = int(v['value'])

            if MyCache.cart_add(context_item, count):
                MyCache.set_context_intent(None)
                MyCache.set_context_item(None)
                return {
                    "type": "generic",
                    "value": "Alright... I've added {} to your cart!".format(natural_list({context_item: count}))
                }

            MyCache.set_context_intent(None)
            MyCache.set_context_item(None)
            return {
                "type": "generic",
                "value": "Apologies, I do not understand what item you're referring to. Could you please repeat?"
            }

        if all(MyCache.cart_add(item, count) for item, count in order.items()):
            return {"type": "generic", "value": "Alright... I've added {} to your cart!".format(natural_list(order))}

        return {
            "type": "generic",
            "value": "Apologies, I do not understand what item you're referring to. Could you please repeat?"
        }

    if intent == 'cart_delete':

        order = decipher_order(output)
        if len(order) == 0:
            return {"type": "generic", "value": "But haven't ordered {}".format(natural_list(order, countless=True))}

        if all(MyCache.cart_delete(item) for item, count in order.items()):
            return {
                "type": "generic",
                "value": "I've removed {} from your cart!".format(natural_list(order, countless=True))
            }

        return {
            "type": "generic",
            "value": "Apologies, I do not understand what item you're referring to. Could you please repeat?"
        }

    if intent == 'item_list':

        candidate_items = [v for i, v in enumerate(output['entities']) if v['entity'] == 'Item']
        if candidate_items is not None and len(candidate_items) > 0 and candidate_items[0] is not None:
            item = candidate_items[0]['value']
            if item in [i[1] for i in entity_items]:
                MyCache.set_context_item(item)
                MyCache.set_context_intent("cart_add")
                return {
                    "type": "generic",
                    "value": "Yes, we do have {}. Should I add that?".format(item)
                }

            # return {
            #     "type": "generic",
            #     "value": "I'm sorry, but we do not have {}".format(item)
            # }

        candidates = [v for i, v in enumerate(output['entities']) if v['entity'] == 'Ingredient']
        if candidates is not None and len(candidates) > 0 and candidates[0] is not None:
            ingredient = candidates[0]['value']
            if ingredient in ingr_item_dict:
                items = natural_list(ingr_item_dict[ingredient], countless=True, already_list=True, shorten=True)
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

    if intent == 'checkout':

        cart = MyCache.cart_list()
        if cart is None or len(cart) == 0 or all([count == 0 for item, count in cart.items()]):
            return {
                "type": "generic",
                "value": "Your cart is empty, please order something"
            }

        MyCache.set_context_intent('checkout_confirmation')
        return {
            "type": "generic",
            "value": "You have ordered {}. Please confirm".format(natural_list(cart))
        }

    if intent == 'checkout_confirmation':

        MyCache.set_context_intent(None)
        MyCache.set_context_item(None)

        if any([v['entity'] == 'Boolean' and v['value'] == 'yes' for i, v in enumerate(output['entities'])]):
            name = None
            try:
                name = context['skills']['main skill']['user_defined']['name']
            except:
                pass
            return {
                "type": "end",
                "value": "I am placing your order{}. Thank you for using HungerAI, and we'd be glad to have you back!".format(
                    '!' if name is None else (' ' + name))
            }

        return {
            "type": "generic",
            "value": "Alright then. Please let me know what you want to change in your order"
        }

    return {"type": "generic", "value": output['generic'][0]['text']}

    # except:

    # return {"type": "generic", "value": output['generic'][0]['text']}


def decipher_order(output):
    result = {}
    temp_num = 1
    for i, v in enumerate(output['entities']):
        if v['entity'] == 'sys-number':
            temp_num = int(v['value'])
        elif v['entity'] == 'Item':
            result[v['value']] = temp_num
            temp_num = 1
    return result


def natural_list(items, countless=False, already_list=False, shorten=False):
    content = ''
    distinct_count = len(items)
    distinct_counter = 0

    if already_list:
        items = {item: 1 for item in items}

    for item, count in items.items():

        if shorten and distinct_counter == 4:
            content += ' and {} more items.'.format(distinct_count - distinct_counter)
            break

        distinct_counter += 1
        if 1 < distinct_count == distinct_counter:
            content += ' and'

        if countless:
            content += ' {},'.format(item)
        elif count == 1:
            content += ' {} {},'.format('an' if item[0] in ['a', 'e', 'i', 'o', 'u'] else 'a', item)
        else:
            content += ' {} {}{},'.format(count, item, 's')

    return content[:-1]


if __name__ == "__main__":
    app.run(debug=True)
