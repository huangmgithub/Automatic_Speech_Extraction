from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
import numpy as np
from numpy.linalg import norm

def tf_idf_similarity(docs):
    """
    TF-IDF计算文本相似度
    :param docs: 文本列表,内含两个文本
    :return:  numpy.ndarray
    """
    vectorizer = CountVectorizer()
    tf_idf_transformer = TfidfTransformer()
    tf_idf = tf_idf_transformer.fit_transform(vectorizer.fit_transform(docs))
    train_weight = tf_idf.toarray()

    return np.dot(train_weight[0], train_weight[1]) / (norm(train_weight[0]) * norm(train_weight[1]))

def compare_txt_similarity(s1, s2):
    """
    TF-IDF比较文本相似性
    :param s1:
    :param s2:
    :return:
    """
    l = []
    s1 = ' '.join(s1)
    s2 = ' '.join(s2)
    l.append(s1)
    l.append(s2)
    if tf_idf_similarity(l) > 0.8:
        return True
    return False

if __name__ == "__main__":
    train_sample = ['如果 一个 网页 被 很多 其他 网页 链接 说明 网页','如果 一个 网页 被 很多 其他 网页 链接 说明 网页 重要']
    print(tf_idf_similarity(train_sample))
