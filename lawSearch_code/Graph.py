from py2neo import *
import re
import Db_Operation


# 连接数据库
opt = {
    'host': '输入主机名', 'user': 'root', 'password': '输入密码',
    'port': 3300, 'database': 'intelligence', 'charset': ''}
db = Db_Operation.connect(opt)
# 数据库查询语言 获取法规所有信息 准备入eno4j库
result = Db_Operation.Query(db, "SELECT * FROM intelligence.legal")

# 连接eno4j图数据库 获取 graph 待用
graph = Graph('http://localhost:7474', auth=('neo4j', '780815'))


# ======== 创建第一个节点，标签为《label1 = "法规"》，《attr》为其各个属性，节点名为《a》 =========================================
label1 = "法规"
for legal in result:
    attr1 = {"name": legal[3]}
    attr2 = {"message_type": legal[1]}
    attr3 = {"pstage": legal[2]}
    attr4 = {"graph_dic": legal[4]}
    attr5 = {"text_dic": legal[5]}
    attr6 = {"url": legal[6]}
    attr7 = {"region": legal[8]}
    attr8 = {"keyword": legal[10]}
    attr9 = {"remarks": legal[9]}
    attr10 = {"id": legal[0]}
    a = Node(label1, **attr1, **attr2, **attr3, **attr4, **attr5, **attr6,
             **attr7, **attr8, **attr9, **attr10)
    graph.create(a)
# ======== 创建第一个节点，标签为《label1 = "法规"》，《attr》为其各个属性，节点名为《a》 =========================================


print("第一节点创建完毕")


# ======== 创建第二个节点，标签为《label2 = "地区"》，《attr》为其各个属性，节点名为《b》 =========================================
label2 = "地区"
city_list = []
for city in result:
    if (city[8] not in city_list):  # 去重
        attr1 = {"name": city[8]}
        b = Node(label2, **attr1)
        graph.create(b)
        city_list.append(city[8])
# ======== 创建第二个节点，标签为《label2 = "地区"》，《attr》为其各个属性，节点名为《b》 =========================================


print("第二个节点创建完毕")


# ======== 创建第三个节点，标签为《label3 = "法规类别"》，《attr》为其各个属性，节点名为《c》 ======================================
type_list = [0, 1, 2]
typename_list = ['法律', '条例', '其他法律']
label3 = "法规类别"
for i in type_list:
    attr1 = {"name": typename_list[i]}
    attr2 = {"id": i}
    c = Node(label3, **attr1, **attr2)
    graph.create(c)
# ======== 创建第三个节点，标签为《label3 = "法规类别"》，《attr》为其各个属性，节点名为《c》 ======================================


print("第三个节点创建完毕")


# ======== 创建第四个节点，标签为《label4 = "项目实施阶段"》，《attr》为其各个属性，节点名为《d》 ===================================
project_satge_list = ['项目前期阶段（变电）']
label4 = "项目实施阶段"
for i in range(len(project_satge_list)):
    attr1 = {"name": project_satge_list[i]}
    d = Node(label4, **attr1)
    graph.create(d)
# ======== 创建第四个节点，标签为《label4 = "项目实施阶段"》，《attr》为其各个属性，节点名为《d》 ===================================


print("第四个节点创建完毕")


# ======== 创建第五个节点，标签为《label5 = "关键词"》，《attr》为其各个属性，节点名为《e》 ========================================
label5 = "关键词"
keywords_list = []
for keyword1 in result:
    line = re.split(r',', keyword1[10])
    for keyword2 in line:
        if keyword2 not in keywords_list:
            keywords_list.append(keyword2)

for i in keywords_list:
    attr1 = {"name": i}
    e = Node(label5, **attr1)
    graph.create(e)
# ======== 创建第五个节点，标签为《label5 = "关键词"》，《attr》为其各个属性，节点名为《e》 ========================================


print("第五个节点创建完毕")


# ======================================== 查找节点并创建对应关系 ==========================================================
for i in range(len(result)):
    print('正在创建第', i + 1, '条法规的关系')
    # 找出第一个标签为“法规”id为1的节点
    nodeLaw = graph.nodes.match("法规", id=i + 1).first()

    # 找出第一个标签为“地区”name为第一个节点region属性的节点
    nodeReg = graph.nodes.match("地区", name=nodeLaw["region"]).first()
    # 第一个节点和第二个节点创建关系
    nodeLaw2nodeReg = Relationship(nodeLaw, "所在地", nodeReg)
    graph.create(nodeLaw2nodeReg)

    # 找出第一个标签为“法规类别”id为第一个节点message_type属性的节点
    nodeLawType = graph.nodes.match("法规类别", id=nodeLaw["message_type"]).first()
    # 第一个节点和第三个节点创建关系
    nodeLaw2nodeLawType = Relationship(nodeLaw, "归类为", nodeLawType)
    graph.create(nodeLaw2nodeLawType)

    # 找出第一个标签为“项目实施阶段”name为第一个节点pstage属性的节点
    nodeStage = graph.nodes.match("项目实施阶段", name=nodeLaw["pstage"]).first()
    # 第一个节点和第四个节点创建关系
    nodeLaw2nodeStage = Relationship(nodeLaw, "项目阶段", nodeStage)
    graph.create(nodeLaw2nodeStage)

    # 循环关键词列表
    for j in keywords_list:
        # 循环第一个节点属性为 keyword 的字符串
        if j in nodeLaw["keyword"]:
            # 找出第一个标签为“关键词”name为j的节点
            nodeKey = graph.nodes.match("关键词", name=j).first()
            # 第一个节点和第五个节点创建关系
            nodeLaw2nodeKey = Relationship(nodeLaw, "包含关键词", nodeKey)
            graph.create(nodeLaw2nodeKey)
    print('创建第', i + 1, '条法规的关系完毕')
# ======================================== 查找节点并创建对应关系 ==========================================================


print("关系创建完毕")
print("入库完毕~")
