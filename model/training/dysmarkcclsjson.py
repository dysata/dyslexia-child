from typing import List
from transformers import Wav2Vec2Processor, Wav2Vec2ForCTC
from datasets import load_dataset
import torch
#import nltk
#import matplotlib.pyplot as plt
import numpy as np

from dataclasses import dataclass
import librosa#.display
#import torch.nn as nn
import sys
import argparse
import csv
import os
import re


import pandas as pd
#python3 dysmark.py -a hwa127/WA125517_m1.wav -o hwa127/WA125517_m1.txt -t 'в нашей деревне'


#from dysmarkccls.py import Z_GF_HF
import  w2vtransf as w2vtr
from w2vtransf import Segment2
import marks
from remap import remap_t1_to_rightmost


def main():
  print('directory transcriber')


 # parser = argparse.ArgumentParser()
 # parser.add_argument('-a', '--audio', dest='input_name', type=str, required=True,
 #                      help='The input sound dir name.')
 # parser.add_argument('-t', '--text', dest='text', type=str, required=False, default=None,
 #                       help='The text read.')
 # parser.add_argument('-o', '--output', dest='output_name', type=str, required=True,
 #                       help='The output report file name.')
 # args = parser.parse_args()

 # print(args.input_name)
 # print(args.text)
 # print(args.output_name)
  argsoutput_name='out'#args.output_name

  #src = './marks/hwa127'#args.input_name#sys.argv[1]
  if len(sys.argv) > 1:
      src = sys.argv[1]
  else:
      src = './marks/ka'
  print(src)



  print('reading file list...')
  unsortedList = []
  for root, dirs, files in os.walk(src):
     for file in files:
       path = os.path.join(root, file)
       size = os.stat(path).st_size #in bytes
       if size<5000000:
        if ".wav" in file :# exclude non-dicoms, good for messy folders
            unsortedList.append(os.path.join(root, file))


  print('%s files found.' % len(unsortedList))
  filein=f"./marks/text.csv"
  reader = csv.reader(open(filein, encoding='utf-8'), delimiter='\t',quotechar='|')
  text=[]
  for row in reader:
        text.append(row)
  print('text loaded '+str(len(text)))

