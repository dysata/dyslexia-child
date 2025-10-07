[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)(https://github.com/dysata/dyslexia-child/blob/master/LICENSE)
![Python 3.12](https://img.shields.io/badge/python-3.12-green.svg)

# dyslexia-child

This project represents a python pipeline, library and service for automatic speech recognition and transcribing in Russian and marking the 20 types of dyslexia marks.

Different dyslexia markers cause of different brain disorders and require different marks in neurodata records.


## Installation

This project uses a deep learning, therefore a key dependency is a deep learning framework. I prefer [PyTorch](https://pytorch.org/), and you need to install CPU- or GPU-based build of PyTorch ver. 2.3 or later. You can see more detailed description of dependencies in the `requirements.txt`.

Other important dependencies are:

- [Transformers](https://github.com/huggingface/transformers): a Python library for building neural networks with Transformer architecture;
- [FFmpeg](https://ffmpeg.org): a software for handling video, audio, and other multimedia files.

The first dependency Python library, also it might be used FFmpeg for audio conversion as described in the instructions https://ffmpeg.org/download.html.

Also, the Python 3.12 or later is required. The best with [Python virtual environment](https://docs.python.org/3/glossary.html#term-virtual-environment) witch can be created with [Anaconda](https://www.anaconda.com). To install this project in the selected virtual environment, you should activate this environment and run the following commands in the Terminal:

```shell
git clone https://github.com/dysata/dyslexia-child.git
cd dyslexia-child
python -m pip install -r requirements.txt
```

You can choose the level of pipeline.
The first level is the direct transcribation of audio reading and compareson with the prerequested one.
The second level is pass the requred logits parts to the pretrained classifier.
The third level is collect the customly marked sounds/logits in system and api for the data agregation and labeling, and train the classifier. 

## 1st level Usage

### Command prompt

Usage of the **dyslexia-child**. You have to write the following command in your command prompt:

```shell
python3 dysmark.py \
    -a /path/to/your/sound/or/video.wav
    -t /path/to/your/text.txt
    -o /path/to/your/report.txt
```

The **1st** argument `-i` specifies the name of the source audio in wav 16kHz format.
The audio can be converted by ffmpeg as
ffmpeg -i /path/to/your/sound/or/video/to/convert -acodec pcm_s16le -ar 16000 /path/to/your/sound/or/video.wav

The **2st** argument `-t` specifies the name of the text, which is read by person.

The **3st** argument `-o` specifies the name of the report with the results with marks.

Other arguments are not required. 
The argument `-m` points to the directory with all needed pre-downloaded models. 

If you don't specify the argument `-m`, then all needed models will be automatically downloaded from Huggingface hub:

- for Russian:
  1) [dysata/Wav2Vec2-Ru-Child](https://huggingface.co/dysata/Wav2Vec2-Ru-Child),



In turn, project includes additional subdirectories:
archi - architecture for levels
api - api for the data agregation and labeling
tasks - texts, words and picktures selected
external - possible applications based




If your computer has CUDA-compatible GPU, and your PyTorch has been correctly installed for this GPU, then the **Pisets** will transcribe your speech very quickly. So, the real-time factor (xRT), defined as the ratio between the time it takes to process the input and the duration of the input, is approximately 0.15 - 0.25 (it depends on the concrete GPU type). But if you use CPU only, then the **Pisets** will calculate your speech transcription significantly slower (xRT is approximately 1.0 - 1.5).

## Contact

Pavel Rudich   - [pav3ru@yandex.ru](mailto:pav3ru@yandex.ru)

## Acknowledgment


The [Foundation for Assistance to Small Innovative Enterprises](https://fasie.ru) which is Russian governmental non-profit organization supports an unique program to build free and open-source artificial intelligence systems. This programs is known as "Code - Artificial Intelligence" (see https://fasie.ru/press/fund/kod-ai/?sphrase_id=114059 in Russian). The abovementioned project was started within the first stage of the "Code - Artificial Intelligence" program. You can see the first-stage winners list on this web-page: https://fasie.ru/competitions/kod-ai-results (in Russian).


## License

Distributed under the MIT License. See `LICENSE` for more information.
