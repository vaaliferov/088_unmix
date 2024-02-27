#### Music Source Separation

This tool allows you to extract the "sources" (bass, drums, vocals and other) from a given piece of music. The model is based on the [demucs](https://github.com/facebookresearch/demucs) architecture (mdx_extra_q pretrained on [musdb18](https://sigsep.github.io/datasets/musdb.html)). [[demo](https://t.me/vaaliferov_unmix_bot)]

```bash
python3 -m venv env
apt install -y ffmpeg
source env/bin/activate
pip install -r requirements.txt
python3 bot.py <bot_owner_id> <bot_token>
```

![Alt Text](pics/tg.png)