from flask import Flask, request, send_file, render_template
from diffusers import (
    StableDiffusionPipeline,
    EulerDiscreteScheduler,
    StableDiffusionImg2ImgPipeline,
)
import torch
from PIL import Image

app = Flask(__name__, from io import BytesIO
import requests
from flask_cors import CORS
import openai
import os
template_folder="frontend", static_folder="frontend")
CORS(app, support_credentials=True)
openai.api_key = os.environ.get('OPENAI_API_KEY')


@app.route("/")
def index():
    return render_template("index.html")


@app.post("/gpt")
def request_gpt_question():
    data = request.json
    print(data)
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=data["prompt"]  # 直接使用请求中的数据作为messages参数
    )
    s = response['choices']
    # 获取第一个响应对象
    response_obj = s[0]
    # 获取 "content" 的值
    content = response_obj["message"]["content"]
    return content, 200



@app.post("/txt2img")
def text_to_img():
    data = request.json
    model_id = "runwayml/stable-diffusion-v1-5"
    output = "output_txt2img.png"

    scheduler = EulerDiscreteScheduler.from_pretrained(model_id, subfolder="scheduler")
    pipe = StableDiffusionPipeline.from_pretrained(
        model_id, scheduler=scheduler, revision="fp16", torch_dtype=torch.float16
    )
    pipe = pipe.to("cuda")
    image = \
        pipe(data["prompt"], guidance_scale=7.5, num_inference_steps=15, height=data["height"],
             width=data["width"]).images[
            0]

    image.save(output)
    return send_file(output), 200


@app.post("/img2img")
def img_to_img():
    data = request.json
    model_id = "runwayml/stable-diffusion-v1-5"
    output = "output_img2img.png"

    pipe = StableDiffusionImg2ImgPipeline.from_pretrained(
        model_id, torch_dtype=torch.float16
    )
    pipe = pipe.to("cuda")
    response = requests.get(data["url"])
    init_image = Image.open(BytesIO(response.content)).convert("RGB")
    init_image = init_image.resize((768, 512))
    images = pipe(
        prompt=data["prompt"], image=init_image, strength=0.75, guidance_scale=7.5
    ).images

    images[0].save(output)
    return send_file(output), 200


app.run(host='0.0.0.0', port=5000)
