# -*- coding: utf-8 -*-

'''
Created on 1 déc. 2014

@author: briner
'''


class Cache(object):
    '''
    classdocs
    '''
    def __init__(self):
        self._co=[]
    def add(self, inst):
        type_inst=type(inst)
        self._co.append(type_inst, inst)
    def get_type(self,type_inst):
        return filter(lambda x:x[0] == type_inst, self._co)[:]
    def get(self, type_inst):
        return filter(lambda x:(x[0] == type_inst)and(.), self._co)[:]

    
        