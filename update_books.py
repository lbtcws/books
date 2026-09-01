#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate book metadata JSON from public/books directory."""

import os
import json
import re
import hashlib

BOOKS_DIR = os.path.join(os.path.dirname(__file__), "public", "books")

# Known book summaries (title -> summary)
BOOK_SUMMARIES = {
    # 小说
    "庆余年": "一部架空历史小说，讲述范闲在庆国权谋斗争中的成长与传奇经历。",
    "穆斯林的葬礼": "霍达代表作，讲述一个穆斯林家族三代人的命运沉浮与文化冲突。",
    "起床后的黄金1小时": "介绍如何利用早晨起床后的黄金一小时提升效率、改变人生。",
    "世界观": "系统介绍科学哲学和科学史，帮助现代人理解科学思维与世界观念。",
    "东晋十六国风云": "讲述东晋十六国时期波澜壮阔的历史风云与民族融合。",
    "人月神话": "软件工程经典著作，探讨软件开发的本质、规律与管理方法。",
    "人生只有一件事": "讲述人生最重要的是找到一件值得全力以赴的事。",
    "围城": "钱钟书经典小说，以方鸿渐的经历讽刺知识分子的困境与人生围城。",
    "悉达多": "黑塞代表作，讲述悉达多追寻自我与生命真谛的精神之旅。",
    "悲惨世界": "雨果巨著，通过冉阿让的一生展现19世纪法国社会的苦难与救赎。",
    "明朝那些事儿": "当年明月以通俗笔法讲述明朝三百年兴衰历史，兼具史实与趣味。",
    "月亮和六便士": "毛姆代表作，讲述一个中年人抛弃世俗追求艺术理想的故事。",
    "杀死一只知更鸟": "哈珀·李经典小说，通过儿童视角探讨种族偏见与正义良知。",
    "吾国与吾民": "林语堂向西方介绍中国文化与民族性格的经典之作。",
    "枪炮、病菌与钢铁": "戴蒙德从地理与环境角度解释人类社会命运差异的跨学科巨著。",
    "毛泽东传": "全面记述毛泽东一生的传记，涵盖其革命历程与思想发展。",
    "活着": "余华代表作，讲述福贵一生的苦难与对生命的坚韧承受。",
    "深度思考": "介绍如何透过现象看本质，培养深度思考与解决问题的能力。",
    "父母的觉醒": "探讨父母如何通过自我觉醒来更好地养育孩子。",
    "美人赠我蒙汗药": "王朔与老侠的对话录，涉及文化、社会与人生的犀利评论。",
    "理想国": "柏拉图经典著作，探讨正义、理想社会与哲学王的治理。",
    "生命之书": "克里希那穆提的每日冥想指南，帮助读者静心观照内心。",
    "白鹿原": "陈忠实代表作，讲述白鹿原上两大家族跨越数代的命运变迁。",
    "笑傲江湖": "金庸武侠小说，讲述令狐冲在江湖纷争中的成长与爱情。",
    "边城": "沈从文代表作，以湘西为背景讲述翠翠纯美而忧伤的爱情故事。",
    "来生不做中国人": "钟祖康的争议性著作，对中国文化与国民性的批判性反思。",
    "菊与刀": "本尼迪克特研究日本民族性的经典之作，解析日本文化矛盾特质。",
    # 巴菲特信
    "巴菲特致股东信": "巴菲特每年致伯克希尔股东的信，阐述投资理念与经营思考。",
    "巴菲特50年评论": "对伯克希尔五十年历程的回顾、评论与未来展望。",
    "伯克希尔50周年评论": "芒格对伯克希尔五十年历程的评论与反思。",
    # 认知
    "乌合之众": "勒庞经典社会心理学著作，剖析群体行为的非理性特征。",
    "纳瓦尔宝典": "纳瓦尔关于财富创造与幸福获取的思维方法与人生智慧。",
    "主角模式": "樊登讲解如何从被动人生转向主动掌控的主角思维模式。",
    "事实": "罗斯林揭示人类对世界的十大本能偏见，用数据还原真实世界。",
    "动机与人格": "马斯洛经典著作，系统阐述需求层次理论与人格心理学。",
    "中国人的性格": "亚瑟·史密斯晚清时期对中国国民性的观察与分析。",
    "人人都可以学的顶级思维法": "套装7册，介绍多种顶级思维方法帮助提升认知与决策能力。",
    "人性的弱点": "卡耐基经典之作，讲述人际交往与影响他人的基本原则。",
    "从优秀到卓越": "柯林斯研究企业如何从优秀跨越到卓越的管理学经典。",
    "洗脑心理学": "凯瑟琳·泰勒揭示洗脑与心理控制的科学原理与机制。",
    "基业长青": "柯林斯研究高瞻远瞩公司永续经营的秘诀与管理原则。",
    "底层逻辑": "刘润讲解看透世界底牌的思维方式与认知升级方法。",
    "思考，快与慢": "卡尼曼揭示人类思维的两套系统及其对决策的影响。",
    "我们为什么要睡觉": "比尔·盖茨推荐的睡眠科学著作，解析睡眠对健康的关键作用。",
    "少有人走的路": "斯科特·派克探讨心智成熟与自我成长的心理学经典。",
    "红与黑": "司汤达代表作，讲述于连在复辟王朝时期的野心与爱情悲剧。",
    "黑天鹅": "塔勒布揭示极端不确定事件对世界的巨大影响与应对之道。",
    "结构化思维": "介绍结构化思考的方法与工具，提升逻辑表达与问题解决能力。",
    "老人与海": "海明威代表作，讲述老渔夫与大马林鱼搏斗的硬汉精神。",
    "背叛": "豆豆小说，讲述商人宋一坤的商战与人性挣扎。",
    "自卑与超越": "阿德勒个体心理学经典，探讨自卑感与自我超越的路径。",
    "自私的基因": "道金斯从基因视角解释生物进化与人类行为的科学经典。",
    "蒋介石日记": "蒋介石1915至1949年间的私人日记，记录其心路与近代史重大事件。",
    "表象与本质": "侯世达探讨类比在认知中的核心作用，揭示思维的本质。",
    "财富自由之路": "李笑来关于如何通过认知升级实现财富自由的思维方法论。",
    "统计数字会撒谎": "达莱尔·哈夫揭露统计数据被操纵的常见手法与陷阱。",
    "统计陷阱": "达莱尔·哈夫用通俗语言揭示统计学中的常见误导与陷阱。",
    "金字塔原理": "芭芭拉·明托提出的结构化思考与表达的经典方法论。",
    "长尾理论": "克里斯·安德森揭示互联网时代长尾经济的商业新逻辑。",
    "引爆点": "格拉德威尔探讨流行潮如何爆发与传播的社会学著作。",
    "麻省理工深度思考法": "平井孝志介绍用模型与动力机制深度思考现象的方法。",
    # 财经
    "30岁之后，用钱赚钱": "介绍30岁后如何通过理财实现财富增值与财务自由。",
    "一本书读懂财报": "肖星讲解如何阅读与分析财务报表的入门经典。",
    "怎样选择成长股": "费雪的成长股投资方法论，影响巴菲特的投资经典。",
    "资产配置的艺术": "介绍资产配置的原理与方法，帮助构建稳健投资组合。",
    "一本书读懂投资理财学": "投资理财入门读物，系统介绍理财知识与实用方法。",
    "不炒股只投基": "雪球岛系列，介绍低风险基金投资获取稳健收益的方法。",
    "金融炼金术": "索罗斯的反身性理论与其金融市场实践的思考记录。",
    "国富论": "亚当·斯密经济学奠基之作，探讨国民财富的性质与原因。",
    "金融学": "博迪与莫顿合著的经典金融学教材，覆盖金融体系核心理论。",
    "就业、利息和货币通论": "凯恩斯革命性著作，奠定现代宏观经济学的基础。",
    "Principles of Economics": "门格尔的经济学原理，边际革命的奠基性著作之一。",
    "资本论": "马克思政治经济学巨著，系统分析资本主义生产方式。",
    "反脆弱": "塔勒布探讨如何从不确定性与混乱中获益的思维框架。",
    "思想者的足迹": "普雷斯曼介绍五十位重要西方经济学家及其思想贡献。",
    "中级微观经济学": "范里安的中级微观经济学教材，现代观点与严谨分析并重。",
    "微观经济分析": "范里安的高级微观经济学分析教材，理论深入且系统。",
    "你的灯亮着吗": "高斯与温伯格探讨如何发现与定义真正问题的经典小书。",
    "宏观经济学": "多恩布什、费希尔与斯塔兹合著的经典宏观经济学教材。",
    "只有偏执狂才能生存": "格鲁夫讲述战略转折点的识别与企业生存之道。",
    "格鲁夫给经理人的第一课": "格鲁夫分享英特尔管理方法论与经理人实战心得。",
    "富爸爸穷爸爸": "清崎通过两个父亲的对比讲述财商教育与财富思维。",
    "Natural Value": "维塞尔的自然价值理论，奥地利学派的重要经济学著作。",
    "个人主义与经济秩序": "哈耶克探讨自发秩序与个人主义的经济哲学经典。",
    "第五项修炼": "圣吉提出学习型组织的五项修炼与系统思考方法。",
    "经济为什么会崩溃": "希夫兄弟用寓言故事讲解经济学基本原理。",
    "高级宏观经济学": "罗默的高级宏观经济学教材，覆盖现代宏观理论前沿。",
    "手把手教你读财报": "唐朝讲解如何阅读与分析财报的实战指南。",
    "手把手教你读财报笔记": "读者对《手把手教你读财报》的笔记与心得整理。",
    "New Ideas from Dead Economists": "布赫霍尔茨介绍已故经济学家的思想对现代的启示。",
    "经济学大师们": "布赫霍尔茨通俗讲解经济学大师们的思想与贡献。",
    "投资中最简单的事": "邱国鹭分享价值投资在中国市场的实践与思考。",
    "投资最重要的事": "马克斯分享投资中最重要的20条经验与思考。",
    "投资者的未来": "西格尔研究长期投资回报与股票市场的历史表现。",
    "指数基金投资指南": "银行螺丝钉讲解指数基金投资的入门与实战方法。",
    "文明、现代化、价值投资与中国": "李录探讨文明演进、现代化与价值投资在中国的实践。",
    "未来30年 用钱赚钱": "面向未来的理财指南，探讨长期财富积累的方法。",
    "定位": "特劳特与里斯提出的营销定位理论，影响深远的商业经典。",
    "段永平投资问答录": "段永平关于投资、企业与人生的问答与思考记录。",
    "海龟交易法则": "柯蒂斯·费思讲述海龟交易实验与趋势跟踪交易方法。",
    "滚雪球": "巴菲特传记，讲述其财富人生与投资哲学的形成。",
    "股票作手回忆录": "李费佛笔下的利弗莫尔，投机交易领域的经典之作。",
    "理财就是理生活": "讲述理财与生活规划相结合的个人财务管理方法。",
    "穷查理宝典": "查理·芒格的智慧箴言录，涵盖投资、思维与人生哲学。",
    "穷查理年鉴": "芒格每年的智慧语录与思考精华汇编。",
    "自由选择": "弗里德曼倡导经济自由与个人选择的经典经济学著作。",
    "随机致富的傻瓜": "塔勒布揭示运气与随机性在投资与人生中的隐藏作用。",
    "经济学原理": "曼昆的经济学入门经典教材，深入浅出讲解经济学原理。",
    "非理性繁荣": "希勒分析金融市场非理性行为与资产泡沫的形成。",
    "聪明的投资者": "格雷厄姆的价值投资经典，巴菲特称之为最佳投资书籍。",
    "股市长线法宝": "西格尔研究股票长期回报与投资策略的历史数据著作。",
    "生活中的经济学": "茅于轼用通俗语言讲解生活中的经济学原理。",
    "谁妨碍了我们致富": "茅于轼探讨阻碍财富创造与社会进步的制度与观念因素。",
    "薛兆丰经济学讲义": "薛兆丰用通俗语言讲解经济学思维与核心概念。",
    "从来就没有救世主": "许小年倡导市场自由与企业家精神的经济学思考。",
    "证券分析": "格雷厄姆与多德的价值投资圣经，证券分析领域的奠基之作。",
    "财务报表分析与股票估值": "讲解如何通过财报分析进行股票估值的方法与实务。",
    "财务自由之路": "博多·舍费尔讲解理财方法与财富积累路径。",
    "躺着赚钱": "懒人理财指南，介绍简单实用的投资盈利技巧。",
    "金融学从入门到精通": "系统介绍金融学基础知识与实用投资方法。",
    "金钱心理学": "豪泽尔探讨人们对金钱的心理偏见与财富行为的底层逻辑。",
    "论金融衍生工具": "米勒对金融衍生工具的理论分析与批判性思考。",
    "战胜华尔街": "介绍巴菲特战胜华尔街的投资策略与经验。",
    "文明、现代化、价值投资与中国": "李录探讨文明演进、现代化与价值投资在中国的实践。",
    "巴菲特50年评论-伯克希尔": "对伯克希尔五十年历程的回顾、评论与未来展望。",
}

