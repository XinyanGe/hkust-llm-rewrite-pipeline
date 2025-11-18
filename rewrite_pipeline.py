import json
import requests
import time
from tqdm import tqdm
import os
import sys
from openai import OpenAI
from concurrent.futures import ThreadPoolExecutor, as_completed


YOUR_SERVER_URL = "YOUR_SERVER_URL"
YOUR_API_KEY = "YOUR_API_KEY"
YOUR_ACCESS_KEY = "YOUR_ACCESS_KEY"
YOUR_MODEL_ENDPOINT = "YOUR_MODEL_ENDPOINT"
GPT_SERVER_URL = "YOUR_GPT_SERVER_URL"

model_list = ['gpt-4o-mini-2024-07-18', 'gpt-4o-2024-08-06', 'gpt-4o-2024-11-20', 'o1']
best_model = 'gpt-4o-2024-11-20'
ci_best_model = 'gpt-4o-2024-08-06'

last_sentence = ''

# 请求GPT系列
def requestGPT4(instruction, query, ak, temperature, model='gpt-4o-mini-2024-07-18', max_retries=100000000):
    headers = {"Content-Type": "application/json"}
    data = {
        "messages": [
            {"role": "system", "content": instruction},
            {"role": "user", "content": query}
        ],
        "model": model, 
        "max_tokens": 1000,
        "temperature": temperature,
        "top_p": 0,
        "logit_bias": {},
        "n": 1,
        "stream": False
    }

    for attempt in range(max_retries):
        try:
            # 发送请求
            response = requests.post(f"{GPT_SERVER_URL}?ak={ak}", headers=headers, json=data)
            res = json.loads(response.text)  # 将响应解析为 JSON
            
            # 提取结果
            result = res['choices'][0]['message']['content'].strip()
            return result  # 如果成功，立即返回结果

        except Exception as e:
            print(f"[ERROR] Request failed on attempt {attempt + 1}: {e}")
            time.sleep(5)  # 等待 2 秒后重试
    return f"Failed to get a response after {max_retries} retries."

# 请求豆包
def requestDoubao(instruction, query, max_retries=100000000):
    client = OpenAI(
        base_url="YOUR_SERVER_URL",
        api_key="YOUR_API_KEY",
    )
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(

                model="YOUR_MODEL_ENDPOINT",
                messages = [
                    {"role": "system", "content": instruction},
                    {"role": "user", "content": query},
                ],
            )
            res=json.loads(response.model_dump_json())
            results,thinking_res=res["choices"][0]["message"]["content"],res["choices"][0]["message"]["reasoning_content"]
            return results
        except Exception as e:
            print(f"[ERROR] Request failed on attempt {attempt + 1}: {e}")
            time.sleep(5)  # 等待 2 秒后重试
    return f"Failed to get a response after {max_retries} retries."

# 请求deepseek-r1
def requestDeepseek(instruction, query, max_retries=100000000):
    client = OpenAI(
        api_key = "YOUR_API_KEY",
        base_url = "YOUR_SERVER_URL",
    )
    for attempt in range(max_retries):
        try:
            completion = client.chat.completions.create(
            model = "YOUR_MODEL_ENDPOINT",  # your model endpoint ID
            messages = [
                {"role": "system", "content": instruction},
                {"role": "user", "content": query},
            ],
        )
            res=completion.choices[0].message.content.strip()
            results,thinking_res=res["choices"][0]["message"]["content"],res["choices"][0]["message"]["reasoning_content"]
            return results 
        except Exception as e:
            print(f"[ERROR] Request failed on attempt {attempt + 1}: {e}")
            time.sleep(5)  # 等待 2 秒后重试
    return f"Failed to get a response after {max_retries} retries."
   

import requests
import json
import random
import time

