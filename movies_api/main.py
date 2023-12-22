from fastapi import FastAPI, UploadFile, File,Depends
from fastapi.responses import HTMLResponse, JSONResponse


from config.database import engine,Base
from middlewares.error_handler import ErrorHandler
from routers.movie import movie_router
from routers.user import user_router


import shutil
import os
import nistitl
from typing import IO
import base64
from PIL import Image
import wsq

app = FastAPI()
app.title = "Mi app de prueba con FastAPI"
app.version = "0.0.1"

app.add_middleware(ErrorHandler)
app.include_router(movie_router)
app.include_router(user_router)



Base.metadata.create_all(bind= engine)

UPLOADS_DIR = "./uploads/"

if not os.path.exists(UPLOADS_DIR):
    os.makedirs(UPLOADS_DIR)


@app.get('/', tags=["home"])


def message():
    return HTMLResponse('<h1>Hey prro</h1>')



@app.post("/uploadNIST/")
async def upload_nist(file: UploadFile = File(...)):
    with open(f"{UPLOADS_DIR}{file.filename}", "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
     # Llama a la función de desempaquetado después de guardar el archivo
    desempaquetar_archivo(UPLOADS_DIR+"/"+file.filename)
    return {"filename": file.filename}


def desempaquetar_archivo(file_path):
    
    with open(file_path, "rb") as file:
        buffer_data = file.read()
    
    msg = nistitl.Message()
    msg.parse(buffer_data)
    
      # --- Access type 1 record
    for record in msg.iter(1):
        print("Type1 content:\n",record)


    # --- Access type 2 record
    for record in msg.iter(2):
        print("Type2 content:\n",record)

    # --- Loop on all records of type 4
    i=0
    for r4 in msg.iter(4):
        
        i=i+1
        
        # Get all fields
        all_fields = r4.unpack("!BBBBBBBBHHB")
        imp = all_fields[0]
        fgp = list(all_fields[1:7])
        isr = all_fields[7]
        width = all_fields[8]
        height = all_fields[9]
        gca = all_fields[10]
        image = all_fields[11]        
        file_exists(UPLOADS_DIR+str(i)+".wsq")
        save_file_bytes(UPLOADS_DIR+str(i)+".wsq",image)
        
        img = Image.open(UPLOADS_DIR+str(i)+".wsq")   
        img = img.convert("1") 
        img.save(UPLOADS_DIR+str(i)+".bmp")
        #file.close()
        
        print(img)
        

    # --- Loop on all records of type 10
    i=0
    for r10 in msg.iter(10):
        i=i+1
        # Used pre-defined alias
        src = r10.SRC
        image = r10.DATA
        file_exists(UPLOADS_DIR+str(i)+".jpeg")
        save_file_bytes(UPLOADS_DIR+str(i)+".jpeg",image)
    
    print("Done")
    
def file_exists(file_path: str, default_content: str = None):
    if not os.path.exists(file_path):
        with open(file_path, "w") as file:
            if default_content:
                file.write(default_content)
            print(f"El archivo '{file_path}' ha sido creado.")
        return True
    else:
        print(f"El archivo '{file_path}' ya existe.")
        return False
    
def save_file_bytes(file_path: str, bytes_data: bytes):
    with open(file_path, "wb") as file:
        file.write(bytes_data)
    #b64_string = base64.b64encode(bytes_data).decode('utf-8')
    #print(b64_string)
    print(file_path)  # Solo imprime los datos por ahora, ajusta según lo que necesites hacer con ellos
 