# Known book titles that use "title：subtitle" format (not author：title)
KNOWN_TITLES_WITH_COLON = {
    "世界观", "滚雪球", "躺着赚钱", "穷查理宝典", "财务自由之路Ⅰ",
    "财务自由之路Ⅱ", "未来30年 用钱赚钱", "证券分析", "反脆弱",
    "生命之书", "麻省理工深度思考法", "文明、现代化、价值投资与中国",
}

# Files to skip
SKIP_FILES = {".DS_Store", "Thumbs.db", "desktop.ini"}


def clean_title_suffix(title):
    """Remove trailing edition/version info from title."""
    # Remove trailing "(扫描版)", "(高清)", "(大字版)", etc.
    title = re.sub(r'\s*[\(（](扫描版|高清|大字版|中文完整版|原书第\d+版|典藏版|珍藏版|含图版|第\d+版)[\)）]\s*', '', title)
    # Remove trailing "(共3卷 大字版)" etc.
    title = re.sub(r'\s*[\(（]共\d+卷[^)）]*[)）]\s*', '', title)
    # Remove trailing "(套装共N册)"
    title = re.sub(r'\s*[\(（]套装共\d+册[)）]\s*', '', title)
    # Remove trailing "(增补版)"
    title = re.sub(r'\s*[\(（]增补版[)）]\s*', '', title)
    # Remove trailing "(原本第四版)" etc.
    title = re.sub(r'\s*[\(（]原本第[^)）]+版[)）]\s*', '', title)
    # Remove trailing "(原书第N版)"
    title = re.sub(r'\s*[\(（]原书第[^)）]+版[)）]\s*', '', title)
    # Remove trailing "(第N版 ...)"
    title = re.sub(r'\s*[\(（]第\d+版[^)）]*[)）]\s*', '', title)
    # Remove "(高清)" without parens
    title = re.sub(r'\s*\(高清\)\s*', '', title)
    # Remove "(缺马克思那一章 扫描版)"
    title = re.sub(r'\s*[\(（]缺[^)）]*[)）]\s*', '', title)
    return title.strip()