def requestGPT4_plus(instruction, query, label, ak, temperature, model='gpt-4o-mini-2024-07-18', max_retries=100000000):
    headers = {"Content-Type": "application/json"}
    data = {
        "messages": [
            {"role": "system", "content": instruction},
            {"role": "user", "content": query}
        ],
        "model": model, 
        "max_tokens": 1000,
        "top_p": 0,
        "logit_bias": {},
        "n": 1,
        "stream": False
    }

    for attempt in range(max_retries):
        try:
            # 设置当前温度
            data["temperature"] = temperature
            
            # 发送请求
            response = requests.post(f"{GPT_SERVER_URL}?ak={ak}", headers=headers, json=data)
            res = json.loads(response.text)  # 将响应解析为 JSON

            # 提取结果
            result = res['choices'][0]['message']['content'].strip()

            # 检查结果的最后 25 个字符是否包含 label 中的汉字
            if any(char in result[-25:] for char in label):
                return result  # 满足条件则返回结果

            # 如果不满足条件，随机调整温度
            temperature = round(random.uniform(0.1, 1.5), 2)  # 随机生成 0.1 到 1.5 的温度值
            print(f"[INFO] Adjusting temperature to {temperature} and retrying request...")

        except Exception as e:
            print(f"[ERROR] Request failed on attempt {attempt + 1}: {e}")
            time.sleep(5)  # 等待 5 秒后重试

    # 超过最大尝试次数仍失败
    return f"Failed to get a response after {max_retries} retries."

def process_manyidu_v3(temp, instruction, ak, model):
    temp = json.loads(temp)
    cur_input = '当前的标题为：' + temp['Title'] + '\n我需要你改写的文案为：' + temp['Conclusion'] + '\n这篇信息的来源为：' + temp['OrgNameDisc'] + '\n请给出你的改写，要求长度和原文案类似，内容不得进行修改，写作风格也需要和原文类似：'
    # gpt_out = requestGPT4(instruction, cur_input, ak, 0.7, model).replace('**', '')
    doubao_out = requestDoubao(instruction, cur_input)
    # return gpt_out
    return doubao_out


def manyidu_pipeline(model, instruction, file_path):
    ll = []
    with open(file_path,"r",encoding='utf-8') as f:
        for line in f:
            ll.append(line)
    ak = YOUR_ACCESS_KEY
    output_path = file_path.replace('.jsonl', '_deepseek.jsonl')
    with open(output_path, 'w', encoding='utf-8') as output_line:
        # 使用多线程进行处理
        with ThreadPoolExecutor(max_workers=64) as executor:
            future_to_line = {
                executor.submit(process_manyidu_v3, line, instruction, ak, model): line for line in tqdm(ll)
            }

            for future in tqdm(as_completed(future_to_line), total=len(future_to_line), desc='Processing Tasks'):
                line = future_to_line[future]  # 获取对应的输入数据
                try:
                    result = future.result()  # 获取处理结果
                    line = json.loads(line)
                    line['gpt_result'] = result
                    output_line.write(json.dumps(line, ensure_ascii=False) + '\n')  # 写入结果文件
                except Exception as e:
                    print(f"[ERROR] Exception occurred while processing line {e}")
    print('done')


def split_geci(input_path):
    raw_data = []
    for file in os.listdir(input_path):
        if '.jsonl' in file and 'eng' not in file:
            with open(os.path.join(input_path, file), 'r', encoding='utf-8') as f:
                for line in tqdm(f):
                    try:
                        data = json.loads(line)
                        data = data['gpt_result']
                        if '抱歉' in data:
                            continue
                        else:
                            raw_data.append(data)
                    except:
                        continue
    new_data = []
    for line in raw_data:
        new_data.append(line)
    new_data = list(set(new_data))
    output_list = []
    for line in new_data:
        for l in line.split('|'):
            output_list.append(l)
    output_path = os.path.join(input_path, 'kuochong_data.txt')
    with open(output_path, 'w', encoding='utf-8') as writer:
        for line in output_list:
            writer.write(line+'\n')
    print('done')

def test_read(input_file='path/to/your/output/kuochong_data.txt'):
    with open(input_file, 'r', encoding='utf-8') as reader:
        for line in reader:
            if line != '':
                print(line.replace('\n', ''))


if __name__=="__main__":
    manyidu_pipeline(best_model, '你是一个专业的写手，专门负责商业文案的改写工作\n', 'data/finace_work/filter_data.jsonl')
    