# load model and tokenizer once before the loop
  processor = Wav2Vec2Processor.from_pretrained("./model0proc")
  model = Wav2Vec2ForCTC.from_pretrained("./model7m")

  for filename in unsortedList:
   print(filename)
   argsinput_name=filename
   print(argsinput_name+' is processed')
   match = re.search(r'\d+.wav', str(argsinput_name))
   if match:
        segmindex=match.group()[:-4]
        print(segmindex)
   else:
        segmindex=0

   print('segment '+str(segmindex))
   argstexttmp=text[int(segmindex)-1]
   argstext=argstexttmp[0]
   print(argstext)
   print(' text of segment is'+argstext)
   argsoutput_name=argsinput_name.replace('.wav', '.json')
   print(argsoutput_name)

   aw=argsinput_name
   audio, sr = librosa.load(aw, sr=16000)
   true_texts_in_batch=[argstext]
   sounds_in_batch=[audio]

   processed = processor(sounds_in_batch, sampling_rate=16_000,
                      return_tensors="pt", padding="longest")

   with torch.no_grad():
    outputs = model(processed.input_values, attention_mask=processed.attention_mask, output_hidden_states=True, return_dict=True)
    logits = outputs.logits
    last_hidden_state = outputs.hidden_states[-1].cpu()
   predicted_ids = torch.argmax(logits, dim=-1)
   transcription = processor.decode(predicted_ids[0])
   feat_extract_output_lengths = model._get_feat_extract_output_lengths(processed.attention_mask.sum(dim=1)).numpy()
   emission_matrices = []
   for sample_idx in range(feat_extract_output_lengths.shape[0]):
    specgram_len = feat_extract_output_lengths[sample_idx]
    new_emission_matrix = torch.log_softmax(
        logits[sample_idx, 0:specgram_len],
        dim=-1
    ).numpy()
    assert len(new_emission_matrix.shape) == 2
    assert new_emission_matrix.shape[0] == specgram_len
    emission_matrices.append(new_emission_matrix)

   def process_batch(true_texts_in_batch,processor):
    with processor.as_target_processor():
        processedtxt = processor(text=true_texts_in_batch, text_target=true_texts_in_batch)
    labels_ = processedtxt.input_ids
    labels = []
    for sample_idx in range(len(labels_)):
        new_label_list = []
        for token_idx in range(len(labels_[sample_idx])):
            if labels_[sample_idx][token_idx] < 0:
                break
            new_label_list.append(int(labels_[sample_idx][token_idx]))
        labels.append(new_label_list)
        del new_label_list
    del labels_
    trellis = w2vtr.get_trellis(emission_matrices[0], labels[0])
    path = w2vtr.backtrack(trellis, emission_matrices[0], labels[0])
    tokens=processor.tokenizer.convert_ids_to_tokens(
            labels[0],
            skip_special_tokens=False
        )
    segments = w2vtr.merge_repeats(
        path=path,
        tokenized=tokens
    )
    return segments, labels, path, tokens



   segmentst1, _,patht1,tokenst1 = process_batch(true_texts_in_batch,processor)

   true_texts_in_batch=[transcription]
   segmentsf2, labels,pathf2,tokensf2 = process_batch(true_texts_in_batch,processor)

   segmentst1 = [s for s in segmentst1 if s.label != '<unk>']
   segmentsf2 = [s for s in segmentsf2 if s.label != '<unk>']
   segmentst1 = remap_t1_to_rightmost(segmentst1, segmentsf2)

   for ids, txt in zip(labels, true_texts_in_batch):
    print(f'ids = {ids}, text = {txt}')



   points=[]
   pointst1=[]
   pointsf2=[]
   for i in range(len(segmentst1)):
    pointst1.append(segmentst1[i].start)
   for i in range(len(segmentsf2)):
    pointsf2.append(segmentsf2[i].start)

   points=list(dict.fromkeys(pointst1+pointsf2))
   points.sort()
   wt1='|'
   wf2='|'
   segments2=[]
   for i in points:

    if i in pointst1:
        wt1=segmentst1[pointst1.index(i)  ].label
    if i in pointsf2:
        wf2=segmentsf2[pointsf2.index(i) ].label
#    print(i,wt1,wf2)    
    S2=Segment2(wt1,wf2,'')
#    S2(wt1,wf2,'')
    segments2.append(
            S2
            )
#   for seg in segments2:
#    print(seg)        

   segments2=marks.markK(segments2)

   segments2=marks.mark7(segments2)

   segments2=marks.mark1(segments2)
   segments2=marks.mark2(segments2)
   segments2=marks.mark3(segments2)
   segments2=marks.mark4(segments2)
   segments2=marks.mark5(segments2)
   segments2=marks.mark6(segments2)
   segments2=marks.mark8(segments2)

   segments2=marks.mark9(segments2)
   segments2=marks.markJ(segments2)
   segments2=marks.markA(segments2)
   segments2=marks.markB(segments2)
   segments2=marks.markL(segments2)
   segments2=marks.markD(segments2)
   segments2=marks.markG(segments2)
   segments2=marks.markF(segments2)
   segments2=marks.markC(segments2)
   segments2=marks.markE(segments2)
   segments2=marks.markR(segments2, points, last_hidden_state)
   segments2=marks.mark0(segments2)


   print("-----------------------------")
   for seg in segments2:
    print(seg)        
   print("-----------------------------")

   import json
   output_data = []
   for seg in segments2:

       output_data.append([seg.labelt1, seg.labelf2, seg.mark if seg.mark else "0"])
   #    print(seg,seg.labelt1, seg.labelf2, seg.mark)
   #print("-----output-data----")
   #print(output_data)
   #argsoutput_name='out.json'
   print(argsoutput_name)
   with open(argsoutput_name, 'w', encoding="utf-8") as f:
       json.dump(output_data, f, ensure_ascii=False, indent=2)
   print("Done")
    
    
if __name__ == "__main__":
	main()















