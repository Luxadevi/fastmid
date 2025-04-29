from re import sub
from typing import Union
import subprocess
from pathlib import Path
import asyncio
import logging
from fastapi import FastAPI, Request
from pydantic import BaseModel
from datetime import time, datetime
import json
import socket
from storage import ClipboardStorage
logboek = logging.getLogger()
app = FastAPI()
p = Path.cwd()

class Commanding(BaseModel):
    command :str
    argumens :str

class Caster(BaseModel):
    website :str

class Clipboard(BaseModel):
    store   :str

def get_caller_info(request: Request) -> dict:
    client_host = request.client.host if request.client else "unknown"
    try:
        hostname = socket.gethostbyaddr(client_host)[0]
    except:
        hostname = "unknown"
    return {
        "ip": client_host,
        "hostname": hostname
    }

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/json")
def read_json(waar=p):
    print(waar)
    return waar

@app.get("/shell/{torun}")
async def shell_command(torun :str):
    logging.basicConfig(filename='love',level=logging.INFO)
    container = ""
    oof = "ifailed"
    try:
        logging.info('starting command on')
        commando = subprocess.run(torun,shell=True,capture_output=True, timeout=10)
        logging.info('finito')
        return commando
    except subprocess.TimeoutExpired:
        print('i failed')
        return oof

@app.get("/arg")
async def shell_command_arg(complete: Commanding):
    try:
        print(complete.command, complete.argumens)
        comp = complete.command +" " + complete.argumens
        print(comp)
        commando = subprocess.run(comp,shell=True,capture_output=True, timeout=10)
        return(commando)

    except TimeoutError:
        err = 'noo'
        return err
    # try:
    #     commando = subprocess.run(Commanding.command, Commanding.argumens)
    #     commando = subprocess.run(complete.command,
    #                               complete.argumens,shell=True,capture_output=True, timeout=
# @app.get("/cast")
# async def casting(url: Caster):
#     try:
#         uv_Command = "uvx catt cast "
#         combine = uv_Command + url.website
#         commando = subprocess.check_output(combine, shell=True,stderr=subprocess.STDOUT)
#         sux = 'je begint zo te spelen'
#         print(commando)
#         return sux


#     except subprocess.CalledProcessError as exc:
#             print(exc.returncode, exc.commando)
#     else:
#         print("Output: \n{}\n".format(commando))

@app.get("/cast")
async def casting(url: Caster):
    uv_Command = "uvx catt cast "
    combine = uv_Command + url.website
    print(combine)
    try:
        output = subprocess.check_output(
            combine , stderr=subprocess.STDOUT, shell=True, timeout=30,
            universal_newlines=False)
    except subprocess.CalledProcessError as exc:
        print("Status : FAIL", exc.returncode, exc.output)
        l = print("Status : FAIL", exc.returncode, exc.output)
        return exc.output
    else:
        print("Output: \n{}\n".format(output))
        return output

@app.put("/clipboard")
async def clipboard(text: Clipboard, request: Request):
    storage = ClipboardStorage()
    try:
        caller_info = get_caller_info(request)
        storage.insert_data(text.store, caller_info["ip"], caller_info["hostname"])
        return {"message": "Text written to clipboard", "caller": caller_info}
    except IOError as e:
        return {"message": f"Error writing to clipboard: {str(e)}"}
    except Exception as e:
        return {"message": f"Unexpected error: {str(e)}"}

@app.get("/clipboard")
async def get_clipboard():
    storage = ClipboardStorage()
    try:
        entries = storage.get_entries()
        return {"entries": entries}
    except Exception as e:
        return {"message": f"Error getting clipboard entries: {str(e)}"}

