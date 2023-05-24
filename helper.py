import random
import unicodedata


def limit_transcript_byte_length(text, byte_limit):
    utf8str = unicodedata.normalize("NFKD", text).encode("utf-8")
    byte_length = len(utf8str)

    if byte_length > byte_limit:
        ratio = byte_limit / byte_length
        new_text = text[: int(len(text) * ratio)]
        return new_text

    return text


def filter_half_randomly(arr):
    filtered_arr = []
    half_length = len(arr) // 2
    indices_to_filter = set()

    while len(indices_to_filter) < half_length:
        index = random.randint(0, len(arr) - 1)
        if index not in indices_to_filter:
            indices_to_filter.add(index)

    for i in range(len(arr)):
        if i not in indices_to_filter:
            filtered_arr.append(arr[i])

    return filtered_arr


def get_byte_length(text):
    utf8str = unicodedata.normalize("NFKD", text).encode("utf-8")
    byte_length = len(utf8str)
    return byte_length


def item_in_it(text_data, text):
    for t in text_data:
        if t.text == text:
            return True
    return False


def get_small_size_transcripts(new_text_data, old_text_data, byte_limit):
    sorted_text_data = sorted(new_text_data, key=lambda x: x.index)
    text = " ".join([t.text for t in sorted_text_data])
    byte_length = get_byte_length(text)

    if byte_length > byte_limit:
        filtered_data = filter_half_randomly(sorted_text_data)
        return get_small_size_transcripts(filtered_data, old_text_data, byte_limit)

    result_data = sorted_text_data[:]
    result_text = text
    last_byte_length = byte_length

    for obj in old_text_data:
        if item_in_it(new_text_data, obj.text):
            continue

        next_text_byte_length = get_byte_length(obj.text)
        is_over_limit = last_byte_length + next_text_byte_length > byte_limit

        if is_over_limit:
            over_rate = (
                last_byte_length + next_text_byte_length - byte_limit
            ) / next_text_byte_length
            chunked_text = obj.text[: int(len(obj.text) * over_rate)]
            result_data.append({"text": chunked_text, "index": obj.index})
        else:
            result_data.append(obj)

        result_text = " ".join(
            [t.text for t in sorted(result_data, key=lambda x: x.index)]
        )
        last_byte_length = get_byte_length(result_text)

    return result_text
