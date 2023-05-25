import requests
import openai

from typing import Optional
from reduce import reduce_bilibili_subtitle_timestamp
from helper import get_small_size_transcripts
from notion import insert2notion
from flask import Flask, Response, json, request
from openai_lib import chat

app = Flask(__name__)


def fetch_bilibili_subtitle_urls(video_id: str, page_number: Optional[str] = None):
    # sessdata = random.choice(os.getenv("BILIBILI_SESSION_TOKEN", "").split(","))
    cookie = "buvid3=77CF7CFB-87C9-043D-7FF4-6C6D80A248AF01522infoc; b_nut=1684418301; CURRENT_FNVAL=4048; _uuid=1EEC36105-4E2F-1258-4F54-B1223E13721C01094infoc; buvid_fp=7114c8245ed07125a8db8600de0430c5; buvid4=8CA8663F-62B5-76C8-3EEC-4E8CDF62D83790949-023050421-Rm82vYEdwpQdyzXhc72nfQ%3D%3D; rpdid=|(u||~kmuYkR0J'uY)RRu)J|R; i-wanna-go-back=-1; b_ut=7; b_lsid=6D736D510_1883848E61F; FEED_LIVE_VERSION=V8; header_theme_version=CLOSE; home_feed_column=5; browser_resolution=1920-944; SESSDATA=72adbe22%2C1700123510%2C2ed5f%2A51; bili_jct=e2ca1dfb3febcedea6e02a1ef21f5824; DedeUserID=230246944; DedeUserID__ckMd5=cb4f4d5a7c541414; nostalgia_conf=-1; bp_video_offset_230246944=797647715722854500; innersign=1; sid=6qp1zhn0"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36 Edg/113.0.1774.42",
        "Host": "api.bilibili.com",
        # "Cookie": f"SESSDATA={sessdata}",
        "Cookie": cookie,
    }
    common_config = {
        "method": "GET",
        "cache": "no-cache",
        "headers": headers,
        "referrerPolicy": "no-referrer",
    }

    # params = (
    #     f"?aid={video_id[2:]}" if video_id.startswith("av") else f"?bvid={video_id}"
    # )
    params = "?bvid=" + video_id
    request_url = f"https://api.bilibili.com/x/web-interface/view{params}"
    print("fetch", request_url)
    response = requests.get(request_url, headers=headers)
    json_data = response.json()

    # Support multiple parts of video
    if page_number:
        data = json_data.get("data", {})
        aid, pages = data.get("aid"), data.get("pages")
        cid = next(
            (page["cid"] for page in pages if page["page"] == int(page_number)), None
        )

        page_url = f"https://api.bilibili.com/x/player/v2?aid={aid}&cid={cid}"
        res = requests.get(page_url, **common_config)
        j = res.json()

        return {
            **json_data["data"],
            "subtitle": {"list": j["data"]["subtitle"]["subtitles"]},
        }

    return json_data["data"]


def fetch_bilibili_subtitle(
    video_id: str,
    page_number: Optional[str] = None,
    should_show_timestamp: Optional[bool] = False,
):
    res = fetch_bilibili_subtitle_urls(video_id, page_number)
    title, desc, dynamic, subtitle = (
        res.get("title"),
        res.get("desc"),
        res.get("dynamic"),
        res.get("subtitle"),
    )
    print(title, desc, dynamic, subtitle)
    has_description = bool(desc or dynamic)
    description_text = f"{desc} {dynamic}" if has_description else None
    subtitle_list = subtitle.get("list") if subtitle else None

    if not subtitle_list or len(subtitle_list) < 1:
        return {
            "title": title,
            "subtitlesArray": None,
            "descriptionText": description_text,
        }

    better_subtitle = next(
        (sub for sub in subtitle_list if sub["lan"] == "zh-CN"), subtitle_list[0]
    )
    subtitle_url = (
        f"https:{better_subtitle['subtitle_url']}"
        if better_subtitle["subtitle_url"].startswith("//")
        else better_subtitle["subtitle_url"]
    )
    print("subtitle_url", subtitle_url)

    subtitle_response = requests.get(subtitle_url)
    subtitles = subtitle_response.json()

    biliItems = [change_key(jsonObj) for jsonObj in subtitles["body"]]
    transcripts = reduce_bilibili_subtitle_timestamp(biliItems, should_show_timestamp)
    return {
        "title": title,
        "subtitlesArray": transcripts,
        "descriptionText": description_text,
    }


def change_key(jsonObj):
    jsonObj["from_"] = jsonObj.pop("from")
    return jsonObj


