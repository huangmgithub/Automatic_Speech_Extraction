def filter_news():
    """
    筛选出含"说"相近词的新闻
    """
    with open('../data/news.txt', 'r', encoding='utf-8') as f1, \
            open('../data/words.txt', 'r', encoding='utf-8') as f2:
                f_w = open('../data/filter_news.txt', 'w', encoding='utf-8')
                words = f2.read().split(' ')
                # print(words)
                for line in f1:
                    for word in words:
                        if word in line:
                            f_w.write(line + '\n')
                            break
                f_w.close()

if __name__ == "__main__":
    filter_news()