from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson import TextToSpeechV1

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


def text_to_speech(msg, num):
    with open('./static/resources/recorded/{}.wav'.format(num), 'wb') as audio_file:
        audio_file.write(
            text_to_speech_service.synthesize(
                msg, voice='en-US_KevinV3Voice', accept='audio/wav'
            ).get_result().content
        )
        audio_file.close()


if __name__ == '__main__':
    full_text = 'John Doe. What pizzas do you have?. Add two cheese pizzas, one fish taco, and a veggie salad. What have i ordered?. Do you serve pork tacos? Make it three. I dont want the cheese pizzas. What\'s in my cart?. What veggies do you serve?. Add a veggie pizza and two veggie tacos please. That\'s all. That\'s correct.'
    # text_to_speech('John Doe', 0)
    # text_to_speech('What pizzas do you have?', 1)
    # text_to_speech('add two cheese pizzas, one fish taco, and a veggie salad', 2)
    # text_to_speech('what have i ordered?', 3)
    # text_to_speech('do you serve pork tacos?', 4)
    # text_to_speech('make it three', 5)
    # text_to_speech('i dont want the cheese pizzas', 6)
    # text_to_speech('what\'s in my cart?', 7)
    # text_to_speech('what veggies do you serve?', 8)
    # text_to_speech('add a veggie pizza and two veggie tacos please?', 9)
    # text_to_speech('that\'s all', 10)
    # text_to_speech('that\'s correct', 11)
    text_to_speech(full_text, 666)
