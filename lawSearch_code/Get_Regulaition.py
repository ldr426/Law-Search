# 载入需要的模块
import codecs
import os
import random
import re
import string
import sys
import urllib.parse
import PyPDF2 as PyPDF2
import jieba
import pdfkit
import qrcode
import requests
from bs4 import BeautifulSoup
import Db_Operation

# 应输入当前数据库的最后一个主键的值 对应 legal 表主键 id 也是 item 表外键 id 记录多少个法规
count = 51
# 法规爬取关键字列表
name_list = ['土地', '保护', '电力', '使用权', '登记', '森林', '公路',
             '建设', '赔偿', '行政', '事故', '林木', '航道', '监督管理']
# 法规分类 0 为法律 1 为条例 2 为其他法规
message_type = 0


# ①判断法规类型
def regulaotion_type(str1):
    if selStr(str1, '法'):
        return 0
    elif selStr(str1, '条例'):
        return 1
    else:
        return 2


# ②url转二维码图片的函数
def url_to_png(url_to_png):
    # 调用 qrcode 生成二维码
    img = qrcode.make(url_to_png)
    # 保存到指定目录下
    img.save("D:\App\PyCharm\PyCharm_Project\data\png\ " + str(count) + ".png")


# ③过滤多余字符串函数
def _filter(content):
    # 将字符串分割再重组，这时候空白字符就会被pass掉了，
    # 不过该方法杀伤力太大，会导致所有空白消失，一定要慎用。
    return "".join(content.split())


# ④法规分条函数 返回值是存放法规条目的一个列表
def _split(content):
    # 根据"第"*"条"拆分字符串
    # 确认传入的是正确的
    # print(content)
    # 正则表达式编译成 Pattern 对象
    pattern = re.compile(r'第.{1,2}条')
    # 该列表用来存放拆分的法规
    item_list = []
    # 先过滤多余字符再按照要求拆分成多个字符串放入列表result
    result = pattern.split(_filter(content))
    # 加字段并形成完整的分条并放入item_list列表
    for i in range(1, int(len(result)) - 1):
        item_list.append("第" + str(i) + "条 " + result[i])
    # 检查是否拆分并赋值成功
    # for i in range(len(item_list)):
    #    print(item_list[i])
    return item_list


# ⑤合并pdf的函数
def merge_pdf():
    # 建立一个装pdf文件的数组
    pdf_list = os.listdir("D:\\App\\PyCharm\\PyCharm_Project\\data\\one\\")
    # 以数字进行排序（数组中的排列顺序默认是以ASCII码排序，当以数字进行排序时会不成功）
    file_list = sorted(pdf_list, key=lambda d: int(d.split(".pdf")[0]))
    # 生成一个空白的PDF文件 初始化一个 PdfFileReader 对象
    pdf = PyPDF2.PdfFileWriter()
    for item in file_list:
        # 进入D:\App\PyCharm\PyCharm_Project\data\one目录，该目录为存放需要合并的pdf的目录
        os.chdir("D:\\App\\PyCharm\\PyCharm_Project\\data\\one\\")
        # 以只读方式依次打开pdf文件
        fd = open(item, "rb")
        pdfreader = PyPDF2.PdfFileReader(fd)
        for pages in range(pdfreader.numPages):
            # 将打开的pdf文件内容一页一页的复制到新建的空白pdf里
            pdf.addPage(pdfreader.getPage(pages))
        # 进入D:\App\PyCharm\PyCharm_Project\data\pdf目录 该目录为合并之后的pdf的导出目录
        os.chdir("D:\\App\\PyCharm\\PyCharm_Project\\data\\pdf\\")
        # 将复制的内容全部写入all.pdf文件中
        pdf.write(codecs.open(str(count) + ".pdf", "wb"))
        # 关闭打开的pdf文件 以便于之后的删除
        fd.close()
    # 删除掉 D:\App\PyCharm\PyCharm_Project\data\one 目录下的所有文件（pdf）
    path = "D:\\App\\PyCharm\\PyCharm_Project\\data\\one\\"
    for i in os.listdir(path):
        os.remove(os.path.join(path, i))


