from tqdm import tqdm
import json
import csv
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
import copy

path_of_vocab = 'entity_vocab_0724.json'
path_of_all_articles = '/corpus/FakeNews/data/covid19/article/covid19_merged_sina_articles_20200724.csv'
path_of_pairs = "covid19_pairs_0724_desp.csv"
path_to_userQA = '/corpus/FakeNews/data/covid19/user_study/20200825/data/userQA.json'
path_of_exp_log = '/corpus/FakeNews/data/covid19/user_study/20200825/data/RL.json'
export_file_name = 'RL_data_user.json'


vocab = dict()
with open(path_of_vocab) as json_file:
    vocab = json.load(json_file)

inv_map = {v: k for k, v in vocab.items()}

corpus = dict()

with open(path_of_all_articles) as csvfile:
    rows = csv.DictReader(csvfile)
    for row in rows:
        corpus[row['id']] = [row['itemId'] ,row['segment_title']]


corpus['PAD'] = 'PAD'
def cosine_similarity_counter(docs_id_lst):
    result = []
    docs_lst = []
    for i in docs_id_lst:
        if i == 'PAD':
            docs_lst.append([i,''])
        else:
            docs_lst.append([i,corpus[i][1]])
    tf = TfidfVectorizer(analyzer='word')
    tfidf_matrix =  tf.fit_transform([content for idx, content in docs_lst])
    scores = linear_kernel(tfidf_matrix[0:1],tfidf_matrix[1:])
    docs_id_lst.pop(0)
    for i in range(len(docs_id_lst)):
        result.append([docs_id_lst[i],scores[0][i]])
    return result

id_test_dct = {}
item_id_event_id = {}
with open(path_of_pairs) as csvfile:
    rows = csv.DictReader(csvfile)
    id_test_dct["random"] = {"fakes":[],"reals":[],"random":[]}
    for row in rows:
        news_id = row["news_id"] #event id
        fake = row["fake"]
        itemId = row["itemId"]
        item_id_event_id[itemId] = news_id
        if news_id not in id_test_dct.keys():
            id_test_dct[news_id] = []
        id_test_dct[news_id].append(itemId)

def color_picker(pairs):
    dct_keys = true_false_dct.keys()
    if pairs[0] not in dct_keys:
        tag = 'random'
    else:
        tag = true_false_dct[pairs[0]]
    if tag == 'fake':
        rbga = "rgba(211,7,7,"
    elif tag == 'real':
        rbga = "rgba(40,178,40,"
    elif tag == 'random':
        rbga = "rgba(68,70,79,"
    score = pairs[1]

    if score > 0.9:
        rbga = rbga + "1.0)"
    elif score > 0.8:
        rbga = rbga + "0.9)"
    elif score > 0.7:
        rbga = rbga + "0.8)"
    elif score > 0.6:
        rbga = rbga + "0.7)"
    elif score > 0.5:
        rbga = rbga + "0.6)"
    elif score > 0.4:
        rbga = rbga + "0.5)"
    elif score > 0.3:
        rbga = rbga + "0.4)"
    elif score > 0.2:
        rbga = rbga + "0.3)"
    elif score >= 0.0:
        rbga = rbga + "0.2)"
    return rbga

user_data = dict()
user_data_lst = open(path_to_userQA)
user_data_lst = user_data_lst.read()
user_data_lst = user_data_lst.split('\n')
print(len(user_data_lst))
user_data_lst.pop()
print(len(user_data_lst))

for i in user_data_lst:
    user_tmp_dct = json.loads(i)
    user = user_tmp_dct['_id']['$oid']
    exps = user_tmp_dct['exps']
    ignore_user = False
    if user_tmp_dct['all_exps_finished'] == False:
        ignore_user = True
    att_fail_times = 0
    for exp in exps:
        for test in ['pretest', 'posttest', 'longterm_test']:
            att_fail_times += 1 if exp[test]['attention']==False else 0
    if att_fail_times >= 3:
        ignore_user = True
    if ignore_user == False:
        user_data[user] = 'pass'
    else:
        user_data[user] = 'fail'
