# -*- coding: utf-8 -*-
import uuid
#import matplotlib.pyplot as plt
from aiohttp import web
#import numpy as np
#import librosa.display
import re
import glob

from aiortc import RTCPeerConnection, RTCSessionDescription
#from pydub import AudioSegment
#from huggingsound import SpeechRecognitionModel
#import soundfile
#from sklearn.ensemble import RandomForestClassifier
from aiortc.contrib.media import MediaBlackhole, MediaRecorder, MediaRelay
import os
import json

import app.settings as settings

from datetime import datetime

import json
import asyncio
relay = MediaRelay()


async def handle_new_phrase(request):
    content = open(os.path.join(settings.ROOT, "text.txt"), "r").read()
    return web.Response(content_type="text/html", text=content)


async def index(request):
    content = open(os.path.join(settings.ROOT, "templates/game/index.html"), "r", encoding="utf-8").read()
    return web.Response(content_type="text/html", text=content)

async def game1(request):
    content = open(os.path.join(settings.ROOT, "templates/game/game1.html"), "r", encoding="utf-8").read()
    return web.Response(content_type="text/html", text=content)

async def game1d(request):
    content = open(os.path.join(settings.ROOT, "templates/game/game1d.html"), "r", encoding="utf-8").read()
    return web.Response(content_type="text/html", text=content)


async def game2(request):
    content = open(os.path.join(settings.ROOT, "templates/game/game2.html"), "r", encoding="utf-8").read()
    return web.Response(content_type="text/html", text=content)

async def game2d(request):
    content = open(os.path.join(settings.ROOT, "templates/game/game2d.html"), "r", encoding="utf-8").read()
    return web.Response(content_type="text/html", text=content)


async def game3(request):
    content = open(os.path.join(settings.ROOT, "templates/game/game3.html"), "r", encoding="utf-8").read()
    return web.Response(content_type="text/html", text=content)

async def game3f(request):
    content = open(os.path.join(settings.ROOT, "templates/game/game3f.html"), "r", encoding="utf-8").read()
    return web.Response(content_type="text/html", text=content)

async def rrrex(request):
    content = open(os.path.join(settings.ROOT, "static/rrrex/index.html"), "r", encoding="utf-8").read()
    return web.Response(content_type="text/html", text=content)

async def process_audio(audio_path, channel):
    print("process_audio: sending message")
    channel.send(json.dumps({"grading": False}, ensure_ascii=False, indent=4))
