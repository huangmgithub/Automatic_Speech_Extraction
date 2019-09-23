import os
from pyltp import SentenceSplitter, Segmentor, Postagger,NamedEntityRecognizer, Parser, SementicRoleLabeller

class LTP:
    def __init__(self, model_path):
        self.MODEL_PATH = model_path

    def sentence_split(self, string):
        """
        分句
        :param string: 传入字符串
        :return:
        """
        sentence  = SentenceSplitter.split(string)
        return sentence

    def word_split(self, string):
        """
        分词
        :param string: 传入字符串
        :param dic: 自定义字典，每行指定一个词，编码为utf-8
        :return:
        """
        cws_model = os.path.join(self.MODEL_PATH, 'cws.model')

        segmentor = Segmentor() # 初始化实例
        segmentor.load(cws_model) # 加载模型
        words = segmentor.segment(string) #分词
        segmentor.release()
        return list(words)

    def word_tag(self, words):
        """
        词性标注
        :param words: must be list contains words by word_split
        :return:
        """
        pos_model = os.path.join(self.MODEL_PATH, 'pos.model')

        postagger = Postagger() # 初始化实例
        postagger.load(pos_model) #加载模型

        postags = postagger.postag(words)
        postagger.release() # 释放模型

        # for word, pos in zip(words, postags):
        #     print(word, pos)
        return postags

    def name_entity_recognize(self, words, postags):
        """
        命名体识别
        :param words: must be list contains words by word_split
        :param postags: must be list contains postags by word_tag
        :return:
        """
        ner_model = os.path.join(self.MODEL_PATH, 'ner.model')

        recognizer = NamedEntityRecognizer() # 初始化实例
        recognizer.load(ner_model) # 加载模型

        nertags = recognizer.recognize(words, postags)
        recognizer.release() #释放模型
        return [(word, nertag) for word, nertag in zip(words, nertags)]

    def dependence_parse(self, words, postags):
        """
        依存句法分析
        :param words:
        :param postags:
        :return:
        """
        par_model = os.path.join(self.MODEL_PATH, 'parser.model') # 依存句法分析模型

        parser = Parser() # 初始化实例
        parser.load(par_model) # 加载模型
        arcs = parser.parse(words, postags) # 句法分析

        rely_id = [arc.head for arc in arcs] # 提取依存父节点id
        relation = [arc.relation for arc in arcs] # 提取依存关系
        heads = ['Root' if id == 0 else words[id- 1] for id in rely_id]

        # for i in range(len(words)):
        #     print(f'{relation[i]}->({words[i]},{heads[i]})')
        parser.release()

        return arcs, relation, heads

    def role_label(self, words, postags, arcs):
        """
        语义角色标注
        :param words:
        :param postags:
        :param arcs:
        :return:
        """
        srl_model = os.path.join(self.MODEL_PATH, 'pisrl_win.model')

        labeller = SementicRoleLabeller() # 初始化实例
        labeller.load(srl_model) # 加载模型

        roles = labeller.label(words, postags, arcs) # 语义角色标注

        for role in roles:
            print(role.index, "".join(
                ["{0}:({1},{2})".format(arg.name, arg.range.start, arg.range.end) for arg in role.arguments]
            ))
        labeller.release()

        return "roles{}".format(roles)



