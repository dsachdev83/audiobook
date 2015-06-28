#
# Copyright 2014 IBM Corp. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# -*- coding: utf-8 -*-

import os
import requests
import json
from flask import Flask, render_template, request, Response, stream_with_context
import slate
import sys
from urllib2 import Request, urlopen
from pyPdf import PdfFileWriter, PdfFileReader
from StringIO import StringIO

app = Flask(__name__)

class TextToSpeechService:
    """Wrapper on the Text to Speech service"""

    def __init__(self):
        """
        Construct an instance. Fetches service parameters from VCAP_SERVICES
        runtime variable for Bluemix, or it defaults to local URLs.
        """
        vcapServices = os.getenv("VCAP_SERVICES")
        # Local variables
        self.url = "https://stream.watsonplatform.net/text-to-speech-beta/api"
        self.username = "255b39c3-1619-4bb6-9de2-a88ebfbba23f"
        self.password = "v3NNLDOinOTv"

        if vcapServices is not None:
            print("Parsing VCAP_SERVICES")
            services = json.loads(vcapServices)
            svcName = "text_to_speech"
            if svcName in services:
                print("Text to Speech service found!")
                svc = services[svcName][0]["credentials"]
                self.url = svc["url"]
                self.username = svc["username"]
                self.password = svc["password"]
            else:
                print("ERROR: The Text to Speech service was not found")

    def synthesize(self, text, voice, accept):
        return requests.get(self.url + "/v1/synthesize",
            auth=(self.username, self.password),
            params={'text': text, 'voice': voice, 'accept': accept},
            stream=True, verify=False
        )

    def post_synthesize(self, body, voice, accept):
        return requests.post(self.url + "/v1/synthesize",
            auth=(self.username, self.password),
            params={'body': body, 'voice': voice, 'accept': accept},
            stream=True, verify=False
        )

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

#curl -H "Content-type: application/json" -X GET -G http://localhost:3000/synthesize -d text=hello,there -d voice=VoiceEnUsMichael
# @app.route('/synthesize', methods=['GET'])
# def synthesize():
#     print request.args
#     voice = request.args.get('voice', 'VoiceEnUsMichael')
#     accept = request.args.get('accept', 'audio/ogg; codecs=opus')
#     text = request.args.get('text', '')
#     download = request.args.get('download', '')
#     headers = {}
#     if download:
#         headers['content-disposition'] = 'attachment; filename=transcript.ogg'
#     try:
#         req = textToSpeech.synthesize(text, voice, accept)
#         return Response(stream_with_context(req.iter_content()),
#             headers=headers, content_type = req.headers['content-type'])
#     except Exception,e:
#         print format(e)
#         sys.exit(500)


def get_text(book_url):
    body = ''
    r = requests.get(book_url)
    with open("test.pdf", "wb") as pdf:
        pdf.write(r.content)
    f = open('test.pdf', 'rb')
    doc = slate.PDF(f)
    for item in doc:
            print item
            item = str(item)
            if item is not None:
                body += item
    os.remove("test.pdf")
    return body


@app.route('/synthesize', methods=['POST'])
def post_synthesize():
    print "inside POST synthesize"
    print request.json
    voice = request.json['voice'].encode('utf-8')
    # voice = request.args.get('voice', 'VoiceEnUsMichael')
    accept = 'audio/ogg; codecs=opus'
    book_url = request.json['url'].encode('utf-8')
    # download = request.args.get('download', '')
    download = ''
    print book_url
    body = get_text(book_url)

    print body
    print (str(sys.getsizeof(body)/1000000.0)+'mb')
    #body = request.args.get('body', '')
    #download = True
    headers = {}
    if download:
        headers['content-disposition'] = 'attachment; filename=transcript.ogg'
    try:
        req = textToSpeech.post_synthesize(body, voice, accept)
        return Response(stream_with_context(req.iter_content()),
            headers=headers, content_type = req.headers['content-type'])
    except Exception,e:
        print format(e)
        sys.exit(500)

@app.errorhandler(500)
def internal_Server_error(error):
    return 'Error processing the request', 500

# Global watson service wrapper
textToSpeech = None

if __name__ == "__main__":
    textToSpeech = TextToSpeechService()

    # Get host/port from the Bluemix environment, or default to local
    HOST_NAME = os.getenv("VCAP_APP_HOST", "127.0.0.1")
    PORT_NUMBER = int(os.getenv("VCAP_APP_PORT", "3000"))

    app.run(host=HOST_NAME, port=int(PORT_NUMBER), debug=True)

    # Start the server
    print("Listening on %s:%d" % (HOST_NAME, PORT_NUMBER))
