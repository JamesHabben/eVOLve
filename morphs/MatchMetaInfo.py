#__author__ = 'john.lukach'

import requests
from morphs.BaseMorph import BaseMorph

class MatchMetaInfo(BaseMorph):
    name = 'MatchMetaInfo'
    displayname = 'MatchMetaInfo'
    helptext = 'Shows filenames that do not match the NSRL collection'
    plugins = ['pslist']
    config = {
        'mmi':{
            'name':'MatchMetaInfo API',
            'description':'Website hosting the filenames in the NSRL collection',
            'type':'string',
            'defaultvalue':'http://matchmeta.info',
            'required':True
        }
    }

    def morph(self, data):
        if data['name'] == 'pslist':
            colnum = data['columns'].index('Name')
            for idx,row in enumerate(data['data']):
		r = requests.get(self.config['mmi']['defaultvalue']+'/'+row[colnum])
		#print '\t'+self.config['mmi']['defaultvalue']+'/'+row[colnum]+' '+r.text
                if r.text == 'NA':
                    row = list(row)
                    row[colnum] = {'value':row[colnum],'style':'background-color:yellow;'}
                    data['data'][idx] = row
