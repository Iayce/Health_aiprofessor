from flask import Flask, request, send_file, make_response,Response
from flask_cors import CORS
import json
from MLLM import DiscMedlLLM
import logging

MLLM = DiscMedlLLM() #模型初始化


app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "https://yiyan.baidu.com"}})
# 日志初始初始化
log_filename = "web_server.log"
logging.basicConfig(filename=log_filename, level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

user_record = []
medicalrecord = { } #创建病历本dict，构造症状—诊断映射
def make_json_response(data, status_code=200):
    response = make_response(json.dumps(data), status_code)
    response.headers["Content-Type"] = "application/json"
    return response


@app.before_request
def log_each_request():
    logging.info('【请求方法】{}【请求路径】{}【请求地址】{}'.format(request.method, request.path, request.remote_addr))

@app.route("/add_symptom", methods=['POST'])
async def add_symptom():
    """
        添加一个症状
    """
    print("route /add_symptom begin")
    logging.info('symptom: ',symptom)
    symptom = request.json.get('symptom', "")
    print(symptom)
    user_record.append(symptom)
    medicalrecord[symptom] = ''
    logging.info('med_record: ',medicalrecord)
    print("/add_symptom FINISHED, 病历本：",medicalrecord)
    return make_json_response({"message": "症状添加成功"})


@app.route("/delete_symptom", methods=['DELETE'])
async def delete_word():
    """
        删除一个症状
    """
    symptom = request.json.get('symptom', "")
    # print("route /delete_symptom begin; symptom to delete: ",symptom)
    logging.info('symptom: ',symptom)
    if symptom in medicalrecord:
        del[medicalrecord[symptom]]
    print("/delete_symptom FINISHED, 病历本：",medicalrecord)
    logging.info('med_record: ',medicalrecord)
    return make_json_response({"message": "症状删除成功"})

@app.route("/medical_chat",methods = ['POST'])
async def chat():
    '''
    调用Disc模型进行回答
    '''
    
    asking = request.json.get('asking', "")
    logging.info('asking: ',asking)
    print("route /medical_chat begin, request:",asking)
    
    # wrapped_record = '   病历本:['+str(medicalrecord) +']'
    
    answer = MLLM.mchat(asking)
    logging.info('answer: ',answer)
    return make_json_response({"message": f"{answer}"})


@app.route("/get_medicalrecord")
async def get_medicalrecord():
    """
        获得病历本
    """
    print("route /get_medicalrecord begin")
    
    print("/get_medicalrecord:",str(medicalrecord))
    logging.info('med_record',medicalrecord)
    return make_json_response({"medicalrecord": medicalrecord})

@app.route("/generate_diagnosis",methods = ['POST'])
async  def generate_diagnosis():
    
    symptom = request.json.get('symptom', "")
    logging.info('symptom',symptom)
    print(symptom)
    print(json.dumps(request.get_json()))
    #user_record.append(symptom)
    medicalrecord.update({symptom:" "})
    logging.info('med_record',medicalrecord)
    
    print("route /generate_diagnosis begin, symptom:",symptom)
    
    wrapped_record = '请根据病历本生成诊断：   病历本:['+str(medicalrecord) +']'
    print("/generate_diagnosis,wrapped_record:",wrapped_record)
    if symptom in medicalrecord:
        logging.info('symptom in medicalrecord')
        dignosis = MLLM.mchat(symptom + wrapped_record)
        medicalrecord.update({symptom: dignosis})
        logging.info('med_record',medicalrecord)
        return make_json_response({"diagnosis": f"{dignosis}"})
    else:
        logging.info('symptom NOT in medicalrecord')
        medicalrecord.update({symptom: ''})
        dignosis = MLLM.mchat(symptom + wrapped_record)
        medicalrecord.update({symptom: dignosis})
        logging.info('med_record',medicalrecord)
        return make_json_response({"diagnosis": f"{dignosis}"})

@app.route("/healthcare_professor.png")
async def plugin_logo():
    """
        注册用的：返回插件的logo，要求48 x 48大小的png文件.
        注意：API路由是固定的，事先约定的。
    """
    return send_file('healthcare_professor.png', mimetype='image/png')


@app.route("/.well-known/ai-plugin.json")
async def plugin_manifest():
    """
        注册用的：返回插件的描述文件，描述了插件是什么等信息。
        注意：API路由是固定的，事先约定的。
    """
    host = request.host_url
    with open(".well-known/ai-plugin.json", encoding="utf-8") as f:
        text = f.read().replace("PLUGIN_HOST", host)
        return text, 200, {"Content-Type": "application/json"}


@app.route("/.well-known/openapi.yaml")
async def openapi_spec():
    """
        注册用的：返回插件所依赖的插件服务的API接口描述，参照openapi规范编写。
        注意：API路由是固定的，事先约定的。
    """
    with open(".well-known/openapi.yaml", encoding="utf-8") as f:
        text = f.read()
        # return text, 200, {"Content-Type": "text/yaml"}
        return Response(text, status=200, content_type="text/yaml; charset=utf-8")
        

@app.route("/.well-known/example.yaml")
async def example_yaml():
    """
        注册用的：example 文件
        注意：API路由是固定的，事先约定的。
    """
    with open(".well-known/example.yaml", encoding="utf-8") as f:
        text = f.read()
        # return text, 200, {"Content-Type": "text/yaml"}
        return Response(text, status=200, content_type="text/yaml; charset=utf-8")


@app.route('/')
def index():
    return 'welcome to my webpage!'

if __name__ == '__main__':
    try:
        import os
        print(os.getcwd())
        app.run(debug=True, host='0.0.0.0', port=6006, use_reloader=False,ssl_context=('./cert.pem', './privkey.pem'))
    except KeyboardInterrupt:
        exit(0)