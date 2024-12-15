from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates 
from fastapi.responses import HTMLResponse
import subprocess # shell

app = FastAPI()
template = Jinja2Templates(directory="templates")

@app.get( '/' , response_class=HTMLResponse)
async def read_root(request : Request):
    return template.TemplateResponse('index.html', {"request" : request})

@app.post('/compile', response_class=HTMLResponse)
async def complier_code(request : Request):
    try:
        compile_process = subprocess.run(
            ["g++", "/app/program.cpp", "-o", "/app/program"],
            check = True,
            stdout = subprocess.PIPE,
            stderr = subprocess.PIPE
           )
        output = compile_process.stdout.decode('utf-8') #correct
        error = compile_process.stderr.decode('utf-8') #error
        return template.TemplateResponse('index.html', {"request" : request, "output" : output, "error": error})
    except subprocess.CalledProcessError as e:
        error = e.stderr.decode('utf-8')
        return template.TemplateResponse('index.html', {"request" : request, "error" : error})