def clean_author(author):
    """Clean up author name."""
    # Remove nationality markers like [美], [英], [日]
    author = re.sub(r'\[([^\]]+)\]', '', author)
    author = re.sub(r'【([^】]+)】', '', author)
    # Remove translator info after ；
    if '；' in author:
        parts = author.split('；')
        author = parts[0]
    # Remove "著", "译", "(译)" etc.
    author = re.sub(r'\s*著\s*$', '', author)
    author = re.sub(r'\s*译\s*$', '', author)
    author = re.sub(r'\([\u4e00-\u9fa5]+\)\s*$', '', author)
    # Remove trailing " ePUBw.COM" etc.
    author = re.sub(r'\s*ePUBw\.COM.*$', '', author)
    # Clean up multiple spaces
    author = re.sub(r'\s+', ' ', author).strip()
    return author


def parse_filename(filename):
    """Parse filename to extract title, author, and extension."""
    name, ext = os.path.splitext(filename)
    ext = ext.lower()
    
    # Remove common suffixes
    name = re.sub(r'\s*\(z-lib\.org\)\s*', '', name, flags=re.IGNORECASE)
    name = re.sub(r'\s*\(Z-Library\)\s*', '', name, flags=re.IGNORECASE)
    name = re.sub(r'\s*\(\d+\)\s*$', '', name)  # trailing (1), (2)
    name = re.sub(r'【[^】]*】', '', name)
    name = name.strip()
    
    # Pattern: "《书名》作者" - must check before removing brackets
    match = re.match(r'^《([^》]+)》\s*(.+)?$', name)
    if match:
        title = match.group(1).strip()
        author = match.group(2).strip() if match.group(2) else ""
        author = clean_author(author)
        title = clean_title_suffix(title)
        return title, author, ext
    
    # Remove 《》 brackets
    name = name.replace('《', '').replace('》', '')
    
    author = ""
    title = name
    
    # Pattern: "作者：书名" or "作者:书名"
    match = re.match(r'^([^：:]+)[：:](.+)$', name)
    if match:
        potential_author = match.group(1).strip()
        potential_title = match.group(2).strip()
        
        # Check if the part before ： is a known book title (title：subtitle pattern)
        is_known_title = False
        for kt in KNOWN_TITLES_WITH_COLON:
            if potential_author == kt or potential_author.startswith(kt):
                is_known_title = True
                break
        
        if not is_known_title:
            # Check if it looks like an author name
            is_author = False
            if '·' in potential_author or '&' in potential_author:
                if len(potential_author) <= 30:
                    is_author = True
            elif 2 <= len(potential_author) <= 4 and re.match(r'^[\u4e00-\u9fa5]+$', potential_author):
                is_author = True
            
            if is_author:
                author = clean_author(potential_author)
                title = clean_title_suffix(potential_title)
                return title, author, ext
    
    # Pattern: "书名 by 作者"
    match = re.match(r'^(.+?)\s+by\s+(.+)$', name, re.IGNORECASE)
    if match:
        title = match.group(1).strip()
        author = match.group(2).strip()
        author = clean_author(author)
        title = clean_title_suffix(title)
        return title, author, ext
    
    # Pattern: "书名_作者" (only one underscore, and right part looks like author)
    if '_' in name:
        parts = name.rsplit('_', 1)
        if len(parts) == 2:
            potential_title = parts[0].strip()
            potential_author = parts[1].strip()
            # Check if right part looks like an author (not a language code or date)
            if (len(potential_author) < 20 and
                potential_author not in ('en', 'zh', 'cn') and
                not re.match(r'^\d{4}', potential_author) and
                not re.match(r'^\d{4}-\d{4}$', potential_author)):
                title = clean_title_suffix(potential_title)
                author = clean_author(potential_author)
                return title, author, ext
    
    # Pattern: "书名-作者" (dash separator, only if author part is short Chinese name)
    match = re.match(r'^(.+?)-([\u4e00-\u9fa5]{2,4})$', name)
    if match:
        potential_title = match.group(1).strip()
        potential_author = match.group(2).strip()
        title = clean_title_suffix(potential_title)
        author = clean_author(potential_author)
        return title, author, ext
    
    # Pattern: "书名 (作者)" or "书名 （作者）"
    match = re.match(r'^(.+?)\s*[\(（]([^)）]+?)[\)）]\s*$', name)
    if match:
        potential_title = match.group(1).strip()
        potential_author = match.group(2).strip()
        # Exclude edition/version info and date ranges
        if (len(potential_author) < 30 and
            not any(c in potential_author for c in ['版', '册', '卷', '增补', '套装']) and
            not re.match(r'^\d{4}', potential_author) and
            not re.match(r'^\d{4}-\d{4}$', potential_author)):
            title = clean_title_suffix(potential_title)
            author = clean_author(potential_author)
            return title, author, ext
    
    # No author found, just clean the title
    title = clean_title_suffix(name)
    return title, author, ext


