from flask import Flask
from flask import render_template
from flask import request
from flask import Response
import boto3
import chardet
import urllib
from os import path

app=Flask(__name__)

@app.route('/')
def hello_pybo():
    return render_template('Home.html')

@app.route('/SelectFile')
def select_file():
    return render_template('SelectFile.html')

@app.route('/UploadFile',methods=['POST'])
def upload_file():
    # SelectFile.html 페이지에서 전송버튼을 클릭했을때 method의 값이 POST
    if request.method == 'POST':
        # request.files['select'] : name 속성의 값이 select인 파일 선택 버튼에서 선택한 파일 정보를 리턴
        file = request.files['select']
        # 선택한 파일의 이름을 리턴
        print("선택한 파일 이름 =", file.filename)
        # 선택한 파일이 존재 한다면
        if file.filename != '':
            # 선택한 파일의 이름을 save_file에 대입
            save_file_name=file.filename
            # 중복 파일명에 붙일 번호
            count=1

            # temprory 폴더 안에 같은 이름이 있으면 True 리턴 하고 반북문 안의 내용 실행
            # 존재하지 않으면 False 반환하고 반복문 실행x
            while path.exists("./temporary/"+save_file_name):
                print(save_file_name+"은 이미 존재하는 파일")

                # 확장자가 있는 경우
                # ex) ["blog","txt"]
                if len( path.splitext(save_file_name))==2:
                    # 파일이름과 확장자에 따로 저장
                    file_name, ext=path.splitext(save_file_name)
                # 확장자 없는 경우
                else:
                    #file_name에 save_file_name 대입
                    file_name=save_file_name
                    ext=""
                    print("file_name = ",file_name)
                    print("ext = ",ext)

                # 같은 이름 파일이 존재하기 때문에 file_name에 str(count) 더하고 ext 붙여서 리턴
                save_file_name = file_name+str(count)+ext
                print("save_file_name = ",save_file_name)
                #count 1 증가시킨 뒤 반복
                count=count+1



            #file (SelectFile.html 에서 선택한 파일) 을 temporary 폴더에 save_file_name 파일명으로 임시 저장
            file.save("./temporary/"+save_file_name)
            #AWS 의 S3에 접속
            s3 = boto3.client('s3')

            # 첫번째 매개변수 : 로컬에서 올릴 파일이름 file.filename (업로드한 파일의 원래 이름)
            # 두번째 매개변수 : S3 버킷 이름 (본인의 버켓 이름을 입력할것)
            # 세번째 매개변수 : 버킷에 저장될 파일 이름. (업로드한 파일의 원래 이름)
            s3.upload_file("./temporary/"+save_file_name, "jes.04.07.bucket", save_file_name)
            return save_file_name + " 파일이 S3로 업로드 되었습니다"

    return "S3에 파일 업로드 실패!!"

# ViewFileList URL이 실행될때 아래의 함수실행
@app.route('/ViewFileList')
def view_file_list():
    # AWS 의 S3에 접속
    s3 = boto3.client('s3')
    # s3.get_paginator('list_objects_v2') : s3에 저장한 파일 리스트를 가져올 객체 생성해서 리턴
    paginator = s3.get_paginator('list_objects_v2')

    # paginator.paginate( Bucket='본인 S3버켓이름'  ) : s3 버켓에 업로드한 파일의 정보를 리턴 (Iterator 타입의 객체)
    #                                                한번에 50개 파일 정보씩 저장되 있음
    response_iterator = paginator.paginate(
                            Bucket='jes.04.07.bucket'
                            )
    # list(response_iterator) : S3 버켓에 저장된 파일의 정보가 저장된 response_iterator (Iterator 타입 객체) 를 list 객체로 변환
    #                          리스트에 파일정보는 50개씩 다음과 같이 저장되 있음
    #                         [
    #                            { "Contents": [파일1 정보, 파일2 정보, ..... 파일50정보] }, <== [0]
    #                            {"Contents": [파일 51정보, 파일 52정보 .... 파일 100정보] }, <== [1]
    #                         ...]
    file_list = list(response_iterator)
    print("="*100)
    print("file_list =", file_list)
    print("=" * 100)
    # file_list[0] : 맨처음 50개의 파일정보를 리턴 (리턴타입 Dictionary)
    # { "Contents": [파일1 정보, 파일2 정보, ..... 파일50정보] }, <== [0]
    print("file_list[0] =", file_list[0])
    print("=" * 100)
    # 파일 정보가 저장된 Contents 정보를 리턴
    print("file_list[0][Contents] =", file_list[0]["Contents"])
    print("=" * 100)
    # render_template('ViewFileList.html' : ViewFileList.html 을 실행
    # file_list=file_list[0]["Contents"] : ViewFileList.html 로
    #                                      업로드한 파일의 정보가 저장된 file_list[0]["Contents"] 를 전송
    return render_template('ViewFileList.html', file_list=file_list[0]["Contents"])


# @app.route('/DownLoadFile', : DownLoadFile URL이 실행될때 아래의 함수실행
# methods=['POST'] : input type="submit" 인 버튼을 클릭했을때 실행
@app.route('/DownLoadFile', methods=['POST'])
def download_file():
    # request.form['file_name'] : input name="file_name" 의 value 속성의 값 을 리턴
    #                            : 선택한 파일의 이름
    file_name = request.form['file_name']
    print("file_name =", file_name)
    print(file_name.encode('utf-8'))
    encode=file_name.encode('utf-8')
    remove_space=urllib.parse.quote(encode)
    print("="*100)

    # boto3.client('s3') : AWS s3 에 접속 하는 객체를 생성해서 리턴
    s3 = boto3.client('s3')
    # s3.get_object(Bucket='버켓이름', Key=file_name) : 버켓에서 파일명이 file_name 인 파일의 내용을 읽어올 객체를 생성해서 리턴
    # file : 버켓에서 파일명이 file_name 인 파일의 내용을 AWS s3 버켓에서 가져올 객체


    file = s3.get_object(Bucket='jes.04.07.bucket', Key=file_name)
    print("file = ", file)
    print("="*100)
    # file : AWS s3  버켓에서 파일명이 file_name 인 파일의 내용을 가져올 객체
    # file['Body'].read() : AWS s3 버켓에서 파일명이 file_name 인 파일의 내용 을 가져옴
    # headers={"Content-Disposition": "attachment;filename="+file_name} : 다운로드할 파일의 이름
    # Response( 웹브라우저로 전송할 내용) : 웹브라우저로 AWS s3 버켓에서 파일명이 file_name 인 파일의 내용을 전송 (파일 내용 다운로드 시작)
    body=file['Body'].read()
    return Response(
        body,
        headers={"Content-Disposition": "attachment;filename="+remove_space}
    )