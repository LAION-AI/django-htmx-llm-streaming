## streaming/views.py
# https://github.com/bigskysoftware/htmx/issues/2149

import os
import time
import uuid
import json
import queue
import requests
from django.http import HttpResponse, StreamingHttpResponse, JsonResponse
from django.shortcuts import render
from .forms import ChatForm
from .models import Message
from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv('API_URL')
API_MODEL = os.getenv('API_MODEL')
API_KEY = os.getenv('API_KEY')

message_queue = queue.Queue()
messages = {}

def index_view(request):
    return render(request, 'streaming/index.html')

def chat_view(request):
    if request.method == 'POST':
        form = ChatForm(request.POST)
        if form.is_valid():
            prompt = form.cleaned_data['message']
            message_id = str(uuid.uuid4())
            messages[message_id] = prompt
            message_queue.put((message_id, prompt))
            return HttpResponse(f'<div sse-swap="{message_id}" hx-swap="beforeend"></div>')
    else:
        form = ChatForm()
    return render(request, 'streaming/chat_htmx.html', {'form': form})

def generate_htmx():
    while True:
        try:
            message_id, prompt = message_queue.get(block=False)
        except queue.Empty:
            yield "event: keepalive\ndata: \n\n"
            time.sleep(1)
            continue

        api_url = 'http://pop-os:11434/api/generate'
        payload = {
            "model": "llama3:8b-instruct-fp16",
            "prompt": prompt,
            "stream": True
        }
        headers = {'Content-Type': 'application/json'}
        try:
            response = requests.post(api_url, data=json.dumps(payload), headers=headers, stream=True)
            for line in response.iter_lines():
                if line:
                    data = json.loads(line)
                    if 'response' in data:
                        # print(data['response'])
                        yield f"event: ResponseEvent\ndata: <span style='white-space: pre;'>" + data['response'].replace('\n', '<br />') + "</span>\n\n"
        except requests.exceptions.RequestException as e:
            print(f"Error from API: {e}")
            yield f"event: error\ndata: An error occurred while processing your request. Please try again later.\n\n"

        message_queue.task_done()

def sse_endpoint(request):
    res = StreamingHttpResponse(generate_htmx(), content_type='text/event-stream')
    res['Cache-Control'] = 'no-cache'
    res['X-Accel-Buffering'] = 'no'
    return res


#### JAVASCRIPT ####
def stream_javascript_response(request, user_message):
    api_url = API_URL
    payload = {
        "model": API_MODEL,
        # "prompt": user_message,
        "messages": [
            {"role": "system", "content": "You are a helpful, friendly AI assistant."},
            {"role": "user", "content": user_message}
        ],
        "stream": True
    }
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {API_KEY}',
    }
    # response = requests.post(api_url, data=json.dumps(payload), headers=headers) ### for local server
    response = requests.post(api_url, json=payload, headers=headers) ### for hyprlab

    def generate_javascript():
        bot_response = ""
        for line in response.iter_lines():
            if line and line != b'data: [DONE]':
                ####### For debugging #######
                # print(line)
                
                ####### for hyprlab endpoint: https://docs.hyprlab.io/endpoints/version-1/chat-openai-format #######
                data = json.loads(line.decode('utf-8').strip('data: '))
                if 'choices' in data:
                    if not data['choices'][0]['finish_reason']:
                        text_response = data['choices'][0]['delta']['content']
                        bot_response += text_response
                        yield f"data: {json.dumps({'response': text_response, 'done': False})}\n\n"
                        
                ####### for ollama endpoint: https://github.com/ollama/ollama/blob/main/docs/api.md #######
                if 'response' in data:
                    bot_response += data['response']
                    yield f"data: {json.dumps({'response': data['response'], 'done': data.get('done', False)})}\n\n"
        Message.objects.create(user_message=user_message, bot_response=bot_response)
        yield "data: {\"done\": true}\n\n"  # Signal the end of the stream

    return StreamingHttpResponse(generate_javascript(), content_type='text/event-stream')

def chat_javascript_view(request):
    if request.method == 'POST':
        form = ChatForm(request.POST)
        if form.is_valid():
            user_message = form.cleaned_data['message']
            return render(request, 'streaming/chat_javascript.html', {'form': form, 'user_message': user_message})
    else:
        form = ChatForm()
    return render(request, 'streaming/chat_javascript.html', {'form': form})