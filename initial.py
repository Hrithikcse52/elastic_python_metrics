from elasticsearch import Elasticsearch
import psutil




def connect_elasticsearch():
    _es = None
    _es = Elasticsearch([{'host': 'localhost', 'port': 9200}])
    if _es.ping():
        print('Yay Connected')
    else:
        print('Awww it could not connect!')
    return _es



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



def create_index_cpu(es_object, index_name):
    created = False
    settings = {
    "mappings": {
        "properties": {
            "cpu_usage": {"type": "float"},
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

def create_index_mem(es_object, index_name):
    created = False
    settings = {
    "mappings": {
        "properties": {
            "memory_usage": {"type": "integer"},
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




def send_data_cpu(res):
    es = connect_elasticsearch()
    if es is not None:
        if create_index_cpu(es, 'cpu'):
            out = store_record(es, 'cpu', res)
            print('Data indexed CPU',out)




def send_data_mem(res):
    es = connect_elasticsearch()
    if es is not None:
        if create_index_mem(es, 'cpu'):
            out = store_record(es, 'cpu', res)
            print('Data indexed MEM',out)
def main():
    
    cpu_data = []
    memory_data = []
    for process in psutil.process_iter():
        with process.oneshot():
            cpu_usage = psutil.cpu_percent(interval=0.01)/psutil.cpu_count()
            cpu_data.append({
            'cpu_usage' : cpu_usage
            })
            print("process",process.pid)
    for process in psutil.process_iter():
        with process.oneshot():
            memory_usage = process.memory_full_info().uss / (1024 *1024)
            memory_data.append({
            'memory_usage' : memory_usage
            })


    for p in cpu_data:
        send_data_cpu(p)
    
    for p in memory_data:
        send_data_mem(p)




   

if __name__ == '__main__':
    main()