# ⑥判断是否是非汉语词汇 如果是则返回false
def is_Chinese(word):
    for ch in word:
        if '\u4e00' <= ch <= '\u9fff':
            return True
    return False


# ⑦进行词频统计并返回排好序的列表
def statistics(result):
    # 使用精确模式对文本进行分词 返回的是一个列表
    words = jieba.lcut(result)
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


# ⑧判断字符串中是否存在某个子串的函数
def selStr(str1, str2):
    p = str1.find(str2)
    if p == -1:
        return False
    return True


# ⑨判断法规的地区   国家 某个省/某个直辖市/某个自治区 某个市/某个区
def regulation_level(title_str):
    region = '国家'
    province_list = ['北京市', '天津市', '河北省', '山西省', '内蒙古自治区', '辽宁省', '吉林省', '黑龙江省', '上海市',
                     '江苏省', '浙江省', '安徽省', '福建省', '江西省', '山东省', '河南省', '湖北省', '湖南省', '广东省',
                     '广西壮族自治区', '海南省', '重庆市', '四川省', '贵州省', '云南省', '西藏自治区', '陕西省', '甘肃省',
                     '青海省', '宁夏回族自治区', '新疆维吾尔自治区']
    city_list = [
        ['东城区', '西城区', '朝阳区', '丰台区', '石景山区', '海淀区', '门头沟区', '房山区', '通州区', '顺义区', '昌平区', '大兴区', '怀柔区', '平谷区',
         '密云区' '延庆区'],
        ['和平区', '河东区', '河西区', '南开区', '河北区', '红桥区', '东丽区', '西青区', '津南区', '北辰区', '武清区', '宝坻区', '滨海新区', '宁河区', '静海区',
         '蓟州区'],
        ['石家庄市', '唐山市', '秦皇岛市', '邯郸市', '邢台市', '保定市', '张家口市', '承德市', '沧州市', '廊坊市', '衡水市'],
        ['太原市', '大同市', '阳泉市', '长治市', '晋城市', '朔州市', '晋中市', '运城市', '忻州市', '临汾市', '吕梁市'],
        ['呼和浩特市', '包头市', '乌海市', '赤峰市', '通辽市', '鄂尔多斯市', '呼伦贝尔市', '巴彦淖尔市', '乌兰察布市', '兴安盟', '锡林郭勒盟', '阿拉善盟'],
        ['沈阳市', '大连市', '鞍山市', '抚顺市', '本溪市', '丹东市', '锦州市', '营口市', '阜新市', '辽阳市', '盘锦市', '铁岭市', '朝阳市', '葫芦岛市'],
        ['长春市', '吉林市', '四平市', '辽源市', '通化市', '白山市', '松原市', '白城市', '延边朝鲜族自治州'],
        ['哈尔滨市', '齐齐哈尔市', '鸡西市', '鹤岗市', '双鸭山市', '大庆市', '伊春市', '佳木斯市', '七台河市', '牡丹江市', '黑河市', '绥化市', '大兴安岭地区'],
        ['黄浦区', '徐汇区', '长宁区', '静安区', '普陀区', '虹口区', '杨浦区', '闵行区', '宝山区', '嘉定区', '浦东新区', '金山区', '松江区', '青浦区', '奉贤区',
         '崇明区'],
        ['南京市', '无锡市', '徐州市', '常州市', '苏州市', '南通市', '连云港市', '淮安市', '盐城市', '扬州市', '镇江市', '泰州市', '宿迁市'],
        ['杭州市', '宁波市', '温州市', '嘉兴市', '湖州市', '绍兴市', '金华市', '衢州市', '舟山市', '台州市', '丽水市'],
        ['合肥市', '芜湖市', '蚌埠市', '淮南市', '马鞍山市', '淮北市', '铜陵市', '安庆市', '黄山市', '滁州市', '阜阳市', '宿州市', '六安市', '亳州市', '池州市',
         '宣城市'],
        ['福州市', '厦门市', '莆田市', '三明市', '泉州市', '漳州市', '南平市', '龙岩市', '宁德市'],
        ['南昌市', '景德镇市', '萍乡市', '九江市', '新余市', '鹰潭市', '赣州市', '吉安市', '宜春市', '抚州市', '上饶市'],
        ['济南市', '青岛市', '淄博市', '枣庄市', '东营市', '烟台市', '潍坊市', '济宁市', '泰安市', '威海市', '日照市', '临沂市', '德州市', '聊城市', '滨州市',
         '菏泽市'],
        ['郑州市', '开封市', '洛阳市', '平顶山市', '安阳市', '鹤壁市', '新乡市', '焦作市', '濮阳市', '许昌市', '漯河市', '三门峡市', '南阳市', '商丘市', '信阳市',
         '周口市', '驻马店市'],
        ['武汉市', '黄石市', '十堰市', '宜昌市', '襄阳市', '鄂州市', '荆门市', '孝感市', '荆州市', '黄冈市', '咸宁市', '随州市', '恩施土家族苗族自治州'],
        ['长沙市', '株洲市', '湘潭市', '衡阳市', '邵阳市', '岳阳市', '常德市', '张家界市', '益阳市', '郴州市', '永州市', '怀化市', '娄底市', '湘西土家族苗族自治州'],
        ['广州市', '韶关市', '深圳市', '珠海市', ',汕头市', '佛山市', '江门市', '湛江市', '茂名市', '肇庆市', '惠州市', '梅州市', '汕尾市', '河源市', '阳江市',
         '清远市', '东莞市', '中山市', '潮州市', '揭阳市', '云浮市'],
        ['南宁市', '柳州市', '桂林市', '梧州市', '北海市', '防城港市', '钦州市', '贵港市', '玉林市', '百色市', '贺州市', '河池市', '来宾市', '崇左市'],
        ['海口市', '三亚市', '三沙市', '儋州市'],
        ['万州区', '涪陵区', '渝中区', '大渡口区', '江北区', '沙坪坝区', '九龙坡区', '南岸区', '北碚区', '綦江区', '大足区', '渝北区', '巴南区', '黔江区', '长寿区',
         '江津区', '合川区', '永川区', '南川区', '璧山区', '铜梁区',
         '潼南区', '荣昌区', '开州区', '梁平区', '武隆区', '城口县', '丰都县', '垫江县', '忠县云阳县', '奉节县', '巫山县', '巫溪县', '石柱土家族自治县', '秀山土家族苗族自治县',
         '酉阳土家族苗族自治县', '彭水苗族土家族自治县'],
        ['成都市', '自贡市', '攀枝花市', '泸州市', '德阳市', '绵阳市', '广元市', '遂宁市', '内江市', '乐山市', '南充市', '眉山市', '宜宾市', '广安市', '达州市',
         '雅安市', '巴中市', '资阳市', '阿坝藏族羌族自治州', '甘孜藏族自治州', '凉山彝族自治州'],
        ['贵阳市', '六盘水市', '遵义市', '安顺市', '毕节市', '铜仁市', '黔西南布依族苗族自治州', '黔东南苗族侗族自治州', '黔南布依族苗族自治州'],
        ['昆明市', '曲靖市', '玉溪市', '保山市', '昭通市', '丽江市', '普洱市', '临沧市', '楚雄彝族自治州', '红河哈尼族彝族自治州', '文山壮族苗族自治州', '西双版纳傣族自治州',
         '大理白族自治州', '德宏傣族景颇族自治州', '怒江傈僳族自治州', '迪庆藏族自治州'],
        ['拉萨市', '日喀则市', '昌都市', '林芝市', '山南市', '那曲市', '阿里地区'],
        ['西安市', '铜川市', '宝鸡市', '咸阳市', '渭南市', '延安市', '汉中市', '榆林市', '安康市', '商洛市'],
        ['兰州市', '嘉峪关市', '金昌市', '白银市', '天水市', '武威市', '张掖市', '平凉市', '酒泉市', '庆阳市', '定西市', '陇南市', '临夏回族自治州', '甘南藏族自治州'],
        ['西宁市', '海东市', '海北藏族自治州', '黄南藏族自治州', '海南藏族自治州', '果洛藏族自治州', '玉树藏族自治州', '海西蒙古族藏族自治州'],
        ['银川市', '石嘴山市', '吴忠市', '固原市', '中卫市'],
        ['乌鲁木齐市', '克拉玛依市', '吐鲁番市', '哈密市', '昌吉回族自治州', '博尔塔拉蒙古自治州', '巴音郭楞蒙古自治州', '阿克苏地区', '克孜勒苏柯尔克孜自治州', '喀什地区', '和田地区',
         '伊犁哈萨克自治州', '塔城地区', '阿勒泰地区']
    ]
    # 匹配到具体的省/直辖市/自治区 读取对应的市/区
    city_num = 0
    # 判断也没有匹配到省/直辖市/自治区
    flag1 = False
    # 用来读取具体的省/直辖市/自治区
    countnum = 0
    # 判断是哪个 省/直辖市/自治区
    for province in province_list:
        city_num += 1
        if selStr(title_str, province):
            region = province
            flag1 = True
            break
    # 判断是哪个 市/区
    if flag1:
        for city in city_list[city_num - 1]:
            if selStr(title_str, city):
                region += city
                break
    else:
        for province in city_list:
            flag2 = False
            countnum += 1
            for city in province:
                if selStr(title_str, city):
                    region = city
                    flag2 = True
                    break
            if flag2 is True:
                region = province_list[int(countnum) - 1] + region
                break
    return region


