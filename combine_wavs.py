#!/usr/bin/env python
import sys
import argparse
import wave
import pprint

from os import listdir
from os.path import isfile, join
import glob
# iterate over directory getWavFilesInDir(dir)
# group in chunks of 64 getN(filesList)
# merge 
# write to single wav file?

def main():
    parser = argparse.ArgumentParser(description='Merge wav files')
    parser.add_argument('dirname', metavar='DIR', type=str, nargs=1,
                        help='Specify a directory containing .wav files')
    parser.add_argument('--output', metavar='OUTPUTDIR', type=str, nargs=1, default='.',
                        help='Specify an output directory')
    args = parser.parse_args()
    files = getWavFilesInDir(dirName=args.dirname[0])
    waveHandlers = [getFileAndReturnFrames(singleFile) for chunk in files for singleFile in chunk]
    merge(waveHandlers)
    
    
def getWavFilesInDir(dirName, groupBy=64):
    files = []
    chunks = []
    for fileName in glob.glob(join(dirName, '*.wav')):
        chunks.append(join(dirName, fileName))
        if len(chunks) == groupBy:
            files.append(chunks)
            chunks = []
    # todo: handle the case when there are less files in directory than groupBy argument
    if chunks:
        files.append(chunks)
    return files

def getFileAndReturnFrames(fileName, frames=1000):
    try:
        fileHandler = wave.open(fileName, 'r')
        params = fileHandler.getparams();
        fileHandler.close()
        return [fileName, params]
    except Exception, exception:
        return str(exception)
    
def merge(filesList, groupedBy = 64):
    masterParams = filesList[0][1];
    longestFilesFramesCount = 22050;
    writeHandle = getWriteHandle(masterParams, longestFilesFramesCount, groupedBy);
    #longestFilesFramesCount = getLongestSampleSize(filesList)
    
    print "Longest file:{0}".format(longestFilesFramesCount);
    for fileData in filesList:
        readHandle = wave.open(fileData[0], "r");
        framesTotal = readHandle.getnframes();
        if (framesTotal > longestFilesFramesCount):
            framesTotal = longestFilesFramesCount;
        print "writing extra: {0}".format((longestFilesFramesCount - framesTotal))
        emptyFrames = getnEmptyFrames(longestFilesFramesCount - framesTotal, masterParams[0], masterParams[1])
        writeHandle.writeframes(readHandle.readframes(framesTotal));
        writeHandle.writeframes(emptyFrames)
        readHandle.close();

    if (len(filesList) < groupedBy):
        emptyFrames = getnEmptyFrames(groupedBy - len(filesList) * longestFilesFramesCount,  masterParams[0],  masterParams[1])
        writeHandle.writeframes(emptyFrames)
    writeHandle.close();
    

def getWriteHandle(masterParams, singleSampleLength, groupedBy):
    writeHandle = wave.open('test.wav', 'w');    
    writeHandle.setnchannels(masterParams[0]);
    writeHandle.setsampwidth(masterParams[1]);
    writeHandle.setframerate(masterParams[2]);
    writeHandle.setnframes(singleSampleLength * groupedBy);
    return writeHandle

def getLongestSampleSize(filesList):
    max = 0
    for fileData in filesList:
        if (fileData[1][3] > max):
            max = fileData[1][3]
    return max


def getnEmptyFrames(emptyFramesCount, nchannels, sampleWidth):
    return '\0' * emptyFramesCount * nchannels * sampleWidth;

main()
