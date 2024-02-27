import os, sys, shutil, argparse
import pydub, subprocess, asyncio

from telegram import Update
from telegram import InputMediaAudio
from telegram.ext import MessageHandler
from telegram.ext import filters, Application

parser = argparse.ArgumentParser()
parser.add_argument('id', type=int, help='bot owner id')
parser.add_argument('token', type=str, help='bot token')
args = parser.parse_args()


async def handle_text(update, context):
    usage = 'Please, send me mp3 audio file'
    await update.message.reply_text(usage)


def separate(path):

    pydub.AudioSegment.from_mp3(path)[30000:50000].export(path)

    cmd = (sys.executable, 
           '-m', 'demucs.separate', '-d', 'cpu', 
           '-n', 'mdx_extra_q', '-o', '.', '--mp3', path)

    subprocess.Popen(cmd, env=os.environ.copy()).wait()

    targets = ('vocals', 'drums', 'bass', 'other')
    filename = os.path.basename(path).split('.')[0]
    return [f'./mdx_extra_q/{filename}/{t}.mp3' for t in targets]


async def handle_audio(update, context):

    audio = update.message.audio
    path = audio['file_id'] + '.mp3'
    user = update.message.from_user
    chat_id = update.message.chat_id

    file = await context.bot.get_file(audio)
    await file.download_to_drive(path)

    loop = asyncio.get_running_loop()
    await update.message.reply_text('please, wait ..')
    paths = await loop.run_in_executor(None, separate, path)
    media_group = [InputMediaAudio(open(p, 'rb')) for p in paths]
    await update.message.reply_media_group(media_group)

    if user['id'] != args.id:
        msg = f"@{user['username']} {user['id']}"
        await context.bot.send_message(args.id, msg)
        await context.bot.send_audio(args.id, audio['file_id'])

    for p in [path] + paths: os.remove(p)
    shutil.rmtree(os.path.dirname(paths[0]))


app = Application.builder().token(args.token).build()
app.add_handler(MessageHandler(filters.TEXT, handle_text))
app.add_handler(MessageHandler(filters.AUDIO, handle_audio))
app.run_polling(allowed_updates=Update.ALL_TYPES)