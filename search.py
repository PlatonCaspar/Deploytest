def value_search(search_word: str, value: str):  # returns a score for each given string

    score = 0
    search_word = search_word.lower()
    value = value.lower()
    search_words = search_word.split(' ')

    for w in search_words:

        if w in value:
            print(len(search_words))
            print("1. Krit +1")
            score += 1


    okay = True



        # adds 1 to score if words are in the same row
    start_count = 0 

    split_value = value.split(';')
    
    for v in split_value:

        if search_words[0] == v:
            start_count += 1
            break
        start_count +=1

    i = 1
    good = True
    while good and (i<len(search_words)) and (start_count<len(split_value)):

        if search_words[i] == split_value[start_count]:

            score+=1
            start_count+=1
        else:
            good = False
        
        i+=1

    return score

def sort_results(result):
    #sorted(result, reverse=True)
    return sorted(result, key=lambda r: r[1], reverse=True)

def search(search_word, items):
    results = []
    for i in items:
        score = value_search(search_word, i.reduce())
        print("score "+str(score) )
        print(i.reduce())
        if score > 0:
            results.append((i,score))
        print("RESULTS "+str(results))
    return [r[0] for r in sort_results(results)]