def segTranscipt(transcript):
    transcript = [
        {"text": item.text, "index": index, "timestamp": item.s}
        for index, item in enumerate(transcript)
    ]
    text = " ".join([x["text"] for x in sorted(transcript, key=lambda x: x["index"])])
    length = len(text)
    seg_length = 3500
    n = length // seg_length + 1
    print(f"视频文本共{length}字, 分为{n}部分进行摘要")
    division = len(transcript) // n
    new_l = [transcript[i * division : (i + 1) * division] for i in range(n)]
    segedTranscipt = [
        " ".join([x["text"] for x in sorted(j, key=lambda x: x["index"])])
        for j in new_l
    ]
    return segedTranscipt


def main():
    token = "secret_3xTmO920wGYoNyqD5rCDlOsAqLKfowmDSHCKHPxVW8e"
    database_id = "9297373ea0d9417d9e13dc73f894ec43"
    blink = input("请输入B站视频：")
    bvid = blink.split("/")[4]
    print(f"开始处理视频信息：{bvid}")
    prompt = "我希望你是一名专业的视频内容编辑，请你帮我将以下视频字幕文本的精华内容进行总结（字幕中可能有错别字，如果你发现了错别字请改正），在每句话的最前面加上时间戳，每句话开头只需要一个开始时间，然后以无序列表的方式返回，不要超过5条！并确保所有的句子都足够精简，清晰完整。"
    video_info = fetch_bilibili_subtitle(bvid)

    if video_info:
        print("字幕获取成功")
        subtitle_array = video_info["subtitlesArray"]
        # 自定义的压缩字幕
        # seged_text = get_small_size_transcripts(subtitle_array, subtitle_array, 6200)

        seged_text = segTranscipt(video_info["subtitlesArray"])
        # print(seged_text)
        summarized_text = ""
        i = 1
        for entry in seged_text:
            try:
                response = chat(prompt, entry)
                print(f"完成第{str(i)}部分摘要")
                i += 1
            except:
                print("GPT接口摘要失败, 请检查网络连接")
                response = "摘要失败"
            summarized_text += "\n" + response

        print(summarized_text)
        insert2notion(token, database_id, bvid, summarized_text)
    else:
        print("字幕获取失败")


@app.route("/health", methods=["GET"])
def health():
    resp = Response(
        json.dumps({"code": "2000", "message": "succeed", "data": {"key": "成功啦"}}),
        content_type="application/json",
    )
    return resp


@app.route("/api/summary/bilibili", methods=["GET"])
def bilibili_summary():
    token = "secret_3xTmO920wGYoNyqD5rCDlOsAqLKfowmDSHCKHPxVW8e"
    database_id = "9297373ea0d9417d9e13dc73f894ec43"
    blink = request.args.get("link")
    split_value = blink.split("/")
    if len(split_value) < 4:
        resp = Response(
            json.dumps({"code": "2001", "message": "错误的连接", "data": {}}),
            content_type="application/json",
        )
        return resp

    bvid = blink.split("/")[4]
    print(f"开始处理视频信息：{bvid}")
    prompt = "我希望你是一名专业的视频内容编辑，请你帮我将以下视频字幕文本的精华内容进行总结（字幕中可能有错别字，如果你发现了错别字请改正），在每句话的最前面加上时间戳，每句话开头只需要一个开始时间，然后以无序列表的方式返回，不要超过5条！并确保所有的句子都足够精简，清晰完整。"
    video_info = fetch_bilibili_subtitle(bvid)

    if video_info:
        print("字幕获取成功")
        # subtitle_array = video_info["subtitlesArray"]
        # 自定义的压缩字幕
        # seged_text = get_small_size_transcripts(subtitle_array, subtitle_array, 6200)

        seged_text = segTranscipt(video_info["subtitlesArray"])
        summarized_text = ""
        i = 1
        for entry in seged_text:
            try:
                response = chat(prompt, entry)
                print(f"完成第{str(i)}部分摘要")
                i += 1
            except:
                print("GPT接口摘要失败, 请检查网络连接")
                response = "摘要失败"
                resp = Response(
                    json.dumps({"code": "2001", "message": "错误的连接", "data": {}}),
                    content_type="application/json",
                )
                return resp

            summarized_text += "\n" + response
        print(summarized_text)
        insert2notion(token, database_id, bvid, summarized_text)
    else:
        print("字幕获取失败")


if __name__ == "__main__":
    app.run(port="8889")
    # main()
