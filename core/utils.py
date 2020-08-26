import random
import string
import sys
import time
from io import StringIO


def random_name():
    # 删减部分，比较大众化姓氏
    firstName = "赵钱孙李周吴郑王冯陈褚卫蒋沈韩杨朱秦尤许何吕施张孔曹严华金魏陶姜戚谢邹喻水云苏潘葛奚范彭郎鲁韦昌马苗凤花方俞任袁柳鲍史唐费岑薛雷贺倪汤滕殷罗毕郝邬安常乐于时傅卞齐康伍余元卜顾孟平" \
                "黄和穆萧尹姚邵湛汪祁毛禹狄米贝明臧计成戴宋茅庞熊纪舒屈项祝董粱杜阮席季麻强贾路娄危江童颜郭梅盛林刁钟徐邱骆高夏蔡田胡凌霍万柯卢莫房缪干解应宗丁宣邓郁单杭洪包诸左石崔吉" \
                "龚程邢滑裴陆荣翁荀羊甄家封芮储靳邴松井富乌焦巴弓牧隗山谷车侯伊宁仇祖武符刘景詹束龙叶幸司韶黎乔苍双闻莘劳逄姬冉宰桂牛寿通边燕冀尚农温庄晏瞿茹习鱼容向古戈终居衡步都耿满弘国文东殴沃曾关红游盖益桓公晋楚闫"
    # 百家姓全部姓氏
    # firstName = "赵钱孙李周吴郑王冯陈褚卫蒋沈韩杨朱秦尤许何吕施张孔曹严华金魏陶姜戚谢邹喻柏水窦章云苏潘葛奚范彭郎鲁韦昌马苗凤花方俞任袁柳酆鲍史唐费廉岑薛雷贺倪汤滕殷罗毕郝邬安常乐于时傅皮卞齐康伍余元卜顾孟平" \
    #             "黄和穆萧尹姚邵湛汪祁毛禹狄米贝明臧计伏成戴谈宋茅庞熊纪舒屈项祝董粱杜阮蓝闵席季麻强贾路娄危江童颜郭梅盛林刁钟徐邱骆高夏蔡田樊胡凌霍虞万支柯昝管卢莫经房裘缪干解应宗丁宣贲邓郁单杭洪包诸左石崔吉钮" \
    #             "龚程嵇邢滑裴陆荣翁荀羊於惠甄麴家封芮羿储靳汲邴糜松井段富巫乌焦巴弓牧隗山谷车侯宓蓬全郗班仰秋仲伊宫宁仇栾暴甘钭厉戎祖武符刘景詹束龙叶幸司韶郜黎蓟薄印宿白怀蒲邰从鄂索咸籍赖卓蔺屠蒙池乔阴欎胥能苍" \
    #             "双闻莘党翟谭贡劳逄姬申扶堵冉宰郦雍舄璩桑桂濮牛寿通边扈燕冀郏浦尚农温别庄晏柴瞿阎充慕连茹习宦艾鱼容向古易慎戈廖庾终暨居衡步都耿满弘匡国文寇广禄阙东殴殳沃利蔚越夔隆师巩厍聂晁勾敖融冷訾辛阚那简饶空" \
    #             "曾毋沙乜养鞠须丰巢关蒯相查後荆红游竺权逯盖益桓公晋楚闫法汝鄢涂钦归海帅缑亢况后有琴梁丘左丘商牟佘佴伯赏南宫墨哈谯笪年爱阳佟言福百家姓终"
    # 百家姓中双姓氏
    firstName2 = "万俟司马上官欧阳夏侯诸葛闻人东方赫连皇甫尉迟公羊澹台公冶宗政濮阳淳于单于太叔申屠公孙仲孙轩辕令狐钟离宇文长孙慕容鲜于闾丘司徒司空亓官司寇仉督子颛孙端木巫马公西漆雕乐正壤驷公良拓跋夹谷宰父谷梁段干百里东郭南门呼延羊舌微生梁丘左丘东门西门南宫南宫"
    # 女孩名字
    girl = '秀娟英华慧巧美娜静淑惠珠翠雅芝玉萍红娥玲芬芳燕彩春菊兰凤洁梅琳素云莲真环雪荣爱妹霞香月莺媛艳瑞凡佳嘉琼勤珍贞莉桂娣叶璧璐娅琦晶妍茜秋珊莎锦黛青倩婷姣婉娴瑾颖露瑶怡婵雁蓓纨仪荷丹蓉眉君琴蕊薇菁梦岚苑婕馨瑗琰韵融园艺咏卿聪澜纯毓悦昭冰爽琬茗羽希宁欣飘育滢馥筠柔竹霭凝晓欢霄枫芸菲寒伊亚宜可姬舒影荔枝思丽'
    # 男孩名字
    boy = '伟刚勇毅俊峰强军平保东文辉力明永健世广志义兴良海山仁波宁贵福生龙元全国胜学祥才发武新利清飞彬富顺信子杰涛昌成康星光天达安岩中茂进林有坚和彪博诚先敬震振壮会思群豪心邦承乐绍功松善厚庆磊民友裕河哲江超浩亮政谦亨奇固之轮翰朗伯宏言若鸣朋斌梁栋维启克伦翔旭鹏泽晨辰士以建家致树炎德行时泰盛雄琛钧冠策腾楠榕风航弘'
    # 名
    name = '中笑贝凯歌易仁器义礼智信友上都卡被好无九加电金马钰玉忠孝'

    # 10%的机遇生成双数姓氏
    if random.choice(range(100)) > 10:
        firstName_name = firstName[random.choice(range(len(firstName)))]
    else:
        i = random.choice(range(len(firstName2)))
        firstName_name = firstName2[i:i + 2]

    sex = random.choice(range(2))
    name_1 = ""
    if sex > 0:
        girl_name = girl[random.choice(range(len(girl)))]
        if random.choice(range(2)) > 0:
            name_1 = name[random.choice(range(len(name)))]
        return firstName_name + name_1 + girl_name
    else:
        boy_name = boy[random.choice(range(len(boy)))]
        if random.choice(range(2)) > 0:
            name_1 = name[random.choice(range(len(name)))]

        return firstName_name + name_1 + boy_name


