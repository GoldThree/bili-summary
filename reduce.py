from typing import List, TypeVar


T = TypeVar("T")


class CommonSubtitleItem:
    index = 0
    s = 0.0
    text = ""


class YoutubeSubtitleItem:
    def __init__(self, start: float, lines: List[str]):
        self.start = start
        self.lines = lines


class BilibiliSubtitleItem:
    def __init__(self, from_: float, content: str):
        self.from_ = from_
        self.content = content


def reduce_youtube_subtitle_timestamp(
    subtitles: List[YoutubeSubtitleItem] = [],
) -> List[CommonSubtitleItem]:
    return reduce_subtitle_timestamp(
        subtitles, lambda i: i.start, lambda i: " ".join(i.lines), True
    )


def reduce_bilibili_subtitle_timestamp(
    subtitles: List[BilibiliSubtitleItem] = [], should_show_timestamp: bool = False
) -> List[CommonSubtitleItem]:
    return reduce_subtitle_timestamp(subtitles, should_show_timestamp)


def reduce_subtitle_timestamp(
    subtitles: List[BilibiliSubtitleItem],
    should_show_timestamp=False,
) -> List[CommonSubtitleItem]:
    TOTAL_GROUP_COUNT = 30
    MINIMUM_COUNT_ONE_GROUP = 7

    # each_group_count = (
    #     subtitles.length / TOTAL_GROUP_COUNT
    #     if len(subtitles) > TOTAL_GROUP_COUNT
    #     else MINIMUM_COUNT_ONE_GROUP
    # )

    accumulator = []
    for index, current in enumerate(subtitles):
        group_index = index // MINIMUM_COUNT_ONE_GROUP

        start = current["from_"]
        content = current["content"]
        if len(accumulator) <= group_index:
            accumulator.append(CommonSubtitleItem())
            accumulator[group_index].index = group_index
            accumulator[group_index].s = start
            accumulator[group_index].text = (
                f"{start} - " if should_show_timestamp else ""
            )

        accumulator[group_index].text += f"{content} "

    return accumulator