# ⑩获取随机headers
def get_headers():
    # 得到随机headers
    user_agents = [
        "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; AcooBrowser; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
        "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0; Acoo Browser; SLCC1; .NET CLR 2.0.50727; Media Center PC 5.0; .NET CLR 3.0.04506)",
        "Mozilla/4.0 (compatible; MSIE 7.0; AOL 9.5; AOLBuild 4337.35; Windows NT 5.1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
        "Mozilla/5.0 (Windows; U; MSIE 9.0; Windows NT 9.0; en-US)",
        "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 2.0.50727; Media Center PC 6.0)",
        "Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 1.0.3705; .NET CLR 1.1.4322)",
        "Mozilla/4.0 (compatible; MSIE 7.0b; Windows NT 5.2; .NET CLR 1.1.4322; .NET CLR 2.0.50727; InfoPath.2; .NET CLR 3.0.04506.30)",
        "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN) AppleWebKit/523.15 (KHTML, like Gecko, Safari/419.3) Arora/0.3 (Change: 287 c9dfb30)",
        "Mozilla/5.0 (X11; U; Linux; en-US) AppleWebKit/527+ (KHTML, like Gecko, Safari/419.3) Arora/0.6",
        "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.2pre) Gecko/20070215 K-Ninja/2.1.1",
        "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9) Gecko/20080705 Firefox/3.0 Kapiko/3.0",
        "Mozilla/5.0 (X11; Linux i686; U;) Gecko/20070322 Kazehakase/0.4.5",
        "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.8) Gecko Fedora/1.9.0.8-1.fc10 Kazehakase/0.5.6",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) AppleWebKit/535.20 (KHTML, like Gecko) Chrome/19.0.1036.7 Safari/535.20",
        "Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; fr) Presto/2.9.168 Version/11.52",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.11 TaoBrowser/2.0 Safari/536.11",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.71 Safari/537.1 LBBROWSER",
        "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E; LBBROWSER)",
        "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; QQDownload 732; .NET4.0C; .NET4.0E; LBBROWSER)",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.84 Safari/535.11 LBBROWSER",
        "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E)",
        "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E; QQBrowser/7.0.3698.400)",
        "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; QQDownload 732; .NET4.0C; .NET4.0E)",
        "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; SV1; QQDownload 732; .NET4.0C; .NET4.0E; 360SE)",
        "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; QQDownload 732; .NET4.0C; .NET4.0E)",
        "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E)",
        "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.89 Safari/537.1",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.89 Safari/537.1",
        "Mozilla/5.0 (iPad; U; CPU OS 4_2_1 like Mac OS X; zh-cn) AppleWebKit/533.17.9 (KHTML, like Gecko) Version/5.0.2 Mobile/8C148 Safari/6533.18.5",
        "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:2.0b13pre) Gecko/20110307 Firefox/4.0b13pre",
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:16.0) Gecko/20100101 Firefox/16.0",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11",
        "Mozilla/5.0 (X11; U; Linux x86_64; zh-CN; rv:1.9.2.10) Gecko/20100922 Ubuntu/10.10 (maverick) Firefox/3.6.10"
    ]
    user_agent = random.choice(user_agents)
    headers = {'User-Agent': user_agent}
    return headers