#async def process_audio_klus(audio_path, channel):
#    audio_paths = [audio_path]
#    transcriptions = model.transcribe(audio_paths)
#    words = transcriptions[0]['transcription']
#    start_times = transcriptions[0]['start_timestamps']
#    end_times = transcriptions[0]['end_timestamps']
#    print(words)
#
#    a = [m.start() for m in re.finditer('р', words)]
#    j = 1
#    for i in a:
#        start = start_times[i] - 20
#        end = end_times[i] + 20
#        audio = AudioSegment.from_file(audio_path, format='wav')
#        cut = audio[start:end]
#        cut.export('test' + str(j) + '.wav', format='wav')
#
#        filename = 'test' + str(j) + '.wav'
#        out = 'pred' + str(j) + '.wav'
#        y, sr = librosa.load(filename, mono=True)
#        y_8000 = librosa.resample(y, orig_sr=sr, target_sr=8000)
#        soundfile.write(out, y_8000, 8000)
#        j = j + 1
#
#    x = []
#
#    folder_path = os.path.join(settings.ROOT, "app/game/resources/audios/")
#    a_wavs = glob.glob(folder_path + "a*.wav")
#    b_wavs = glob.glob(folder_path + "b*.wav")
#    c_wavs = glob.glob(folder_path + "c*.wav")
#    d_wavs = glob.glob(folder_path + "d*.wav")
#
#    for wav in a_wavs:
#        audio, sr = librosa.load(wav, sr=8000)
#        features = librosa.feature.mfcc(y=audio, sr=sr, n_fft=256)
#        features_scaled = np.mean(features.T, axis=0)
#        x.append(features_scaled)
#
#    for wav in b_wavs:
#        audio, sr = librosa.load(wav, sr=8000)
#        features = librosa.feature.mfcc(y=audio, sr=sr, n_fft=256)
#        features_scaled = np.mean(features.T, axis=0)
#        x.append(features_scaled)
#
#    for wav in c_wavs:
#        audio, sr = librosa.load(wav, sr=8000)
#        features = librosa.feature.mfcc(y=audio, sr=sr, n_fft=256)
#        features_scaled = np.mean(features.T, axis=0)
#        x.append(features_scaled)
#
#    for wav in d_wavs:
#        audio, sr = librosa.load(wav, sr=8000)
#        features = librosa.feature.mfcc(y=audio, sr=sr, n_fft=256)
#        features_scaled = np.mean(features.T, axis=0)
#        x.append(features_scaled)
#
#    y = np.concatenate([np.zeros(32), np.ones(20), np.full((44,), 2), np.full((34,), 3)])
#
#    rf = RandomForestClassifier(n_estimators=1000, max_depth=None, random_state=23)
#    rf.fit(x, y)
#
#    x_test = []
#    pred_wavs = glob.glob("pred*.wav")
#    test_wavs = glob.glob("test*.wav")
#    k = 0
##    #os.remove(os.path.join(settings.ROOT, "text.txt"))
#    result_string = ''
#    for wav in pred_wavs:
#        audio, sr = librosa.load(wav, sr=8000)
#        features = librosa.feature.mfcc(y=audio, sr=sr, n_fft=256)
#        features_scaled = np.mean(features.T, axis=0)
###        librosa.display.waveshow(audio, sr=sr)
###        plt.show()
#        x_test.append(features_scaled)
##        y_pred = rf.predict(x_test)
#
##        # with open(os.path.join(ROOT, "text.txt"), "a", ) as f:
##        #     if y_pred[k] == 0:
##        #         print("существенная артикуляция")
##        #         f.write("существенная артикуляция" + '\n')
##        #     elif y_pred[k] == 1:
##        #         print("нормальное произношение")
##        #         f.write("нормальное произношение" + '\n')
##        #     elif y_pred[k] == 2:
##        #         print("плохое выговаривание")
##        #         f.write("плохое выговаривание" + '\n')
##        #     elif y_pred[k] == 3:
##        #         print("отсутствие звука")
##        #         f.write("отсутствие звука" + '\n')
#        if y_pred[k] == 0:
#            result_string += "существенная артикуляция<br>"
#        elif y_pred[k] == 1:
#            result_string += "нормальное произношение<br>"
#        elif y_pred[k] == 2:
#            result_string += "плохое выговаривание<br>"
#        elif y_pred[k] == 3:
#            result_string += "отсутствие звука<br>"
#
#        print(y_pred[k])
#        k = k + 1
##    # for wav in test_wavs:
##    #     os.remove(wav)
#    for wav in pred_wavs:
#        os.remove(wav)
#
#    result_string = f"Распознанные слова:<br>{words}" + "<br>Оценка:<br>" + result_string
#    channel.send(json.dumps({"grading": True, "words": words, "result_string": result_string}, ensure_ascii=False, indent=4))
#
#
async def offer(request):
    meta = {}
    audio_track = {}
    recorder = {}
    sink = {}
    filename_json = ""
    game = ""
    wav_file_path = ""
    params = await request.json()
    offer = RTCSessionDescription(sdp=params["sdp"], type=params["type"])

    pc = RTCPeerConnection()
    pc_id = "PeerConnection(%s)" % uuid.uuid4()
    settings.pcs.add(pc)

    def log_info(msg, *args):
        settings.logger.info(pc_id + " " + msg, *args)

    log_info("Created for %s", request.remote)

    # if settings.args.record_to:
    #     recorder = MediaRecorder(settings.args.record_to)
    # else:
    #     recorder = MediaBlackhole()

    # pc is an RTCPeerConnection
    @pc.on("datachannel")
    def on_datachannel(channel):
        @channel.on("message")
        async def on_message(message):
            #print(message)
            nonlocal game
            nonlocal recorder
            nonlocal sink
            nonlocal meta
            nonlocal filename_json
            message_object = json.loads(message)
            nonlocal wav_file_path
            if message_object['action'] == 'start_recording':
                gotmeta = message_object['meta']
                itemType = "_image_" if gotmeta['isImage'] else "_word_"
                if 'wordIndex' in gotmeta:
                    worddata = str(gotmeta["wordIndex"]).zfill(4)
                elif "taskID" in gotmeta and "step" in gotmeta:
                    worddata = str(gotmeta['taskID']).zfill(2) + '_' + str(gotmeta['step']).zfill(2) + '_'
                else:
                    worddata = "unexpected"
                filename = worddata + itemType + gotmeta["datetime"]
                filename_wav = filename + ".wav"
                filename_json = filename + ".json"

                game = gotmeta["game"];
                print(game)
                meta = {
                    'filename': filename_wav,
                    'meta': gotmeta
                }
                wav_file_path = "storage/" + game + "/" + filename_wav

                await recorder.stop()
                recorder = MediaRecorder(wav_file_path)
                recorder.addTrack(audio_track)
                await recorder.start()

            elif message_object['action'] == 'stop_recording' and game and isinstance(game, str) and game.strip() != "":
                meta['post'] = message_object['postmeta']
                await recorder.stop()
                recorder = MediaRecorder("storage/tmp/tmp.wav")
                recorder.addTrack(audio_track)
                await recorder.start()
                with open("storage/" + game + "/" + filename_json, 'w', encoding='utf-8') as f:
                    json.dump(meta, f, ensure_ascii=False, indent=4)
                if meta["meta"]["game"] == "game3":
                    await process_audio(wav_file_path, channel)
                if meta["meta"]["game"] == "game3f":
                    await process_audio(wav_file_path, channel)
            else:
                print("Strange action in the message: " + message_object['action'])

    @pc.on("connectionstatechange")
    async def on_connectionstatechange():
        log_info("Connection state is %s", pc.connectionState)
        if pc.connectionState == "failed":
            meta['control'] = {"connection": "failed", "description": "connection failed when we were receiving this object"}
            with open("storage/" + game + "/" + filename_json, 'w', encoding='utf-8') as f:
                json.dump(meta, f, ensure_ascii=False, indent=4)
            await pc.close()
            settings.pcs.discard(pc)

    @pc.on("track")
    async def on_track(track):
        nonlocal audio_track
        nonlocal recorder
        log_info("Track %s received", track.kind)

        if track.kind == "audio":
            audio_track = track
            recorder = MediaRecorder("storage/tmp/tmp.wav")
            recorder.addTrack(audio_track)
            await recorder.start()

        @track.on("ended")
        async def on_ended():
            log_info("Track %s ended", track.kind)

    # handle offer
    await pc.setRemoteDescription(offer)

    # send answer
    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)

    return web.Response(
        content_type="application/json",
        text=json.dumps(
            {"sdp": pc.localDescription.sdp, "type": pc.localDescription.type}
        ),
    )
