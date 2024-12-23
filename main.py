from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import tarfile
import os
import docker
import uuid  # create only filename
import re  # clean string

app = FastAPI()

# CORS(處理跨域資源共享) : 允許不同領域的請求
app.add_middleware(
    CORSMiddleware, # 跨域訪問設置
    allow_origins = ['http://127.0.0.1:8000'],
    allow_credentials = True, # 允許請求攜帶憑據
    allow_methods = ['*'], # 允許所有HTTP方法
    allow_headers = ['*'] # 允許所有標頭 
)

client = docker.from_env() # 創建docker用戶端
templates = Jinja2Templates(directory='templates')

class Code(BaseModel):
    id_code : str
    action : str

# create file
unique_filename = f'program_{uuid.uuid4().hex}' # make a unique filename (to prevent repeatly)
source_file = f'{unique_filename}.cpp'
executable_file = f'{unique_filename}'
error_file = f'{unique_filename}.txt'
tar_file = 'source.tar'

@app.get('/')
async def read_root(request : Request):
    print(10)
    return templates.TemplateResponse('index.html',{"request" : request})

@app.post("/compile")
async def compile_code(request : Request, code : Code):
    print(code.id_code)
    if not code.id_code.strip():
        return {"status" : "error" , "message" : "Empty code"}
    

    container = client.containers.get('cpp_compiler')

    if code.action == "c":
        print(code.id_code)

        # write code in source_file
        with open(source_file, 'w') as f:
            f.write(code.id_code)
        # source_file to tar
        with tarfile.open(tar_file, 'w') as tar:
            tar.add(source_file, arcname = os.path.basename(source_file))

        # mv source_file /tmp
        with open(tar_file, 'rb') as f:
            container.put_archive('/tmp', f.read())
        
        # compile source_file and put the error in error_file
        compile_linux = f'g++ /tmp/{source_file} -o /tmp/{executable_file} 2> /tmp/{error_file}'
        compile_result = container.exec_run(compile_linux, shell = True)
   
        # check compile error
        error_check = container.exec_run(f'cat /tmp/{error_file}')
        compile_error = error_check.output.decode('utf-8').strip()

        if compile_result.exit_code != 0 or compile_error:
            return {
                "status" : "compilation_error" ,
                "message" : compile_result.output.decode('utf-8') + "\n" + compile_error,
                "detail" : {
                    "exit_code" : compile_result.exit_code
                }
            }

    return {"status" : "success" , "message" : "Code compiled successfully"}