# ⑩①逐页爬取搜索到的法规内容的函数
def get_regulaotion(page, title_url):
    # 逐页爬取法规
    for _page in range(int(page)):
        # 修改PageIndex的值来跳转到不同的页面， 实现逐页爬取
        new_url = title_url + '&PageIndex=' + str(_page + 1)
        response1 = requests.get(url=new_url, headers=get_headers())
        # html字符串创建BeautifulSoup对象 解析方式为lxml
        new_soup = BeautifulSoup(response1.text, 'lxml')
        # 当前页面中的法规标题列表
        new_list = new_soup.find_all('a', {'target': "_blank"})
        # 依次爬取当前页面中的法规
        for Title in new_list:
            # 声明并引用全局变量 count详情见上头
            global count
            count += 1
            # title为法规的简短名称，即标题 转化为字符串格式保存
            title = Title.get_text()
            # 用来存放法规的标题和相关信息
            title_message = title + '\n'

            # ===============================================判断法规类型===========================================================================================
            global message_type
            message_type = regulaotion_type(title)
            # ===============================================判断法规类型===========================================================================================

            url2 = 'http://search.chinalaw.gov.cn/'
            # 加上 Title 的 href 和 PageIndex 形成新的 Url，并且因 Url 只允许 Ascii 字符，所以需编码，将字符串转化成 Python 解释器可以看懂的 Ascii 形式
            content_url = urllib.parse.quote(url2 + Title['href'] + '&PageIndex=1', safe=string.printable)
            # 对应每条法规的完整的Url
            Url = str(content_url)

            # ===============================================URL转二维码===========================================================================================
            url_to_png(Url)
            # ===============================================URL转二维码===========================================================================================

            # 爬取属性为 class="d_infor" 的 td 中的内容和属性为 class="textAlignCenter" 的
            # p 中的内容，并组成完整的包函相关信息的法规标题 title_message
            response2 = requests.get(url=content_url, headers=get_headers())
            # html字符串创建BeautifulSoup对象 解析方式为lxml
            content_soup = BeautifulSoup(response2.text, 'lxml')
            for information in content_soup.find('table', {'class': "d_infor"}).find_all('td'):
                title_message += information.get_text() + '\n'
            if content_soup.find('p', {'class': "textAlignCenter"}).string is None:
                print('该列为空')
            else:
                title_message += content_soup.find('p', {'class': "textAlignCenter"}).string + '\n'

            # ===============================================判断法规地区===========================================================================================
            region = regulation_level(title)
            # ===============================================判断法规地区===========================================================================================

            # ===============================================判断法规国家还是具体省市=================================================================================
            if region == '国家':
                district = '国家'
            else:
                district = '地方'
            # ===============================================判断法规国家还是具体省市=================================================================================

            # 法规内容为 content，将title_message赋值给它，后续再追加内容
            content = title_message
            # 获取每篇文章的页数
            pagecount = content_soup.find(id="pagecount")
            if pagecount is None:
                # 法规只有一页 所以只爬取一页

                # ======================将该页导出为 pdf 导出目录为 'D:\App\PyCharm\PyCharm_Project\data\one\'========================================================
                for a in range(1):
                    try:
                        pdfkit.from_url(content_url, 'D:\\App\\PyCharm\\PyCharm_Project\\data\\one\\' + '1.pdf')
                    except Exception as e:
                        # 删除错误的文件
                        os.remove('D:\\App\\PyCharm\\PyCharm_Project\\data\\one\\' + '1.pdf')
                        print("网站：", content_url)
                        print("报错信息：", e)
                        sys.exit()
                    else:
                        break
                # ======================将该页导出为 pdf 导出目录为 'D:\App\PyCharm\PyCharm_Project\data\one\'========================================================

                # 爬取属性为 div class="con" 中所有包含在 td 中的内容并放入 content 形成完整的法规内容 content
                for I in content_soup.find('div', {'class': "con"}).find_all('td'):
                    content = content + I.get_text() + '\n'
            else:
                # 逐页爬取多页法规
                for Pagecount in range(int(pagecount.string)):
                    url = urllib.parse.quote(url2 + Title['href'] + '&PageIndex=' + str(Pagecount + 1),
                                             safe=string.printable)
                    response3 = requests.get(url=url, headers=get_headers())
                    soup = BeautifulSoup(response3.text, 'lxml')

                    # ======================将该页导出为 pdf 导出目录为 'D:\App\PyCharm\PyCharm_Project\data\one\'========================================================
                    for a in range(1):
                        try:
                            pdfkit.from_url(url, 'D:\\App\\PyCharm\\PyCharm_Project\\data\\one\\' + str(
                                Pagecount + 1) + '.pdf')
                        except Exception as e:
                            # 删除错误的文件
                            os.remove('D:\\App\\PyCharm\\PyCharm_Project\\data\\one\\' + str(Pagecount + 1) + '.pdf')
                            print("网站：", content_url)
                            print("报错信息：", e)
                            sys.exit()
                        else:
                            break
                    # ======================将该页导出为 pdf 导出目录为 'D:\App\PyCharm\PyCharm_Project\data\one\'========================================================

                    # 爬取属性为 div class="con" 中所有包含在 td 中的内容并放入 content 形成完整的法规内容 content
                    for I in soup.find('div', {'class': "con"}).find_all('td'):
                        content = content + I.get_text() + '\n'
                        # 判断是否爬取成功 不成功则用另一套方法爬取
            if title == content:
                if pagecount is None:
                    # 法规只有一页 所以只爬取一页

                    # ======================将该页导出为 pdf 导出目录为 'D:\App\PyCharm\PyCharm_Project\data\one\'========================================================
                    for a in range(1):
                        try:
                            pdfkit.from_url(content_url, 'D:\\App\\PyCharm\\PyCharm_Project\\data\\one\\' + '1.pdf')
                        except Exception as e:  #
                            # 删除错误的文件
                            os.remove('D:\\App\\PyCharm\\PyCharm_Project\\data\\one\\' + '1.pdf')
                            print("网站：", content_url)
                            print("报错信息：", e)
                            sys.exit()
                        else:
                            break
                    # ======================将该页导出为 pdf 导出目录为 'D:\App\PyCharm\PyCharm_Project\data\one\'========================================================

                    # 爬取属性为div class="con"中所有包含在td中的内容并放入content 形成完整的法规内容 content
                    for I in content_soup.find('div', {'class': "detailCon"}).find_all('p'):
                        content = content + I.get_text() + '\n'
                else:
                    # 逐页爬取多页法规
                    for Pagecount in range(int(pagecount.string)):
                        _url = urllib.parse.quote(url2 + Title['href'] + '&PageIndex=' + str(Pagecount + 1),
                                                  safe=string.printable)
                        response4 = requests.get(url=_url, headers=get_headers())
                        _soup = BeautifulSoup(response4.text, 'lxml')

                        # ======================将该页导出为 pdf 导出目录为 'D:\App\PyCharm\PyCharm_Project\data\one\'========================================================
                        for a in range(1):
                            try:
                                pdfkit.from_url(_url, 'D:\\App\\PyCharm\\PyCharm_Project\\data\\one\\' + str(
                                    Pagecount + 1) + '.pdf')
                            except Exception as e:
                                # 删除错误的文件
                                os.remove('D:\\App\\PyCharm\\PyCharm_Project\\data\\one\\' +
                                          str(Pagecount + 1) + '.pdf')
                                print("网站：", content_url)
                                print("报错信息：", e)
                                sys.exit()
                            else:
                                break
                        # ======================将该页导出为 pdf 导出目录为 'D:\App\PyCharm\PyCharm_Project\data\one\'========================================================

                        # 爬取属性为 div class="con" 中所有包含在 td 中的内容并放入 content 形成完整的法规内容 content
                        for I in _soup.find('div', {'class': "detailCon"}).find_all('p'):
                            content = content + I.get_text() + '\n'

            # =====================================对法规进行词频统计 确定三个关键字============================================================================================
            list_keyword = statistics(content)
            result_keyword = []
            for i in range(3):
                word, cou = list_keyword[i]
                result_keyword.append(word)
            # 存入字符串以便后用
            keywords1 = (str(result_keyword[0]) + ',' + str(result_keyword[1]) + ',' + str(result_keyword[2]))
            # =====================================对法规进行词频统计 确定三个关键字============================================================================================

            # =====================================将导出的多个pdf合并为一个pdf===============================================================================================
            merge_pdf()
            # =====================================将导出的多个pdf合并为一个pdf===============================================================================================

            # 入库操作 库的配置为opt
            '''
            opt = {'host': '输入主机名',
                   'user': 'root',
                   'password': '输入密码',
                   'port': 3300,
                   'database': 'intelligence',
                   'charset': ''}
            '''
            opt = {'host': 'localhost',
                   'user': 'root',
                   'password': '780815',
                   'port': 3306,
                   'database': 'test',
                   'charset': ''}

            # 连接数据库
            db = Db_Operation.connect(opt)
            # 爬入legal库
            Db_Operation.Add(db, "INSERT INTO legal "
                                 "(message_type,pstage,message,graph_dic,text_dic,url,district,region,remarks,keywords) "
                                 "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                             (message_type, '项目前期阶段（变电）', title,
                              '/root/intelligence/legal/png/' + str(count) + '.png',
                              '/root/intelligence/legal/pdf/' + str(count) + '.pdf',
                              Url, district, region, content, keywords1))

            # =====================================法规分条并存入列表result===============================================================================================
            result_item = _split(content)
            # =====================================法规分条并存入列表result===============================================================================================

            # ===================================对法规进行词频统计 确定两个关键字===========================================================================================
            keywords2 = []
            for item in result_item:
                list_item = statistics(item)
                result = []
                if len(list_item) == 1:
                    word, count2 = list_item[0]
                    keywords2.append(word)
                elif len(list_item) == 0:
                    keywords2.append('无')
                else:
                    for i in range(2):
                        word, count2 = list_item[i]
                        result.append(word)
                    # 存入字符串以便后用
                    keywords2.append(str(result[0]) + ',' + str(result[1]))
            # ===================================对法规进行词频统计 确定两个关键字===========================================================================================

            # 爬入item库
            # 法规逐条入库
            for i in range(len(result_item)):
                Db_Operation.Add(db, "INSERT INTO item (remarks,keywords,legal_id) "
                                     "VALUES (%s,%s,%s)",
                                 (result_item[i], keywords2[i], str(count)))
            # 关闭数据库连接
            db.close()


# 函数主体从这里开始
# 根据name_list表逐名爬取
for Name in name_list:
    # 爬取法律法规数据库 ：http://search.chinalaw.gov.cn/search2.html
    url1 = 'http://search.chinalaw.gov.cn/SearchLawTitle?Query='
    # 加上name形成新的url，因为URL只允许ASCII字符，所以需编码，将字符串转化成python解释器可以看懂的ascii形式
    title_url = urllib.parse.quote(url1 + Name, safe=string.printable)
    # 测试直接用森林
    # title_url = urllib.parse.quote(url1 + '森林', safe=string.printable)
    response = requests.get(url=title_url, headers=get_headers())
    # html字符串创建BeautifulSoup对象 解析方式为lxml
    title_soup = BeautifulSoup(response.text, 'lxml')
    # 找到的页数
    Page = title_soup.find(id="pagecount")
    if Page is None:
        page = 1
    else:
        page = Page.string
    # 逐页爬取搜索到的法规内容
    get_regulaotion(page, title_url)
    print('爬取完毕')