def CreatIDnum():
    jiaoyan = 10
    all_ = 0
    result = 0
    while ((jiaoyan % 11) == 10 or result == 0):
        # 省份
        s = [11, 12, 13, 14, 15, 21, 22, 23, 31, 32, 33, 34, 35, 36, 37, 41, 42, 43, 44, 45, 46, 50, 51, 52, 53, 54,
             61, 62, 63, 64, 65]
        qian = s[random.randint(0, 30)] * 10000 + random.randint(0, 10) * 100 + random.randint(0, 10)
        jiaoyan = 0
        zhong = random.randint(1970, 2000) * 10000 + random.randint(1, 12) * 100 + random.randint(1, 28)

        hou = random.randint(1, 10) * 100 + random.randint(0, 1)

        all = qian * 100000000000 + zhong * 1000 + hou
        all_ = all
        list = []
        for i in range(0, 17):
            list.append(all // 10 ** (16 - i))
            all = all - all // 10 ** (16 - i) * 10 ** (16 - i)
        # 计算前面的校验
        for j in range(0, 17):
            jiaoyan = jiaoyan + list[j] * ((2 ** (17 - j)) % 11)
        for k in range(0, 10):
            if ((jiaoyan + k) % 11 == 1):
                result = all_ * 10 + k

    return result


def token():
    token = ''
    s = string.ascii_lowercase
    for _ in range(4):
        token += random.choice(s)
        token += str(random.choice(range(10)))
    return token


def diffday(t1, t2, AM=5):
    """
    判断两天不同（以默认5AM为界限）
    :param t1: 当前时间
    :param t2: 上一时间
    :return:
    """
    if (t1 - t2) > 3600 * 24:
        return True
    # -5小时，将一天的开始定位5:00AM
    s1 = time.localtime(t1 - AM * 3600)
    s2 = time.localtime(t2 - AM * 3600)
    day1 = s1.tm_year * 366 + s1.tm_yday
    day2 = s2.tm_year * 366 + s2.tm_yday
    if day1 > day2:
        return True
    else:
        return False


def diff_6hour(t1, t2):
    """
    以0h,6h,12h,18h为界判断两个时间是否在两个区间
    :param t1: 当前时间
    :param t2: 上一时间
    :return:
    """
    if (t1 - t2) > 3600 * 6:
        return True
    s1 = time.localtime(t1)
    s2 = time.localtime(t2)
    day1 = s1.tm_year * 366 + s1.tm_yday
    day2 = s2.tm_year * 366 + s2.tm_yday
    if day1 > day2:
        return True
    else:
        h1 = s1.tm_hour
        h2 = s2.tm_hour
        span = [(0, 6), (6, 12), (12, 18), (18, 24)]
        for l, r in span:
            if l <= h1 < r and l <= h2 < r:
                return False
        return True


def diff_5_12hour(t1, t2):
    """
    以5h和12h为界判断两个时间是否在两个区间
    :param t1: 当前时间
    :param t2: 上一时间
    :return:
    """
    if (t1 - t2) > 3600 * 6:
        return True
    # 5h->0h, 12h->7h
    s1 = time.localtime(t1 - 5 * 3600)
    s2 = time.localtime(t2 - 5 * 3600)
    day1 = s1.tm_year * 366 + s1.tm_yday
    day2 = s2.tm_year * 366 + s2.tm_yday
    if day1 > day2:
        return True
    else:
        h1 = s1.tm_hour
        h2 = s2.tm_hour
        span = [(0, 7), (7, 24)]
        for l, r in span:
            if l <= h1 < r and l <= h2 < r:
                return False
        return True


def PrintToStr(fun, *args, **kwargs):
    old_stdout = sys.stdout
    result = StringIO()
    sys.stdout = result
    fun(*args, **kwargs)
    sys.stdout = old_stdout
    return result.getvalue()


if __name__ == '__main__':
    for i in range(100):
        print(token())
