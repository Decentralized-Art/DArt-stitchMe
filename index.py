from flask import Flask, request, jsonify
from flask_cors import CORS 
import cv2
import codecs
import imageio
import sys
import logging
import io
import info
import numpy as np
from PIL import Image
import requests, base64
import ipfsApi

api = ipfsApi.Client("http://127.0.0.1",5001)
logging.basicConfig(level=logging.DEBUG)

app  = Flask(__name__)
CORS(app)
app.secret_key = "moomoo"
app.config['CORS_HEADERS'] = 'Content-Type'
decoder = codecs.getdecoder("utf-8")

@app.route("/init",methods=["GET"])
def push_blank():
    if request.method=="GET":
        im = cv2.imread("blank.png")
        res = api.add('blank.png')
        hash = res["Hash"]
        url = "http://localhost:8080/ipfs/"+hash
        print (url)
        catted = imageio.imread(url)
        print (catted)
        return jsonify({"hash":str(res["Hash"])}),200

@app.route("/concat",methods=["POST","GET"])
def concat():
    if (request.method=="POST"):
        data = request.get_json(force=True)
        # print (data)
        hash = data["orig_hash"]
        new_image = data["new_img"][22:]
        print(new_image,file=sys.stdout)
        start = data["start"]
        end = data["end"]
        url = "http://localhost:8080/ipfs/"+hash
        img_orig = imageio.imread(url)
        img_sub = base64.urlsafe_b64decode(new_image)
        img_sub = Image.open(io.BytesIO(img_sub))
        img_sub = np.array(img_sub)

        print(img_orig.shape,file=sys.stdout)
        print(img_sub.shape,file=sys.stdout)
        print (start,end)
        width = end[0]-start[0]
        height = end[1]-start[1]
        for i in range(width):
            for j in range(height):
                img_orig[i+start[0]][j+start[1]][:3] = img_sub[i][j][:3]
        img_orig = cv2.cvtColor(img_orig, cv2.COLOR_BGR2RGB)
        cv2.imwrite("full_new.png",img_orig)
        res = api.add('full_new.png')
        final_hash = res["Hash"]
        print (final_hash)
        return jsonify({"hash":str(final_hash)}),200

# @app.route("/preNFT",methods=["POST"])
# def pin():
#     if (request.method=="POST"):
#         data = request.get_json(force=True)
#         hash = data["local_hash"]
#         url = "http://localhost:8080/ipfs/"+hash
#         img_orig = imageio.imread(url)
#         img_orig = cv2.cvtColor(img_orig, cv2.COLOR_BGR2RGB)
#         cv2.imwrite("preNFT.png",img_orig)
#         apikey = info.APIKey
#         apisecret = info.APISecret
#         headers = {
#             "Content-Type":"multipart/form-data",
#             "pinata_api_key":apikey,
#             "pinata_secret_api_key":apisecret
#         }


if __name__ == '__main__' :
    app.run(debug=True, port=5000)