def generate_unique_id(title, author, filename, used_ids):
    """Generate a unique ID from title and author."""
    # Build base from title
    clean_t = re.sub(r'[^\w\s]', '', title)
    clean_t = re.sub(r'\s+', '-', clean_t.strip()).lower()
    
    # Build base from author if available
    if author:
        clean_a = re.sub(r'[^\w\s]', '', author)
        clean_a = re.sub(r'\s+', '-', clean_a.strip()).lower()
        base_id = f"{clean_t}-{clean_a}" if clean_t else clean_a
    else:
        base_id = clean_t
    
    # Clean non-alphanumeric except hyphens
    base_id = re.sub(r'[^a-z0-9-]', '', base_id.lower())
    base_id = re.sub(r'-+', '-', base_id).strip('-')
    
    # If too short or empty, use hash
    if not base_id or len(base_id) < 3:
        h = hashlib.md5(filename.encode()).hexdigest()[:8]
        base_id = f"book-{h}"
    
    # Ensure uniqueness
    unique_id = base_id
    counter = 2
    while unique_id in used_ids:
        unique_id = f"{base_id}-{counter}"
        counter += 1
    
    used_ids.add(unique_id)
    return unique_id


def get_summary(title, author):
    """Get summary for a book."""
    # Try exact match
    if title in BOOK_SUMMARIES:
        return BOOK_SUMMARIES[title]
    
    # Try partial match - check if any key is contained in title
    best_match = None
    best_len = 0
    for key, summary in BOOK_SUMMARIES.items():
        if key in title and len(key) > best_len:
            best_match = summary
            best_len = len(key)
    if best_match:
        return best_match
    
    # Try reverse - check if title is contained in any key
    for key, summary in BOOK_SUMMARIES.items():
        if title in key:
            return summary
    
    # Default summary
    return f"《{title}》是一部值得阅读的作品，为读者提供独特的视角与思考。"


