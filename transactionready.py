import os
import sys
import pprint
import json
from itertools import count
import operator

class BlockChain:
    forks = []
    startforkarray = []
    transactionlist = []
    repopath = {'mainBranch':[], 'Forks':[]}
    sortedForks = []

    def __init__(self, debug = False) -> None:
        if debug : print ("=============INITiALIZATION START=============")
        if debug : print ("*************PARSING BLOCKS START*************")
        put = os.getcwd()+"\\transactions"
        for i in os.listdir(put):
            soedput = os.path.join(put, i)
            with open(soedput, "r") as file:
                try:
                    dat = json.load(file)
                    self.transactionlist.append(dat)
                finally:
                    if debug : print ("block %s imported" % i)
        self.transactionlist = sorted(self.transactionlist, key=operator.itemgetter('index')) 
        if debug : print ("*************PARSING BLOCKS END***************")
        self.__FindForkStart()
        self.startforkarray.reverse()
        if debug : print ("*************FINDING FORKS START DONE*********")

        for i in self.startforkarray:
            for j in i['forkpair']:
                paths = (self.__BuildFork(j))
                self.repopath['mainBranch'].extend(paths['mainpath']) if paths['mainpath'] is not None else None
                self.repopath['Forks'].append(paths['fork']) if paths['fork'] is not None else None

        #test uniq filtering casue idk why are dublicates in repopath['mainbranch']
        uniqmainbranch = list({v['index']:v for v in self.repopath['mainBranch']}.values())
        firstpath = self.transactionlist[1:17]

        firstpath.extend(uniqmainbranch)
        self.repopath['mainBranch'] = firstpath
        if debug : print ("*************BUILDING FORKS PATHS DONE********")
        self.sortedForks = sorted(self.repopath['Forks'], key=len)
        if debug : print ("*************SORT FORKS PATHS DONE************")
        if debug : print ("=============INITiALIZATION END===============")
        if debug : print (" ")
    
    #find fork starter node and 2 bloack of branches
    def __FindForkStart(self):
        inp = self.transactionlist.copy()
        out = []
        for x2 in range(0,len(inp)):
            el = inp.pop()
            try:
                tmpel = next((x for x in inp if (x['index'] == el['index']) and (x['pre_hash'] == el['pre_hash'])))
                parentnode = next((x for x in inp if (x['hash'] == el['pre_hash'])))
                el['is_main'] = True if el['timestamp'] < tmpel['timestamp'] else  False
                tmpel['is_main'] = True if el['timestamp'] > tmpel['timestamp'] else  False
                out.append({'forkpair':[el,tmpel], 'parentnode':parentnode})
            except:
                pass
        self.startforkarray =  out

    #build branch path
    def __BuildFork(self, start):
        returnobj = {'mainpath':None,'fork':None}
        list = self.transactionlist.copy()
        previositem = list.pop(list.index(start))
        out = [previositem]
        for x2 in range(0,len(list)):
            try:
                nextitem = next(item for item in list if item['pre_hash'] == previositem['hash'])
                previositem = nextitem
                out.append(nextitem)
            except:
                pass
        if start['is_main']:
            returnobj['mainpath'] = out
        else:
            returnobj['fork'] = out
        return returnobj
    
    def CheckBlocksAmount(self):
        sum = len(self.repopath['mainBranch'])
        for el in self.repopath['Forks']:
            sum += len(el)
        print("Total number of blocks: %s" % (sum+1))

    def FindBlockByHashEndPatern(self, patern='000'):
        out = []
        for element in self.transactionlist:
            if element['hash'].endswith(patern):
                out.append(element)
        return out
    
    def getSortetForks(self):
        return self.sortedForks
    
    def getTransactionList(self):
        return self.transactionlist
    
    def findShortestFork(self):
            return self.sortedForks[0]
    
    def findLongestFork(self):
            return self.sortedForks[-1]
    
    def findChainWithoutRewardCnahge(self):
        currentRewardAmount = self.repopath['mainBranch'][0]['transactions'][-1]['value']
        chainlenght=1
        for i in self.repopath['mainBranch']:
            if i['transactions'][-1]['value'] == currentRewardAmount:
                chainlenght+=1
            else:
                break
        return chainlenght
    
    def FindRewardRatio(self):
        return self.repopath['mainBranch'][self.findChainWithoutRewardCnahge()-1]['transactions'][-1]['value'] / self.repopath['mainBranch'][self.findChainWithoutRewardCnahge()-2]['transactions'][-1]['value']
    
    def FindBlockByRewardRatio(self):
        if self.repopath['mainBranch'][-1]['transactions'][-1]['value'] <= 0.09:
            currentlastreward = self.repopath['mainBranch'][-1]['transactions'][-1]['value']
            tmpmainbranch = self.repopath['mainBranch']
            tmpmainbranch.reverse()
            for i in tmpmainbranch:
                if i['transactions'][-1]['value'] == 0.09:
                    blockindex = i['index']
                    break
        else:
            currentlastreward = self.repopath['mainBranch'][-1]['transactions'][-1]['value']
            blockindex = self.repopath['mainBranch'][-1]['index']
            numberofblockstodropreward = self.findChainWithoutRewardCnahge() - (blockindex % self.findChainWithoutRewardCnahge()) 
            blockindex += numberofblockstodropreward
            currentlastreward = currentlastreward * self.FindRewardRatio()
            while round(currentlastreward,2) > 0.09:
                currentlastreward = currentlastreward * self.FindRewardRatio()
                blockindex +=self.findChainWithoutRewardCnahge()
        currentlastreward = round(currentlastreward,2)
        return {'blockindex':blockindex, 'currentlastreward':currentlastreward}
    
    def FindBlocksBySecretBlocks(self):
        listwithSecretsBlock = []
        for i in self.repopath['mainBranch']:
            if i['secret_info']:
                secretblock = {"index":i['index'], "secret_info": i['secret_info']}
                listwithSecretsBlock.append(secretblock)
        return listwithSecretsBlock
    
    def DecodeSecretData(self, data = []):
        outputstring = ""
        outputstring = outputstring.join(data)
        bytes_obj = bytes.fromhex(outputstring)
        return bytes_obj.decode('utf-8')

