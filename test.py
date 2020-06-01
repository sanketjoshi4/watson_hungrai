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
                msg, voice='en-US_MichaelVoice', accept='audio/wav'
            ).get_result().content
        )
        audio_file.close()


if __name__ == '__main__':
    text_to_speech('John Doe', 0)
    text_to_speech('Do you serve chicken?', 1)
    text_to_speech('I want one chicken sandwich and two pork tacos please', 2)
