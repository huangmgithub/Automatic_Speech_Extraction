import logging
import os,re
from pyltp import Segmentor, Postagger,NamedEntityRecognizer, Parser, SementicRoleLabeller
from gensim.models import Word2Vec

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(lineno)d -  %(message)s')
logger = logging.getLogger(__name__)

# 文件目录
BASE_DIR = './data'
LTP_MODEL_DIR = './model/ltp_data_v3.4.0'
WORD2VEC_MODEL_DIR = "./model/wiki_news"


class Speech_Extractor:
    def __init__(self,
                 cws_model_path,
                 pos_model_path,
                 ner_model_path,
                 parser_model_path,
                 srl_model_path):

        # 加载ltp模型
        self.segmentor = Segmentor()  # 分词
        self.segmentor.load(cws_model_path)
        self.postagger = Postagger()  # 词性标注
        self.postagger.load(pos_model_path)
        self.recognizer = NamedEntityRecognizer() # 命名实体识别
        self.recognizer.load(ner_model_path)
        self.parser = Parser() # 依存句法分析
        self.parser.load(parser_model_path)
        self.labeller = SementicRoleLabeller() # 语义角色标注
        self.labeller.load(srl_model_path)



    def release(self):
        """
        释放模型
        :return:
        """
        self.segmentor.release()
        self.postagger.release()
        self.recognizer.release()
        self.parser.release()
        self.labeller.release()


    def process(self, news):
        """
        ltp处理新闻数据
        :param news:
        :return:
        """
        words = list(self.segmentor.segment(news))
        # 词性标注
        postags = list(self.postagger.postag(words))
        # 命名实体识别
        nertags = list(self.recognizer.recognize(words, postags))
        # 依存句法分析
        arcs = self.parser.parse(words, postags)  # 句法分析

        rely_id = [arc.head for arc in arcs]  # 提取依存父节点id
        relation = [arc.relation for arc in arcs]  # 提取依存关系
        heads = ['Root' if id == 0 else words[id - 1] for id in rely_id]

        return arcs, relation, words, nertags, postags

    def extract(self, news, says, f_w=None):
        """
        抽取新闻观点
        :param news:
        :param says:
        :param f_w:
        :return:
        """
        res = []

        arcs, relation, words, nertags, postags = self.process(news)

        for i, arc in enumerate(arcs):
            # 主语
            subject = ""
            # 谓语
            predicate = ""
            # 观点
            view = []

            p = arc.head - 1 # 谓语的位置
            if arc.relation == "SBV" and words[p] in says:
                print("%s(%s,%s)" % (arc.relation, words[i], words[p]))
                predicate = words[p]
                # 主语
                # 若主语是代词，需要找到主体
                if postags[i] == "r":
                    flag = False
                    # 向前找主语
                    for j in range(i, 0, -1):
                        if nertags[j] != "O": # O表示不构成主体
                            # 找出主体的定语
                            flag = True
                            if arcs[j].relation == "ATT": # 定中关系
                                subject = words[j] + words[arcs[j].head - 1] # 定语和主语
                            else:
                                subject = words[j]
                            break

                    if not flag:
                        # 向后找主语
                        for j in range(i ,len(words)):
                            if nertags[j] != "O":
                                # 找出主体的定语
                                flag = True
                                if arcs[j].relation == "ATT": # 定中关系
                                    subject = words[j] + words[arcs[j].head - 1]
                                else:
                                    subject = words[j]
                                break

                    # 找不到就用代词
                    if not flag:
                        subject = words[i]

                if postags[i].startswith("n"):
                    subject = words[i]

                print(words[i], postags[i], nertags[i])
                # if nertags[i] != "O" and postags[i].startswith("n"):
                #     subject = words[i]

                # 观点
                start = 0
                end = 0
                if words[p+1] in [':','：']: # 谓词后面为冒号
                    end = start = p + 3
                    while end < len(words):
                        if words[end] in ['”','’', '"']:
                            break
                        end += 1
                    view = words[start:end]
                elif words[p+1] in [",", "，"]: # 谓词后面为逗号
                    end = start = p + 2
                    while end < len(words):
                        if words[end] in ['.','。','!','！', '；']:
                            break
                        end += 1
                    view = words[start:end]
                else: # 取谓语前面的句子，一般搜索引号
                    end = p - 1
                    while end >=0 and words[end] not in ['”','’', '"']:
                         end -= 1
                    start = end
                    while start >= 0 and words[start] not in ['‘',"“", '"']:
                        start -= 1
                    view = words[start+1:end] if 0 <= start <= end < len(words) else ""

            # 是否成功抽取
            if not all([subject, predicate, view]):
                continue
            else:
                logger.info("找到符合的===> {0} ：{1} : {2}".format(subject, predicate, view))
                if '。' in subject:
                    subject = re.sub(r'(。|\s+)', '', subject)  # 去掉S中误匹配的。

                res.append((subject, predicate, ''.join(view)))  # 待返回内容
                if f_w:
                    logger.info("写入ing")
                    f_w.write("{0} {1} {2}".format(subject, predicate, ''.join(view)) + '\n')
        return res


if __name__ == "__main__":

    # 获取ltp模型文件名
    cws_model_path = os.path.join(LTP_MODEL_DIR, "cws.model")
    pos_model_path = os.path.join(LTP_MODEL_DIR, "pos.model")
    ner_model_path = os.path.join(LTP_MODEL_DIR, "ner.model")
    parser_model_path = os.path.join(LTP_MODEL_DIR, "parser.model")
    srl_model_path = os.path.join(LTP_MODEL_DIR, "pisrl_win.model")
    # word_vec_path = os.path.join(WORD2VEC_MODEL_DIR, "wiki.zh.model")

    # 实例化抽取类
    speech_extractor = Speech_Extractor(cws_model_path,
                                        pos_model_path,
                                        ner_model_path,
                                        parser_model_path,
                                        srl_model_path)

    # 获得与说相近的词 f1
    # 新闻存储文本
    # 创建txt文件保存结果 f_w
    with open(os.path.join(BASE_DIR, 'words.txt'), 'r', encoding='utf-8') as f1, \
            open(os.path.join(BASE_DIR, 'filter_news.txt'), 'r', encoding='utf-8') as f2, \
            open(os.path.join(BASE_DIR, 'result.txt'), 'w', encoding='utf-8') as f_w:

        # 获得与“说”相近的词列表
        says = f1.read().split(' ')

        # 遍历处理每条新闻
        for news in f2:
            if len(news) < 200:
                result = speech_extractor.extract(news, says, f_w)


    # 释放模型
    speech_extractor.release()







