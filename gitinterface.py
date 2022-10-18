import json
import io
from typing import Any
import requests as rq
import os
import base64
from PIL import Image
import sys
from inspect import currentframe, getframeinfo
import PySimpleGUI as sg
from sqlalchemy import values
from sympy import EX
from multiprocessing import Process

class GitApiParams:
    """
    just for params
    content - repo page
    """
    token: str
    content: dict
    downloadurl: str
    def __init__(
            self,
            url="",
            name="",
            token="",
            who_work_now="",
            who_work_now_mail="",
            fnames=[],
    ):
        self.url = url
        self.name = name
        self.token = token
        self.who_work_now = who_work_now
        self.who_work_now_mail = who_work_now_mail
        self.fnames = fnames
        self.content = load_git_content(self)
        self.downloadurl = self.content.get("dirs")
        self.downloadurl = ''.join(self.downloadurl)

    def __str__(self):
        return (
            f"Url: {self.url} \n"
            f"Username: {self.name} \n"
            f"Who_work_now_commit_info: {self.who_work_now} \n"
            f"Who_work_now_mail_commit_info: {self.who_work_now_mail} \n"
            f"Pictures in raw_pic: {self.fnames} \n"
            f"Content on git: {self.content} \n"
            f"Download url: {self.downloadurl} \n"
        )


def setup():
    try:
        f = open("config.json")
        config = json.load(f)

        workspace = GitApiParams(
            config.get("url"),
            config.get("name"),
            config.get("token"),
            config.get("who_work_now"),
            config.get("who_work_now_mail"),
            find_fls(""),
        )
        return workspace

    except Exception as e:
        print(e)
        exit()

def open_cpp_prog():
    try:
        os.startfile("DatasetCollector_.exe")
    except Exception as e:
        print(e)

def file_to_base64(fname: str):
    """
    переводит файл в base64
    """
    try:
        with open(fname, "rb") as file:
            base64_file = base64.b64encode(file.read())
        return base64_file.decode("utf-8")
    except Exception as e:
        print(e)
        
def find_fls(std_ext=".jpg", std_dir="raw_pic"):
    """
    Ищет в std_dir файлы расширения jpg, можно менять
    и возвращает список flist
    """
    if std_ext != "":
        flist = []
        for file in os.listdir(std_dir):
            if file.endswith(std_ext):
                flist.append(os.path.join(std_dir, file))
        return flist
    else:
        flist = []
        for file in os.listdir(std_dir):
            flist.append(os.path.join(std_dir, file))
        return flist

def download_files(url, val=0):
    """
    image_file_path - path to save of file
    url - ссылка на директорию где нужно качать
    val - количество файлов,если  = 1, то качает первый файл в директории
    если = 0 то качает все
    """
    if val == 1:
        r = rq.get(url)
        if r.status_code != rq.codes.ok:
            assert False, "Status code error: {}.".format(r.status_code)
        r = r.json()
        fls_link_to_download = []
        for i in r:
            fls_link_to_download.append(
                {"name": i.get("path"), "download_url": i.get("download_url")}
            )
            break
        r = rq.get(fls_link_to_download[0].get("download_url"))
        try:
            with Image.open(io.BytesIO(r.content)) as im:
                im = im.convert("RGB")
                im.save(fls_link_to_download[0].get("name"))
                print(f"Downloaded: {i.get('name')}")
        except Exception:
            with open(fls_link_to_download[0].get("name"), "wb") as f:
                f.write(r.content)
            print(f"Downloaded: {i.get('name')}")

    elif val == 0:
        r = rq.get(url)
        count = 1
        if r.status_code != rq.codes.ok:
            assert False, "Status code error: {}.".format(r.status_code)
        r = r.json()
        fls_link_to_download = []
        for i in r:
            fls_link_to_download.append(
                {"name": i.get("path"), "download_url": i.get("download_url")}
            )
        for i in fls_link_to_download:
            r = rq.get(i.get("download_url"))
            try:
                with Image.open(io.BytesIO(r.content)) as im:
                    im = im.convert("RGB")
                    im.save(i.get("name"))
                    print(f"Downloaded: {i.get('name')}")
                    count += 1
            except Exception:
                with open(i.get("name"), "wb") as f:
                    f.write(r.content)
                print(f"Downloaded: {i.get('name')}")

def reupload(url, fname, name, token, who_work_now, who_work_now_mail):
    try:
        fields = {
            "message": f"commit from upload_by_name({fname})",
            "committer": {
                "name": who_work_now,
                "email": who_work_now_mail,
            },
            "content": file_to_base64(fname),
            "sha": str(rq.get(url, auth=(name, token)).json().get("sha")),
        }
        f_resp = rq.put(
            url,
            auth=(name, token),
            headers={"Content-Type": "application/json"},
            data=json.dumps(fields),
        )
        if f_resp.ok:
            print(f"Uploaded {fname} to {url}")
        else:
            print(fname)
            print(f_resp.status_code)
    except Exception as e:
        print(e)
        

