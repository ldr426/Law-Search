# 载入需要的模块
import jieba
import Db_Operation


# 判断是否是非汉语词汇 如果是则返回false
def is_Chinese(word ):
    for ch in word:
        if '\u4e00' <= ch <= '\u9fff':
            return True
    return False

# 进行词频统计并返回排好序的列表
def statistics(result):
    # 将数组转化为字符串
    r_str = result.__str__()
    # 判断是否转化成功
    #print(type(r_str))

    # 使用精确模式对文本进行分词 返回的是一个列表
    words = jieba.lcut(r_str)
    # 创建空的字典 通过键值对的形式存储词语及其出现的次数
    counts = {}
    # 遍历列表来运算词语出现的频率
    for word in words:
        # 单个词语内和非汉语词汇不计算在内
        if len(word) == 1 or is_Chinese(word) == False:
            continue
        # 遍历所有词语，每出现一次其对应的值加 1
        else:
            counts[word] = counts.get(word, 0) + 1
    # 通过item()方法把字典中每对key和value组成一个元组，并把这些元组放在列表中
    items = list(counts.items())
    # 根据词语出现的次数进行从大到小排序 隐函数 通过第二个元素排序
    items.sort(key=lambda x: x[1], reverse=True)
    return items


# 函数主体从这里开始
# 连接数据库
opt = {
    'host': 'localhost', 'user': 'root', 'password': '输入密码',
    'port': 3306, 'database': 'test', 'charset': ''}
db = Db_Operation.connect(opt)
# 数据库查询语言 筛选出需要进行词频统计的内容存入数组result 并关闭数据库连接
result = Db_Operation.Query(db, "SELECT remarks FROM test.legal")


# 返回的是一个数组
_list = statistics(result)

# 列出前50个出现次数最高的关键词

for i in range(60):
    word, count = _list[i]
    print("{0:<5}{1:>5}".format(word, count))
