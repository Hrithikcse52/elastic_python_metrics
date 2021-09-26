from elasticsearch import Elasticsearch
import psutil
import json
from psutil._common import bytes2human



def connect_elasticsearch():
    _es = None
    _es = Elasticsearch([{'host': 'localhost', 'port': 9200}])
    if _es.ping():
        print('Yay Connected')
    else:
        print('Awww it could not connect!')
    return _es

def create_index(es_object, index_name):
    created = False
    settings = {
    "mappings": {
        "properties": {
            "pid": {"type": "integer"},
            "name": {"type": "text"},
            "memory": {"type": "integer"},
            "cpu_time": {"type": "integer"},
            }
        }
    }
    try:
        if not es_object.indices.exists(index_name):
            es_object.indices.create(index=index_name, ignore=400, body=settings)
            print('Created Index')
        created = True
    except Exception as ex:
        print(str(ex))
    finally:
        return created



def store_record(elastic_object, index_name, record):
    is_stored = True
    try:
        outcome = elastic_object.index(index=index_name, body=record)
        print(outcome)
    except Exception as ex:
        print('Error in indexing data')
        print(str(ex))
        is_stored = False
    finally:
        return is_stored

def send_data(res):
    es = connect_elasticsearch()
    if es is not None:
        if create_index(es, 'metrics'):
            out = store_record(es, 'metrics', res)
            print('Data indexed successfully',out)


def get_cpu(pid):
    print(pid)
    p = psutil.Process(pid)
    return p.cpu_percent(interval=None)

def main():
    # pprint_ntuple(psutil.virtual_memory())
    total_in_bytes = getattr(psutil.virtual_memory(),'total')
    forty_percent_memory = total_in_bytes *0.4
    total_human_read = bytes2human(total_in_bytes)
    pp = ([(p.pid, p.info['name'], int((p.info['memory_info'].rss) /(1024*1024)) , sum(p.info['cpu_times'])) for p in sorted(psutil.process_iter(['name', 'memory_info','cpu_times']), key=lambda p: sum(p.info['cpu_times'][:2]))])
    
    
    
    
    modelType = ['pid','name','memory' ,'cpu_time']
    model = [{ modelType[i] : it[i] for i  in range(0,4)} for it in pp ]
    

    
    
    res =json.dumps(model)
    for it in model:
        # print(it)
        send_data(it)



if __name__ == '__main__':
    main()