def upload(env: GitApiParams, mode=0):
    """
    upload - с помощью put запроса начинает отправлять все,
    что находится в env.fnames
    mode 0 - upload all
    mode от 1 до n - upload первые n файлов в env.fnames
     return 409 - Если файл уже лежит на гите
    422 - ошибка
    Если успешно - выводит сообщение об этом
    """
    try:
        if mode == 0:
            for fname in env.fnames:
                url = env.url + "/" + fname  # makes dir if fname has dir
                fields = {
                    "message": "commit from upload()",
                    "committer": {
                        "name": env.who_work_now,
                        "email": env.who_work_now_mail,
                    },
                    "content": file_to_base64(fname),
                    "sha": "",
                }
                f_resp = rq.put(
                    url,
                    auth=(env.name, env.token),
                    headers={"Content-Type": "application/json"},
                    data=json.dumps(fields),
                )
                if f_resp.ok:
                    print(f"Uploaded {fname} to {url}")
                elif f_resp.status_code == 409:  # 409 - file already exist
                    reupload(
                        url,
                        fname,
                        env.name,
                        env.token,
                        env.who_work_now,
                        env.who_work_now_mail,
                    )
                else:
                    print(fname)
                    print(f_resp.status_code)
        else:
            count = 0
            for fname in env.fnames:
                if count < mode:
                    count += 1
                    url = env.url + "/" + fname  # makes dir if fname has dir
                    fields = {
                        "message": "commit from upload()",
                        "committer": {
                            "name": env.who_work_now,
                            "email": env.who_work_now_mail,
                        },
                        "content": file_to_base64(fname),
                        "sha": "",
                    }

                    f_resp = rq.put(
                        url,
                        auth=(env.name, env.token),
                        headers={"Content-Type": "application/json"},
                        data=json.dumps(fields),
                    )
                    if f_resp.ok:
                        print(f"Uploaded {fname} to {url}")
                    elif f_resp.status_code == 409:
                        reupload(
                            url,
                            fname,
                            env.name,
                            env.token,
                            env.who_work_now,
                            env.who_work_now_mail,
                        )
                    else:
                        # 409 - file already exist
                        print(fname)
                        print(f_resp.status_code)
                else:
                    break
    except Exception as e:
        print(e)

def upload_by_name(env: GitApiParams, name):
    """
    все предельно просто, тоже самое что и upload,но добавляет
    только один файл с названием name
    """
    try:
        search = next((fname for fname in env.fnames if fname == name), "")
        if search == "":
            print(f"Not found: {name}")
            return
        else:
            fname = search
            url = env.url + "/" + fname  # makes dir if fname has dir
            fields = {
                "message": "commit from upload()",
                "committer": {"name": env.who_work_now, "email": env.who_work_now_mail},
                "content": file_to_base64(fname),
                "sha": "",
            }

            f_resp = rq.put(
                url,
                auth=(env.name, env.token),
                headers={"Content-Type": "application/json"},
                data=json.dumps(fields),
            )
            if f_resp.ok:
                print(f"Uploaded {fname} to {url}")
            elif f_resp.status_code == 409:
                reupload(
                    url,
                    fname,
                    env.name,
                    env.token,
                    env.who_work_now,
                    env.who_work_now_mail,
                )
            else:
                print(fname)
                print(f_resp.status_code)
    except Exception as e:
        print(e)

def add(params:GitApiParams) -> None:
    """
    Простой вызывает upload
    использовать:
    add(env,val- сколько файлов добавить)
    """
    try:
        return upload(params, 0)
    except Exception as e:
      print(e)

def add_by_name(params:GitApiParams, name:str) -> None:
    """
    все очень просто
    вызывает upload_by_name, нужно только задать имя файла которое
    нужно загрузить
    """
    try:
        if name not in params.fnames:
            params.fnames.append(name)
        upload_by_name(params, name)
    except Exception as e:
        print(e)

def load_git_content(env):
    """
    load_git_content - обновляет контент на текущей env.url, автоматический парсит
    все данные при первом объявлении объекта класса
    Дальнейшее использование:
    env.content = load_git_content(env)
    __files - файлы в текущей директории гита
    __dirs - директории
    """
    try:
        __files = []
        __dirs = []
        content = {"files": __files, "dirs": __dirs}
        req = rq.get(env.url, auth=(env.name, env.token))
        for i in req.json():
            if i.get("type") == "file":
                __files.append(i.get("name"))
                content.update({"files": __files})

            elif i.get("type") == "dir":
                __dirs.append(i.get("url"))
                content.update({"dirs": __dirs})
        return content
    except Exception as e:
        print(e)

def start(env: Any):
    try:
        cpp_proc = Process(target=open_cpp_prog)
        cpp_proc.start()

        env = setup()
        
        sg.theme('DarkAmber')   
        layout = [ [sg.Text('Name of file'), sg.InputText()], 
                [sg.Button("Upload"),sg.Button("Download"),sg.Button('Close')] ]
        window = sg.Window('Dataset control', layout)
        while True:
            event,values = window.read()
            print(type(values))
            if event == sg.WIN_CLOSED or event == 'Close': 
                break
            elif event == "Upload":
                print(f"upload")
                #add(env)
            elif event == "Download":
                print("download")
                #download_files(env.downloadurl)
            elif event == "Upload" and values.get('0') != '':
                print(f"upload {values[0]}")
                #add_by_name(env,values[0])
        
        cpp_proc.join()
        window.close()
    except Exception as e:
        print(e)
