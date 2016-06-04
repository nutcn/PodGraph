#!/usr/bin/env python
# coding: utf-8

import re
import os
import sys

def dependencyTreeLine(fileLine):
    fileLine = fileLine.replace('\n', '')
    if fileLine == 'PODS:':
        print('pods head: ' + fileLine)
        return ''
    elif fileLine == 'DEPENDENCIES:':
        print('stop reading file')
        outputDotFile()
        dotFileToPdf()
        exit()
    else:
        return fileLine

branketDelete = re.compile(r' \(.*\)')
def removePodVersion(podLine):
    if podLine == None:
        return
    cleanVersionLine = branketDelete.sub('', podLine)
    return cleanVersionLine

slashDelete = re.compile(r'\/.*')
def removeSubspecLine(line):
    if line == None:
        return
    cleanSubspecLine = slashDelete.sub('', line)
    if line.endswith(':'):
        cleanSubspecLine + ':'
    return cleanSubspecLine

rootNode = ''
uniqSet = set([])
def treeToEdge(cleanTreeLine):
    global rootNode
    global uniqSet
    if cleanTreeLine == None:
        return

    if cleanTreeLine.endswith(':') and cleanTreeLine.startswith('  - '):
        rootNode = cleanTreeLine.replace('  - ', '')
        rootNode = rootNode.replace(':', '')
        return
    elif cleanTreeLine.startswith('  - '):
        return
    # leaf node
    else:
        leafNode = cleanTreeLine.replace('    - ', '')
        # 防止 AFNetworking -> AFNetworking 这种情况
        if rootNode != leafNode:
            uniqSet.add('"' + rootNode + '"' + ' -> ' + '"' + leafNode + '";')

def outputDotFile():
    global uniqSet
    writeFileRef = open('PodGraph.dot', 'w')

    # 节点和边的 UI 设置
    writeFileRef.write('digraph {\n\n')
    writeFileRef.write('ranksep=1.5;\n')
    writeFileRef.write('nodesep=0.1;\n')
    writeFileRef.write('edge [color=gray];\n')
    writeFileRef.write('node [shape=box fontcolor=blue fontname=Menlo fontsize=20];\n')

    # 把保存在 uniqSet 的文本写入文件
    for dotLine in uniqSet:
        if dotLine == None:
            continue
        dotLine = dotLine + '\n'
        writeFileRef.write(dotLine)

    writeFileRef.write('\n}')
    writeFileRef.close()
    
def dotFileToPdf():
    os.system('/usr/local/bin/dot PodGraph.dot -Tpdf -o PodGraph.pdf')
    os.system('rm PodGraph.dot')
    os.system('open PodGraph.pdf')  
    pass    

def main():
    podfileLockPath = sys.argv[1]
    with open(podfileLockPath, 'r') as podFileRef:
        for fileLine in podFileRef.readlines():
            podLine = dependencyTreeLine(fileLine)
            cleanVersionLine = removePodVersion(podLine)
            cleanSubspecLine = removeSubspecLine(cleanVersionLine)
            treeToEdge(cleanSubspecLine)

if __name__ == '__main__':
    main()