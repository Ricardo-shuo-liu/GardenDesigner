from gardendesigner.config import param


def test_EnvFiler_function():
    """测试环境变量创建功能"""
    # 创建功能对象
    envfiler = param.EnvFiler()
    config_path = envfiler.get_config_path()

    # test1创建
    envfiler.make(key="",model="")
    with open(config_path,"r") as fp:
        content = fp.read()
        print(content)
    
    # test2 覆盖内容
    envfiler.make(key="mykeys",model="mymodels")
    with open(config_path,"r") as fp:
        content = fp.read()
        print(content)
    
    # test3 使用base_url
    envfiler.make(key="mykeys",model="mymodels",base_url="mybase_url")
    with open(config_path,"r") as fp:
        content = fp.read()
        print(content)
    
    # test4 测试覆盖base_url
    envfiler.make(key="mykeys",model="mymodels")
    with open(config_path,"r") as fp:
        content = fp.read()
        print(content)
def test_GetEnvParam_function():
    envfiler = param.EnvFiler()
    config_path = envfiler.get_config_path()
    getEnvParam = param.GetEnvParam(config_path=config_path)
    params = []
    try:  
        API_KEY = getEnvParam.get_key()
        params.append({"API_KEY":API_KEY})
        MODEL_NAME = getEnvParam.get_model_name()
        params.append({"MODEL_NAME":MODEL_NAME})
        BASE_URL = getEnvParam.get_base_url()
        params.append({"BASE_URl":BASE_URL})
    except Exception as e:
        print(params)
    finally:
        print(params)
if __name__ == "__main__":
    test_EnvFiler_function()
    test_GetEnvParam_function()