def is_attention(oid):
    return user_data[oid]

target_step = 10
false_dict = dict()
true_dict = dict()
a = open(path_of_exp_log)
a = a.read()
a = a.split('\n')
a.pop()

output_tree = list()
user = 0
for i in a:
    tmp_dct = json.loads(i)
    step = tmp_dct['step']
    user_oid = tmp_dct['_id']['$oid']
    if step != target_step or is_attention(user_oid) == 'fail':
        continue
    else:
        user += 1
        query_relation = tmp_dct['query_entity']
        query_relation = inv_map[query_relation]
        query_relation = item_id_event_id[query_relation] #event_id
        candidates = tmp_dct['step_candidates']
        candidates.reverse()
        candidates.pop(0)
        records = tmp_dct['decision_record']
        records.reverse()
        json_dct = dict()
        tmp_children = list()
        for j in range(len(candidates)):
            entities = candidates[j]['entities']
            decision = records[j][1]

            if j >= 0:
                prev_id = inv_map[records[j+1][1]]
                count_ids = [prev_id]
                for z in entities:
                    count_ids.append(inv_map[z])
                scores_pair = cosine_similarity_counter(count_ids)
                prev_name = corpus[prev_id][0]
                tmp_lst = []
                for z in scores_pair:
                    color = color_picker(z)
                    if z[0] in id_test_dct[str(query_relation)]:
                        stroke_color = "rgba(87, 51, 255, 1)"
                        color = color_picker(z)
                    else:
                        color = "rgba(68,70,79," + color[-4:]
                        stroke_color = color

                    #87, 51, 255
                    if j == 0 and z[0] == inv_map[decision]:
                        if stroke_color == "rgba(87, 51, 255, 1)":
                            stroke_color == "rgba(87, 51, 255, 1)"
                        else:
                            stroke_color = "#000000"
                        tmp_dct = {
                            "name": "",
                            "parent": prev_name,
                            "tip": corpus[z[0]][0],
                            "fill": color,
                            "stroke": stroke_color
                        }
                    elif j != 0 and z[0] == inv_map[decision]:
                        if stroke_color == "rgba(87, 51, 255, 1)":
                            stroke_color == "rgba(87, 51, 255, 1)"
                        else:
                            stroke_color = "#000000"
                        tmp_dct = {
                            "name": "",
                            "parent": prev_name,
                            "tip": corpus[z[0]][0],
                            "fill": color,
                            "stroke": stroke_color,
                            "children" :tmp_children[j-1]
                        }
                    else:
                        # "name": round(z[1],2)
                        tmp_dct = {
                            "name": "",
                            "parent": prev_name,
                            "tip": corpus[z[0]][0],
                            "fill": color,
                            "stroke": stroke_color
                        }

                    tmp_lst.append(copy.deepcopy(tmp_dct))
                    tmp_dct = dict()
                tmp_children.append(tmp_lst)

        dct_keys = true_false_dct.keys()
        decision = inv_map[records[-1][1]]

        if decision not in dct_keys:
            tag = 'random'
        else:
            tag = true_false_dct[decision]
        if tag == 'fake':
            rbga = "rgba(211,7,7,1)"
        elif tag == 'real':
            rbga = "rgba(40,178,40,1)"
        elif tag == 'random':
            rbga = "rgba(68,70,79,1)"
        json_dct = {
                "name": str(user), #pre post long
                "parent": "null",
                "tip": corpus[decision][0],
                "fill": rbga,
                "children": tmp_children[-1],
                "stroke": "#000000"
        }
        output_tree.append(copy.deepcopy(json_dct))
print("Valid samples {}".format(len(output_tree)))

with open(export_file_name,'w') as json_file:
    json.dump(output_tree,json_file,indent=4,ensure_ascii=False)
