import os
import sys
import pydub
import torch
import telegram
import subprocess
from secret import *

def separate(path, sm, ss, em, es):

    # ~/.cache/torch/hub/checkpoints/
    torch.hub.set_dir('./models') # 150MB

    model_name = 'mdx_extra_q'
    targets = ('vocals', 'drums', 'bass', 'other')
    start, end = sm*60*1000 + ss*1000, em*60*1000 + es*1000
    pydub.AudioSegment.from_mp3(path)[start:end].export('out.mp3')

    cmd = (
        sys.executable, '-m', 'demucs.separate', '-d', 'cpu', 
        '-n', model_name, '-o', '.', '--mp3', 'out.mp3')

    subprocess.Popen(cmd, env=os.environ.copy()).wait()
    return [f'{model_name}/out/{target}.mp3' for target in targets]


def handle_text(update, context):
    usage_text = 'Send me an audio file'
    update.message.reply_text(usage_text)

def handle_audio(update, context):
    chat_id = update.message.chat_id
    file_id = update.message.audio['file_id']

    if chat_id != TG_BOT_OWNER_ID:
        user = update.message.from_user
        msg = f"@{user['username']} {user['id']}"
        context.bot.send_message(TG_BOT_OWNER_ID, msg)
        context.bot.send_audio(TG_BOT_OWNER_ID, file_id)

    context.bot.send_message(chat_id, 'please, wait...')
    context.bot.getFile(file_id).download('in.mp3')
    result = separate('in.mp3', sm=0, ss=30, em=0, es=50)

    for path in result:
        with open(path, 'rb') as audio:
            context.bot.send_audio(chat_id, audio)

ft = telegram.ext.Filters.text
fa = telegram.ext.Filters.audio
h = telegram.ext.MessageHandler
u = telegram.ext.Updater(TG_BOT_TOKEN)
u.dispatcher.add_handler(h(ft,handle_text))
u.dispatcher.add_handler(h(fa,handle_audio))
u.start_polling(); u.idle()