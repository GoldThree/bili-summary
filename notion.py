import requests, time

from section import sect


def bili_info(bvid):
    params = (("bvid", bvid),)
    response = requests.get(
        "https://api.bilibili.com/x/web-interface/view", params=params
    )
    return response.json()["data"]


def bili_tags(bvid):
    params = (("bvid", bvid),)

    response = requests.get(
        "https://api.bilibili.com/x/web-interface/view/detail/tag", params=params
    )
    data = response.json()["data"]
    if data:
        tags = [x["tag_name"] for x in data]
        if len(tags) > 5:
            tags = tags[:5]
    else:
        tags = []
    return tags


def insert2notion(token, database_id, bvid, summarized_text):
    headers = {
        "Notion-Version": "2022-06-28",
        "Authorization": "Bearer " + token,
    }
    info = bili_info(bvid)
    print(f'正在导入视频信息：{info["title"]}')
    tags = bili_tags(bvid)
    multi_select = []
    pubdate = time.strftime("%Y-%m-%d", time.localtime(info["pubdate"]))
    for each in tags:
        multi_select.append({"name": each})
    body = {
        "parent": {"type": "database_id", "database_id": database_id},
        "properties": {
            "标题": {"title": [{"type": "text", "text": {"content": info["title"]}}]},
            "URL": {"url": "https://www.bilibili.com/video/" + bvid},
            "UP主": {
                "rich_text": [
                    {"type": "text", "text": {"content": info["owner"]["name"]}}
                ]
            },
            "分区": {"select": {"name": sect[info["tid"]]["parent_name"]}},
            "tags": {"type": "multi_select", "multi_select": multi_select},
            "发布时间": {"date": {"start": pubdate, "end": None}},
            "观看时间": {
                "date": {
                    "start": time.strftime("%Y-%m-%d", time.localtime()),
                    "end": None,
                }
            },
            "封面": {
                "files": [
                    {"type": "external", "name": "封面", "external": {"url": info["pic"]}}
                ]
            },
        },
        "children": [
            {
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [{"type": "text", "text": {"content": "内容摘要："}}]
                },
            },
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {
                                "content": summarized_text,
                                "link": None,
                            },
                        }
                    ]
                },
            },
        ],
    }
    notion_request = requests.post(
        "https://api.notion.com/v1/pages", json=body, headers=headers
    )
    if str(notion_request.status_code) == "200":
        print("导入信息成功")
        return notion_request.json()["url"]
    else:
        print("导入失败，请检查Body字段")
        print(notion_request.text)
        return ""
