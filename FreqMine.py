# author: 周昊天 1400012866

import csv
import time

class treeNode:     
    '''basic class for treenode implement'''
    def __init__(self, nameVal, numOccur, parentNode):  
        self.name = nameVal         # name of the node
        self.count = numOccur       # node count
        self.nodeLink = None        # will be used in header table
        self.parent = parentNode    # Reference of parent node 
        self.children = {}          # Dict of childrens
    
    def add_count(self, numOccur):  # add node count
        self.count += numOccur      
          
    def write_out(self, ind = 2):   # tree output function -- optional
        outstr = (' '*ind) + str(self.name) + ' ' + str(self.count)
        f.write(outstr)
        f.write('\n')
        for child in self.children.values():
            child.write_out(ind + 2)


def CreateTree(dataSet, MinSupVal=1):       
    '''basic method for creating FP-Tree'''
    headerTable = {}  
    for trans in dataSet:       # creating header table
        for item in trans:  
            headerTable[item] = headerTable.get(item, 0) + dataSet[trans]  

    for k in headerTable.keys():        # removing items whose frequency < MinSupVal
        if headerTable[k] < MinSupVal:  
            del(headerTable[k])    

    freqItemSet = set(headerTable.keys())  # containing frequent items
    if len(freqItemSet) == 0:   # if no item meets the criteria, end and quit
        return None, None
    
    for k in headerTable:       # prepare for adding nodeLink
        headerTable[k] = [headerTable[k], None]  

    return_tree = treeNode('NULL', 0, None)     # root node of FP-Tree
    for tranSet, count in dataSet.items():      # traversing dataset by transaction(a line in csvfile)
        # putting items into a dict(easier for sorting)
        tmpDict = {}  
        for item in tranSet:   
            if item in freqItemSet:  
                tmpDict[item] = headerTable[item][0]
        # sort items by frequency, in a descending order.
        if len(tmpDict) > 0:  
            in_order_items = [v[0] for v in sorted(tmpDict.items(), key = lambda p:p[1], reverse = True)] 
            # update tree iteratively
            UpdateTree(in_order_items, return_tree, headerTable, count)
    return return_tree, headerTable

def UpdateTree(items, curTree, headerTable, count):  
    '''update FP-Tree and header table'''   
    if items[0] in curTree.children:        # already created the node, just add the count
        curTree.children[items[0]].add_count(count)  
    else:
        curTree.children[items[0]] = treeNode(items[0], count, curTree)   # create the node
        # updating header table nodelink
        if headerTable[items[0]][1] == None:        # header table link not established
            headerTable[items[0]][1] = curTree.children[items[0]]  
        else:                                       # established, link it to current node
            UpdateHeaderTable(headerTable[items[0]][1], curTree.children[items[0]])  

    if len(items) > 1:      # update the tree recursively
        UpdateTree(items[1::], curTree.children[items[0]], headerTable, count)  
    
def UpdateHeaderTable(update_node, target_node):  
    '''update header table link'''
    while (update_node.nodeLink !=  None):      # finding the tail of header link
        update_node = update_node.nodeLink  
    update_node.nodeLink = target_node          # connect it to current node


def FindPrefix(leafNode, prefixPath):   
    '''finding the whole prefix path recuisively'''
    if leafNode.parent != None:         # adding to prefix if not reached root
        prefixPath.append(leafNode.name)
        FindPrefix(leafNode.parent, prefixPath)
  
def FindCondPat(treeNode):
    '''finding conditional patterns by header links'''
    cond_patterns = {}  
    while treeNode != None:     # process tree nodes along the link route
        prefixPath = []         # list of prefix path of node
        FindPrefix(treeNode, prefixPath)    # find prefix path of node
        if len(prefixPath) > 1:     
            # freq item found
            cond_patterns[frozenset(prefixPath[1:])] = treeNode.count  
        treeNode = treeNode.nodeLink    # go to next node
    return cond_patterns  
  
def MineTree(curTree, headerTable, MinSupVal, prefix, freqItemList):  
    '''mine the initial FP-Tree recursively'''
    bigL = [v[0] for v in sorted(headerTable.items(), key=lambda p:p[1])]   # header table items
    for basePat in bigL:    # mining tree by header table links
        # modify prefix path
        newFreqSet = prefix.copy()
        newFreqSet.add(basePat)
        # add the path to frequent item list
        freqItemList.append(newFreqSet) 
        # creating conditional patterns
        condPatBase = FindCondPat(headerTable[basePat][1])  
        # creating conditional tree
        CondTree, Head = CreateTree(condPatBase, MinSupVal)   
        
        if Head != None:    # if head table of the cond tree is not empty, go on
            MineTree(CondTree, Head, MinSupVal, newFreqSet, freqItemList)  


def CreateInitSet(dataSet):
    '''create a dict that records transaction items and their frequency'''
    retDict = {}  
    for trans in dataSet:  
        trans = frozenset(trans)
        if retDict.get(trans, 0) > 0:
            retDict[trans] += 1
        else:
            retDict[trans] = 1
    return retDict  

def LoadData():
    '''transform the original csv file to a list for further use'''
    totalList = []
    with open('project4 - Groceries.csv') as f:
        f_csv = csv.DictReader(f)
        for row in f_csv:
            s = row['items']
            s = s.lstrip('{').rstrip('}')
            row_items = s.split(',')
            totalList.append(row_items)
    return totalList



if __name__ == "__main__": 
    
    inputData = LoadData()      # loading original data
    initSet = CreateInitSet(inputData)      # create initial item set

    MinSupList = [100, 250, 500, 750, 1000]     # list of min support value to iterate
    for MinSupportValue in MinSupList:          # iterate different min support value
        start = time.clock()        # timer
        f = open('result_' + str(MinSupportValue) + '.txt', 'w')    # output file
        print 'Minimum support value: ' + str(MinSupportValue)

        print 'Creating FP-Tree...'
        FP_Tree, Header_Table = CreateTree(initSet, MinSupportValue)               
        print 'FP-Tree created.'

        print 'Mining initial FP-Tree...'
        freqItems = []      # list for frequent items result
        MineTree(FP_Tree, Header_Table, MinSupportValue, set([]), freqItems)
        print 'Mining Process completed.'

        # print out final result
        f.write('\nFrequent Items: \n')
        for item in freqItems:
            f.write(str(list(item)))
            f.write('\n')
        
        print 'Elapsed time: ' + str(time.clock() - start)      # timer
        print '--------'
        f.close()
    print '------------Finished------------'
