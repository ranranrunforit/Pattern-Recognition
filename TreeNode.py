# a tree node
# optionally takes the parent=>another TreeNode, children=>list of TreeNode
# (will make this an empty list if none are added), data=>a target value string, splitAttrib=>attribute string,
# entropy=>a float value for entropy
class TreeNode:
    def __init__(self, target, parent=None, children=None, data=None, splitAttrib=None, entropy=None):
        if children == None:
            children = []
        self.parent = parent
        self.children = children
        self.data = data
        self.splitAttrib = splitAttrib
        self.entropy = entropy
        self.tabs = ''
        self.cho_Target = target

    # just ads a child and automatically sets the child's parent
    def addChild(self, childNode):
        childNode.parent = self
        self.children.append(childNode)


    # prints the results
    def printTree(self,tabs=None):
        if tabs == None:
            tabs = ""
        if self.data == None:
            if self.splitAttrib != None:
                if len(tabs) < 1:
                    print "if %s , then " % (self.splitAttrib)
                else:
                    print "%s if %s , then " % (tabs, self.splitAttrib)
                tabs += "\t"
            for c in self.children:
                c.printTree(tabs=tabs)
        else:
            if len(tabs) < 1:
                print "if %s , then %s is %s" %(self.splitAttrib, self.cho_Target, self.data)
            else:
                print "%s if %s , then %s is %s" % (tabs, self.splitAttrib, self.cho_Target, self.data)
