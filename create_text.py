import json
import os
from datetime import datetime as dt, timezone as tz

files = os.listdir('./uscis/data/json')
for i, file in enumerate(files):
    try:
        filename = str(i).zfill(4)
        txtfile = f'{filename}.txt'
        metafile = f'{filename}.txt.metadata.json'
        with open('./uscis/data/json/' + file) as f:
            doc = json.load(f)
            with open('./uscis/data/txt/' + txtfile, 'w') as fw:
                fw.write(f"Title : {doc['title']}")
                fw.write("\n")
                fw.write(f"URL : {doc['url']}")
                fw.write("\n")
                if 'last_updated' in doc:
                    fw.write(f"Last Updated : {doc['last_updated']}")
                    fw.write("\n")
                fw.write("\n")
                fw.write('\n'.join(doc['body']))

            with open('./uscis/data/meta/' +  metafile, 'w') as fw:
                #last_updated = dt.strptime(doc['last_updated'], "%m/%d/%Y")
                meta = {
                    "Attributes": {
                        "_created_at": dt.now(tz.utc).astimezone().isoformat(),
                        #"uscis_last_updated_at": last_updated.astimezone().isoformat(),
                        "_source_uri": doc['url'],
                        "_version": "0.1" 
                    },
                    "Title": doc['title'], 
                    "ContentType": "MD"
                }  
                json.dump(meta, fw)
    except:
        continue
