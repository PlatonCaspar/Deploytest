def value_search(search_word: str, value: str):  # returns a score for each given string

    score = 0
    search_word = search_word.lower()
    value = value.lower()
    if "&" in search_word:
        for s_word in search_word.split("&"):
            if s_word is "":
                continue
            res = value_search(s_word.strip("&"), value)
            if res is 0:
                return 0
            else:
                score += res

    search_words = search_word.split()
    okay = True

    # adds 1 to score if words are in the same row
    start_count = 0

    split_value = value.split(';')
    for w in search_words:
        if w in value:
            score+=1
    for v in split_value:
        # print(str(search_word in v)+" "+search_word+" in "+v)
        for w in search_words:
            score += check_property(w, v)
        if search_words[0] == v:
            score += 1
            start_count += 1
            break
        if search_word in v:
            score += 1
        start_count += 1

    i = 1
    good = True
    while good and (i < len(search_words)) and (start_count < len(split_value)):

        if search_words[i] == split_value[start_count]:

            score += 1
            start_count += 1
        else:
            good = False

        i += 1

    return score


def sort_results(result):
    # sorted(result, reverse=True)
    return sorted(result, key=lambda r: r[1], reverse=True)


def search(search_word, items):
    results = []
    for i in items:
        score = value_search(search_word, i.reduce())
        if score > 0:
            results.append((i, score))
    return [r[0] for r in sort_results(results)]


def check_property(search_word, value):
    score = 0
    if ":" not in value or ":" not in search_word:
        return 0
    search_property = search_word.split(":")[0]
    search_values = search_word.split(":")[1]
    # if search_property not in value:
    #     return 0
    value_property = value.split(":")[0]
    if value_property != search_property:
        return 0
    values = value.split(":")[1]
    try:
        values = float(values)
    except Exception as e:
        print(e)
    for s_val in search_values.split(","):
        try:
            s_val = float(s_val)
            print(s_val)
            print(values)
        except Exception as e:
            print(e)
        if s_val == values:
            score += 1
        else:
            return 0

    return score