if __name__ == "__main__" :
    #Init function can be called with unreqirement option debug True/False. Default: False
    myBlockChainContainer = BlockChain()

    print("----- ANALYZE BLOCKCHAIN START -----")
    print("------------------------------------")
    myBlockChainContainer.CheckBlocksAmount()
    print("------------------------------------")
    # #task 1 find block wich ends on 000
    for element in myBlockChainContainer.FindBlockByHashEndPatern('000'):
        print("Task 1. Block index: %d, Author: %s" % (element['index'],element['transactions'][-1]['to']))
    # #task 2 find min lenhgt of fork
    print("Task 2. Min fork lenght: %d" % (len(myBlockChainContainer.findShortestFork())))
    # #task 3 find block index in min lenght fork
    print("Task 3. Min fork lenght first block index: %d" % (myBlockChainContainer.findShortestFork()[0]['index']))
    # #task 4 find max lenhgt of fork
    print("Task 4. Max fork lenght: %d" % (len(myBlockChainContainer.findLongestFork())))
    # #task 5 hash of last block in longest fork - my result
    print("Task 5. Hash of last block (id:%d) of longest fork: %s" % (myBlockChainContainer.findLongestFork()[-1]['index'],myBlockChainContainer.findLongestFork()[-1]['hash']))
    # #task 5 hash of last block in longest fork - seems like mistake
    print("Task 5 - Not my Result. Hash of last block (id:%d) of longest fork: %s" % (myBlockChainContainer.findLongestFork()[-2]['index'],myBlockChainContainer.findLongestFork()[-2]['hash']))
    # #task 6 finding the number of forks that occurred in the system
    print("Task 6 – The number of forks in the system:", (len(myBlockChainContainer.getSortetForks())))
    # #task 7 Reward amount of 71 block
    print("Task 7 - Reward amount for creating block 71:", myBlockChainContainer.getTransactionList()[89]['transactions'][4]['value'])
    # #task 8  Find block chain where reward withoud changes
    print("Task 8 - chain lenght where Reward without changes: %d" % myBlockChainContainer.findChainWithoutRewardCnahge())
    # #task 9  Find reward reduction ratio on first reward drop
    print("Task 9 - Reward reduction ratio: %0.2f" % myBlockChainContainer.FindRewardRatio())
    # #task 10  Predict block index where Rewars is 0,09
    print("Task 10 - block index with reward equal 0.09: %d" %  myBlockChainContainer.FindBlockByRewardRatio()['blockindex'])
    # #task 11 find block indexes with secret_info data
    listSecretIndex = [d['index'] for d in myBlockChainContainer.FindBlocksBySecretBlocks()]
    print("Task 11 - Blocks indexes with information recorded in secret_info: ", listSecretIndex)
    # #task 12 print secret_info data from blockchain
    listSecretData = [d['secret_info'] for d in myBlockChainContainer.FindBlocksBySecretBlocks()]
    print("Task 12 - Blocks secret data: ", listSecretData)
    # #task 13 join secret data, convert to string from hex and print it
    print("Task 13 - Decoded string: %s" % myBlockChainContainer.DecodeSecretData(listSecretData))
    print("------------------------------------")
    print("-------- ALL TASKS COMPLETE --------")
    print("----- ANALYZE BLOCKCHAIN FINISH ----")