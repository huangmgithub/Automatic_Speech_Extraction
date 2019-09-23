import pymysql,re,logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(lineno)d -  %(message)s')
logger = logging.getLogger(__name__)

def connect_db(host, port, user, password, db):
    """
    连接数据库并获取数据
    :param host: 主机
    :param port: 端口
    :param user: 用户名
    :param password: 密码
    :param db: 数据库名
    :return:
    """
    conn = pymysql.connect(host = host, port = port, user = user, password = password, db = db)# 数据库的链接
    cur = conn.cursor()# 获取一个游标
    cur.execute("select content from news_chinese")  # 具体的数据库操作语句
    contents = cur.fetchall()  # 将所有查询结果返回为元组
    cur.close()# 关闭游标
    conn.close() # 释放数据库资源
    return contents

def save(contents):
    """
    获取并保存新闻文本
    :param contents: News from db
    :return:
    """
    with open('../data/news.txt', 'w', encoding='utf-8') as f1:
        for content in contents:
            content = clean(content[0])
            logger.info('Start saving.......')
            f1.write(content + '\n')

def clean(s):
    """
    清洗数据
    :param s: 文本
    :return:
    """
    re_compile = re.compile(r'�|《|》|\/|）|（|【|】|\\n|\\r|\\t|\\u3000|;|\*')
    string = re_compile.sub('', str(s))
    return string


def get_and_save_news(host, port, user, password, db):
    """
    保存新闻
    :param host: 主机
    :param port: 端口
    :param user: 用户名
    :param password: 密码
    :param db: 数据库名
    :return:
    """
    news = connect_db(host, port, user, password, db)
    save(news)


if __name__ == "__main__":
    contents = get_and_save_news(host='rm-8vbwj6507z6465505ro.mysql.zhangbei.rds.aliyuncs.com',
                           port=3306, user='root', password='AI@2019@ai', db='stu_db')