def process_books():
    """Process all books and generate metadata JSON."""
    result = {}
    used_ids = set()
    
    if not os.path.exists(BOOKS_DIR):
        print(f"Directory not found: {BOOKS_DIR}")
        return
    
    for category in sorted(os.listdir(BOOKS_DIR)):
        category_path = os.path.join(BOOKS_DIR, category)
        if not os.path.isdir(category_path):
            continue
        
        books = []
        for filename in sorted(os.listdir(category_path)):
            filepath = os.path.join(category_path, filename)
            if not os.path.isfile(filepath):
                continue
            if filename in SKIP_FILES or filename.startswith('.'):
                continue
            
            title, author, ext = parse_filename(filename)
            book_id = generate_unique_id(title, author, filename, used_ids)
            summary = get_summary(title, author)
            
            book_entry = {
                "id": book_id,
                "title": title,
                "author": author,
                "year": None,
                "fileName": filename,
                "summary": summary
            }
            books.append(book_entry)
        
        if books:
            result[category] = books
    
    # Output JSON to books_metadata.json
    output_path = os.path.join(os.path.dirname(__file__), "books_metadata.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
        
    # Output JSON to books_data.json as well
    data_path = os.path.join(os.path.dirname(__file__), "books_data.json")
    with open(data_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"Generated {output_path} and {data_path}")
    print(f"Total categories: {len(result)}")
    print(f"Total books: {sum(len(v) for v in result.values())}")


if __name__ == "__main__":
    process_books()
