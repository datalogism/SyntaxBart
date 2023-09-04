import numpy as np
import json 
import urllib.parse
import pandas as pd
import json 

formats=["turtle","xml","json-ld","ntriples","list","tags","turtleS"]

dir_path="PATH_TO/BART_model/"
print("======================>>>>>>>>>>> BART DATA")
for f in formats:
    print(">>>>>>>>>>>> SPLIT ",f)
    with open(dir_path+"DS_"+f+"_clean_bart.json",encoding="utf-8") as json_file:
        data = json.load(json_file) 
    df = pd.DataFrame.from_dict(data, orient='columns') 
    train_size = 0.6
    validate_size = 0.2
    df = df.sample(frac = 1)
    train, validate, test = np.split(df.sample(frac=1), [int(train_size * len(df)), int((validate_size + train_size) * len(df))])
    with open(dir_path+"DS_"+f+"_train_bart.json", 'w', encoding='utf-8')  as fl:
        json.dump(train.to_dict(orient = 'records') , fl)
    with open(dir_path+"DS_"+f+"_test_bart.json", 'w', encoding='utf-8')  as fl:
        json.dump(test.to_dict(orient = 'records'), fl)
    with open(dir_path+"DS_"+f+"_sample_bart.json", 'w', encoding='utf-8')  as f1:
          json.dump(test.to_dict(orient = 'records')[0:20], f1)
    with open(dir_path+"DS_"+f+"_val_bart.json", 'w', encoding='utf-8')  as fl:
        json.dump(validate.to_dict(orient = 'records'), fl)
        