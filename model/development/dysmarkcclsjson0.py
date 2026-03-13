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
import model as alignment
from w2vtransf import Segment2
import marks


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
      src = './marks/dmi7'
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
  processor, model = alignment.load_model("./model0proc", "./model7m")

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

   segments2, points, _ = alignment.process_audio(argstext, argsinput_name, processor, model)

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
