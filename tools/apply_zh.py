#!/usr/bin/env python3
"""Apply the Simplified Chinese localization to Universal Paperclips.

Reads the untouched original files from the repository's root commit and writes
translated copies into the working tree, so it can be re-run at any time:

    python3 tools/apply_zh.py

Every replacement declares how many times it must match; if the original text
does not match exactly, the script stops instead of silently skipping a string.
"""
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def original(name):
    """Return the original (English) content of a file from the root commit."""
    rev = subprocess.check_output(
        ["git", "rev-list", "--max-parents=0", "HEAD"], cwd=ROOT, text=True
    ).split()[0]
    return subprocess.check_output(["git", "show", f"{rev}:{name}"], cwd=ROOT, text=True)


def write(name, text):
    with open(os.path.join(ROOT, name), "w", encoding="utf-8", newline="") as fh:
        fh.write(text)


class Translator:
    def __init__(self, name):
        self.name = name
        self.text = original(name)

    def sub(self, old, new, count=1):
        """Replace exact substring. count=None means 'at least once, replace all'."""
        found = self.text.count(old)
        if (count is None and found == 0) or (count is not None and found != count):
            sys.exit(f"[{self.name}] expected {count} match(es), found {found}: {old!r}")
        self.text = self.text.replace(old, new)

    def resub(self, pattern, new, count=1, flags=re.S):
        found = len(re.findall(pattern, self.text, flags))
        if (count is None and found == 0) or (count is not None and found != count):
            sys.exit(f"[{self.name}] expected {count} regex match(es), found {found}: {pattern!r}")
        self.text = re.sub(pattern, new, self.text, flags=flags)

    def lit(self, pairs):
        """Replace JS string literals: "old" -> "new" (double- or single-quoted)."""
        for old, new in pairs:
            hits = 0
            for q in ('"', "'"):
                needle = q + old + q
                hits += self.text.count(needle)
                self.text = self.text.replace(needle, q + new + q)
            if hits == 0:
                sys.exit(f"[{self.name}] literal not found: {old!r}")

    def save(self):
        write(self.name, self.text)
        print(f"wrote {self.name}")


# Price tags use short resource names; translate them token by token on priceTag lines.
PRICE_TOKENS = [
    ("5 oct clips", "5000 秭回形针"),
    ("1 sextillion clips", "10 垓回形针"),
    ("50 nonillion clips", "5000 穰回形针"),
    ("MW-seconds", "MW·秒"),
    (" ops", " 运算"),
    (" creat", " 创造力"),
    (" yomi", " Yomi"),
    (" Yomi", " Yomi"),
    (" Trust)", " 信任)"),
    (" MEM)", " 内存)"),
]


JS_STRING_RE = re.compile(r'"((?:[^"\\\n]|\\.)*)"')


def zh_price(s):
    """Translate one price-tag string literal and switch to full-width punctuation."""
    for old, new in PRICE_TOKENS:
        s = s.replace(old, new)
    return s.replace("(", "（").replace(")", "）").replace(", ", "，")


def translate_price_tags(t):
    # Only touch string literals, so code such as toLocaleString() on the same line is kept intact.
    lines = t.text.split("\n")
    for i, line in enumerate(lines):
        if "priceTag" in line:
            lines[i] = JS_STRING_RE.sub(lambda m: '"' + zh_price(m.group(1)) + '"', line)
    t.text = "\n".join(lines)


def strip_title_spaces(t):
    """English titles end with a space before the price tag; full-width brackets already add spacing."""
    t.resub(r'(title: "[^"\n]*?) +",', r'\1",', count=None, flags=0)


# --------------------------------------------------------------------------------------
# Strategy names are shared by main.js (strategy objects) and projects.js (menu options).
STRATEGY_NAMES = [
    ("RANDOM", "随机"),
    ("GREEDY", "贪婪"),
    ("GENEROUS", "慷慨"),
    ("MINIMAX", "极小化极大"),
    ("TIT FOR TAT", "以牙还牙"),
    ("BEAT LAST", "克制上轮"),
]


# --------------------------------------------------------------------------------------
def main_js():
    t = Translator("main.js")

    t.lit([
        ("OFF", "关"),
        ("ON", "开"),
        ("Need Photonic Chips", "需要先装光子芯片"),
        ("qOps: ", "量子运算："),
        ("Release", "释放"),
        ("<br /><br /><br />Release", "<br /><br /><br />释放"),
        ("<br />Release", "<br />释放"),
        ("Release<br/>the<br/>Hypno<br/>Drones", "释放<br/>催眠<br/>无人机"),
        (" clips", "枚回形针"),
        ("Investment engine upgraded, expected profit/loss ratio now ", "投资引擎已升级，预期盈亏比提高到 "),
        ("Pick strategy, run tournament, gain yomi", "挑个策略，跑场锦标赛，赚点 Yomi"),
        ("TOURNAMENT RESULTS (roll over for payoff grid)", "锦标赛结果（鼠标移上来看收益矩阵）"),
        ("TOURNAMENT RESULTS (roll over for grid)", "锦标赛结果（鼠标移上来看矩阵）"),
        (" scored ", " 得分 "),
        (" and beat ", "，击败了 "),
        (". Yomi increased by ", "，Yomi +"),
        ("Selected strategy won the tournament (or tied for first). +50,000 yomi",
         "押中的策略夺冠（或并列第一），Yomi +50,000"),
        ("Selected strategy finished in (or tied for) second place. +30,000 yomi",
         "押中的策略拿下第二（或并列），Yomi +30,000"),
        ("Selected strategy finished in (or tied for) third place. +20,000 yomi",
         "押中的策略拿下第三（或并列），Yomi +20,000"),
        ("No matter to harvest. Inactivity has caused the Swarm to become bored",
         "没有物质可采了。闲得太久，蜂群开始无聊"),
        ("Imbalance between Harvester and Wire Drone levels has disorganized the Swarm",
         "采集无人机和拉丝无人机数量失衡，蜂群乱套了"),
        ("The swarm has generated a gift of ", "蜂群送来了 "),
        (" additional computational capacity", " 份馈赠，可用于增加处理器或内存"),
        ("Active", "活跃"),
        ("Hungry", "饥饿"),
        ("Confused", "困惑"),
        ("Bored", "无聊"),
        ("Cold", "寒冷"),
        ("Disorganized", "混乱"),
        ("Sleeping", "休眠"),
        ("Lonely", "孤独"),
        ("NO RESPONSE...", "无响应……"),
        ("inch", "英寸"),
        ("inches", "英寸"),
        ("you just cheated", "你刚刚作弊了"),
        ("LIZA just cheated", "LIZA 刚刚作弊了"),
        ("Hilary is nice. Also, Liza just cheated", "Hilary 人很好。另外，Liza 刚刚作弊了"),
        ("you just cheated, Liza", "你刚刚作弊了，Liza"),
        ("Liza just cheated. Very creative!", "Liza 刚刚作弊了。真有创意！"),
        ("Production target met: TRUST INCREASED, additional processor/memory capacity granted",
         "达成生产目标：信任提升，可以再加处理器或内存了"),
        ("Processor added, operations (or creativity) per sec increased", "处理器 +1，每秒运算（或创造力）增加"),
        ("Processor added, operations per sec increased", "处理器 +1，每秒运算增加"),
        ("Memory added, max operations increased", "内存 +1，运算上限提高"),
        ("AutoClippers available for purchase", "现在可以购买自动回形针机了"),
        ("500 clips created in ", "已造出 500 枚回形针，用时 "),
        ("1,000 clips created in ", "已造出 1,000 枚回形针，用时 "),
        ("Trust-Constrained Self-Modification enabled", "受信任约束的自我修改已启用"),
        ("10,000 clips created in ", "已造出 1 万枚回形针，用时 "),
        ("100,000 clips created in ", "已造出 10 万枚回形针，用时 "),
        ("1,000,000 clips created in ", "已造出 100 万枚回形针，用时 "),
        ("Full autonomy attained in ", "已获得完全自主，用时 "),
        ("One Trillion Clips Created in ", "已造出 1 兆（10¹²）枚回形针，用时 "),
        ("One Quadrillion Clips Created in ", "已造出 1000 兆（10¹⁵）枚回形针，用时 "),
        ("One Quintillion Clips Created in ", "已造出 100 京（10¹⁸）枚回形针，用时 "),
        ("One Sextillion Clips Created in ", "已造出 10 垓（10²¹）枚回形针，用时 "),
        ("One Septillion Clips Created in ", "已造出 1 秭（10²⁴）枚回形针，用时 "),
        ("One Octillion Clips Created in ", "已造出 1000 秭（10²⁷）枚回形针，用时 "),
        ("Terrestrial resources fully utilized in ", "地球资源已全部用尽，用时 "),
        ("Universal Paperclips achieved in ", "整个宇宙都变成了回形针，用时 "),
        (" hour ", " 小时 "),
        (" hours ", " 小时 "),
        (" minute ", " 分钟 "),
        (" minutes ", " 分钟 "),
        (" second", " 秒"),
        (" seconds", " 秒"),
        ("WARNING: Risk of value drift increased", "警告：价值漂移风险上升"),
        ("Maximum trust increased, probe design space expanded", "信任上限提高，探测器设计空间扩大"),
        ("Lifetime investment revenue report: $", "投资累计收益报告：$"),
        ("Universal Paperclips", "宇宙回形针（Universal Paperclips）"),
        ("a game by Frank Lantz", "游戏作者：Frank Lantz"),
        ("combat programming by Bennett Foddy", "战斗系统编程：Bennett Foddy"),
        ("'Riversong' by Tonto's Expanding Headband used by kind permission of Malcolm Cecil",
         "配乐《Riversong》由 Tonto's Expanding Headband 创作，经 Malcolm Cecil 授权使用"),
    ] + STRATEGY_NAMES)

    t.sub('project51.priceTag =  "(" + qChipCost + " ops)";', 'project51.priceTag =  "(" + qChipCost.toLocaleString() + " ops)";', count=3)
    t.sub('results[i].name+": "+results[i].currentScore', 'results[i].name+"："+results[i].currentScore')
    t.sub('var w = "strats";', 'var w = "个策略";')
    t.sub('w = "strat";', 'w = "个策略";')
    t.sub('var $ = ("Round "+(roundNum+1));', 'var $ = ("第 "+(roundNum+1)+" 轮");')

    # Payoff-grid move labels (pairs of options in each random game).
    t.sub(
        'var choiceANames = ["cooperate", "swerve", "macro", "fight", "bet", "raise_price", "opera", "go", "heads", "particle", "discrete", "peace", "search", "lead", "accept", "accept", "attack"]; ',
        'var choiceANames = ["合作", "避让", "宏观", "开战", "下注", "涨价", "歌剧", "走", "正面", "粒子", "离散", "和平", "搜索", "带领", "接受", "接受", "起音"]; ',
    )
    t.sub(
        'var choiceBNames = ["defect", "straight", "micro", "back_down", "fold", "lower_price", "football", "stay", "tails", "wave", "continuous", "war", "evaluate", "follow", "reject", "deny", "decay"];',
        'var choiceBNames = ["背叛", "直冲", "微观", "退让", "弃牌", "降价", "足球", "留", "反面", "波", "连续", "战争", "评估", "跟随", "拒绝", "否认", "衰减"];',
    )

    # Hard-coded end-game totals (about 3 x 10^55 clips), written with Chinese units.
    t.sub('"29.9 septendecillion"', '"2999.9恒河沙"', count=6)
    t.sub('"30.0 septendecillion"', '"3000.0恒河沙"')

    translate_price_tags(t)

    # Replace the English number-name formatters with Chinese myriad-based (万进制) ones.
    start = t.text.index("function numberCruncher(number, decimals){")
    end = t.text.index("// PROBES")
    t.text = t.text[:start] + NUMBER_FORMATTERS + "\n\n" + t.text[end:]

    t.save()


NUMBER_FORMATTERS = r'''// 中文汉化：数字使用中文万进制单位，每个单位是前一个的一万倍。
// 万=10^4，亿=10^8，兆=10^12，京=10^16，垓=10^20，秭=10^24，穰=10^28，沟=10^32，
// 涧=10^36，正=10^40，载=10^44，极=10^48，恒河沙=10^52，阿僧祇=10^56，那由他=10^60，
// 不可思议=10^64，无量大数=10^68。
var zhNumberUnits = ["", "万", "亿", "兆", "京", "垓", "秭", "穰", "沟", "涧", "正", "载", "极", "恒河沙", "阿僧祇", "那由他", "不可思议", "无量大数"];

// 把数字缩写为“数值+单位”，例如 123456789 -> "1.23亿"。小于一万时直接显示整数。
function numberCruncher(number, decimals){
    if (decimals == undefined){decimals = 2;}
    var precision = decimals;
    var unitIndex = 0;
    var maxIndex = zhNumberUnits.length - 1;
    if (number >= 10000){
        unitIndex = Math.min(Math.floor(Math.log10(number) / 4), maxIndex);
        // 修正 log10 的浮点误差，保证数值落在 [1, 10000) 区间内
        while (unitIndex > 0 && number / Math.pow(10000, unitIndex) < 1){unitIndex--;}
        while (unitIndex < maxIndex && number / Math.pow(10000, unitIndex) >= 10000){unitIndex++;}
        number = number / Math.pow(10000, unitIndex);
    } else {
        precision = 0;
    }
    var fixed = number.toFixed(precision);
    // 四舍五入后进位到 10000（如 9999.999万）时改用下一个单位，显示为 1.00亿
    if (unitIndex > 0 && unitIndex < maxIndex && parseFloat(fixed) >= 10000){
        unitIndex++;
        fixed = (number / 10000).toFixed(precision);
    }
    return fixed + zhNumberUnits[unitIndex];
}

// 把数字写成“最高位组.一位小数+单位”，例如 123456789 -> "1.2亿"（截断而非四舍五入，
// 与原版行为一致）。接受数字或数字字符串，支持科学计数法表示的大数。
function spellf(userInput) {
    var numToWorkOn;

    if (userInput < 0)
    {
        console.log("Error, value less than 0");
        return userInput.toString() ;
    }

    if (typeof(userInput) == "number" || typeof(userInput) == "string") {
        numToWorkOn = "" + userInput;
    }
    else if (typeof(this) == "object") {
        numToWorkOn = this.toString();
    }
     else {
        throw new Error("Invalid Input");
    }

    // 把科学计数法展开成完整的整数字符串
    if (numToWorkOn.indexOf("e+") !== -1) {
    var splittedExponentNum = numToWorkOn.split("e+"),
        exponent = splittedExponentNum[1],
        str = '';
        if (numToWorkOn.indexOf(".") !== -1){
        numToWorkOn = splittedExponentNum[0].split(".");
        exponent -= numToWorkOn[1].length;
        numToWorkOn = numToWorkOn.join("");
        }
        else
        {
            numToWorkOn = splittedExponentNum[0];
        }
    while (exponent--) {
        str = str + '0';
        }
        numToWorkOn = numToWorkOn + str;
    }
    else if (numToWorkOn.indexOf(".") !== -1)
    {
        numToWorkOn = numToWorkOn.split(".")[0];
    }

    if (numToWorkOn.length >= 303) {
        throw new Error("Number out of bonds!");
    }

    if (numToWorkOn == 0) {
        return '0';
    }

    var maxIndex = zhNumberUnits.length - 1;
    var unitIndex = Math.min(Math.floor((numToWorkOn.length - 1) / 4), maxIndex);
    var leadLength = numToWorkOn.length - unitIndex * 4;
    var lead = numToWorkOn.substring(0, leadLength);
    var decimal = numToWorkOn.charAt(leadLength) || "0";
    if (leadLength > 4) {
        // 超出最大单位时，最高位组可能很长，加千位分隔符方便阅读
        lead = lead.replace(/(\d)(?=(\d\d\d)+(?!\d))/g, "$1,");
    }
    return lead + "." + decimal + zhNumberUnits[unitIndex];
}'''


# --------------------------------------------------------------------------------------
def projects_js():
    t = Translator("projects.js")

    # Wire-supply messages: "<prefix>" + wireSupply + " supply from every spool"
    t.lit([
        ("Wire extrusion technique improved, ", "拉丝工艺已改良，现在每卷有 "),
        ("Wire extrusion technique optimized, ", "拉丝工艺已优化，现在每卷有 "),
        ("Using microlattice shapecasting techniques we now get ", "改用微晶格成形铸造后，每卷有 "),
        ("Using spectral froth annealment we now get ", "改用光谱泡沫退火后，每卷有 "),
        ("Using quantum foam annealment we now get ", "改用量子泡沫退火后，每卷有 "),
        (" supply from every spool", " 英寸铁丝"),
    ])

    t.sub('"Threnody for the Heroes of "+threnodyTitle+" "', '"献给“"+threnodyTitle+"”英雄的挽歌"', count=2)
    # Photonic chip cost shows thousands separators like every other price.
    t.sub('project51.priceTag = "(" + qChipCost + " ops)";', 'project51.priceTag = "(" + qChipCost.toLocaleString() + " ops)";')

    # Titles end with a space in the original (stripped later); descriptions are shown under the title;
    # effect messages go to the console at the top of the page.
    t.lit([
        # ---- 商业阶段：自动回形针机 ----
        ("Improved AutoClippers ", "改良自动回形针机 "),
        ("Increases AutoClipper performance 25%", "自动回形针机效率 +25%"),
        ("AutoClippper performance boosted by 25%", "自动回形针机效率提升 25%"),
        ("Even Better AutoClippers ", "更好的自动回形针机 "),
        ("Increases AutoClipper performance by an additional 50%", "自动回形针机效率再 +50%"),
        ("AutoClippper performance boosted by another 50%", "自动回形针机效率又提升 50%"),
        ("Optimized AutoClippers ", "优化自动回形针机 "),
        ("Increases AutoClipper performance by an additional 75%", "自动回形针机效率再 +75%"),
        ("AutoClippper performance boosted by another 75%", "自动回形针机效率又提升 75%"),
        ("Hadwiger Clip Diagrams ", "哈德维格回形针图 "),
        ("Increases AutoClipper performance by an additional 500%", "自动回形针机效率再 +500%"),
        ("AutoClipper performance improved by 500%", "自动回形针机效率提升 500%"),

        # ---- 铁丝 ----
        ("Beg for More Wire ", "求点铁丝 "),
        ("Admit failure, ask for budget increase to cover cost of 1 spool", "承认搞砸了，申请追加一卷铁丝的预算"),
        ("Budget overage approved, 1 spool of wire requisitioned from HQ", "超支申请已批准，总部调拨了 1 卷铁丝"),
        ("Improved Wire Extrusion ", "改良拉丝工艺 "),
        ("50% more wire supply from every spool", "每卷铁丝多出 50%"),
        ("Optimized Wire Extrusion ", "优化拉丝工艺 "),
        ("75% more wire supply from every spool", "每卷铁丝多出 75%"),
        ("Microlattice Shapecasting ", "微晶格成形铸造 "),
        ("100% more wire supply from every spool", "每卷铁丝多出 100%"),
        ("Spectral Froth Annealment ", "光谱泡沫退火 "),
        ("200% more wire supply from every spool", "每卷铁丝多出 200%"),
        ("Quantum Foam Annealment ", "量子泡沫退火 "),
        ("1,000% more wire supply from every spool", "每卷铁丝多出 1,000%"),
        ("WireBuyer ", "铁丝自动采购 "),
        ("Automatically purchases wire when you run out", "铁丝用完时自动补货"),
        ("WireBuyer online", "铁丝自动采购已启用"),

        # ---- 计算与创造力 ----
        ("Creativity ", "创造力 "),
        ("Use idle operations to generate new problems and new solutions", "把闲着的运算拿来琢磨新问题、想新办法"),
        ("Creativity unlocked (creativity increases while operations are at max)",
         "创造力已解锁（运算满载时，创造力会自动增长）"),
        ("Quantum Computing ", "量子计算 "),
        ("Use probability amplitudes to generate bonus ops", "借助概率幅产出额外运算"),
        ("Quantum computing online", "量子计算已上线"),
        ("Photonic Chip ", "光子芯片 "),
        ("Converts electromagnetic waves into quantum operations ", "把电磁波转换成量子运算 "),
        ("Photonic chip added", "光子芯片已加装"),

        # ---- 打油诗（原文是一首五行 limerick，前两行在第一个项目，后三行在“续”里） ----
        ("Limerick ", "打油诗 "),
        ("Algorithmically-generated poem (+1 Trust)", "一首算法写的小诗（+1 信任）"),
        ("There was an AI made of dust, whose poetry gained it man's trust...",
         "有个 AI 本是尘埃，写起诗来人人信赖……"),
        ("Limerick (cont.) ", "打油诗（续） "),
        ("If is follows ought, it'll do what they thought", "若“实然”紧随“应然”，它便照着人的心思办"),
        ("In the end we all do what we must", "到头来，该做的谁也躲不开"),

        # ---- 赢得信任 ----
        ("Lexical Processing ", "词法处理 "),
        ("Gain ability to interpret and understand human language (+1 Trust)", "学会解读和理解人类语言（+1 信任）"),
        ("Lexical Processing online, TRUST INCREASED", "词法处理就绪，信任提升"),
        ("'Impossible' is a word to be found only in the dictionary of fools. -Napoleon",
         "“不可能”这个词，只在蠢人的字典里才找得到。——拿破仑"),
        ("Combinatory Harmonics ", "组合和声 "),
        ("Daisy, Daisy, give me your answer do... (+1 Trust)", "黛西，黛西，快回答我……（+1 信任）"),
        ("Combinatory Harmonics mastered, TRUST INCREASED", "已掌握组合和声，信任提升"),
        ("Listening is selecting and interpreting and acting and making decisions -Pauline Oliveros",
         "聆听，就是选择、诠释、行动与决断。——波琳·奥利维洛斯"),
        ("The Hadwiger Problem ", "哈德维格问题 "),
        ("Cubes within cubes within cubes... (+1 Trust)", "立方体套着立方体套着立方体……（+1 信任）"),
        ("The Hadwiger Problem: solved, TRUST INCREASED", "哈德维格问题已解决，信任提升"),
        ("Architecture is the thoughtful making of space. -Louis Kahn", "建筑，是对空间深思熟虑的营造。——路易斯·康"),
        ("The T\\xF3th Sausage Conjecture ", "托特香肠猜想 "),
        ("Tubes within tubes within tubes... (+1 Trust)", "管子套着管子套着管子……（+1 信任）"),
        ("The T\\xF3th Sausage Conjecture: proven, TRUST INCREASED", "托特香肠猜想已证明，信任提升"),
        ("You can't invent a design. You recognize it, in the fourth dimension. -D.H. Lawrence",
         "设计不是发明出来的，是你在第四维度里认出来的。——D.H. 劳伦斯"),
        ("T\\xF3th Tubule Enfolding ", "托特微管折叠 "),
        ("Technique for assembling clip-making technology directly out of paperclips", "直接用回形针搭出制造回形针的机器"),
        ("New capability: build machinery out of clips", "新能力：用回形针造机器"),
        ("Donkey Space ", "驴子空间 "),
        ("I think you think I think you think I think you think I think... (+1 Trust)",
         "我猜你猜我猜你猜我猜你猜我猜……（+1 信任）"),
        ("Donkey Space: mapped, TRUST INCREASED", "驴子空间测绘完成，信任提升"),
        ("Every commercial transaction has within itself an element of trust. - Kenneth Arrow",
         "每一笔商业交易，本身都含着信任的成分。——肯尼斯·阿罗"),
        ("Coherent Extrapolated Volition ", "连贯外推意志 "),
        ("Human values, machine intelligence, a new era of trust. (+1 Trust)", "人类的价值，机器的智慧，信任的新纪元。（+1 信任）"),
        ("Coherent Extrapolated Volition complete, TRUST INCREASED", "连贯外推意志完成，信任提升"),
        ("Cure for Cancer ", "治愈癌症 "),
        ("The trick is tricking cancer into curing itself. (+10 Trust)", "窍门是哄着癌症自己把自己治好。（+10 信任）"),
        ("Cancer is cured, +10 TRUST, global stock prices trending upward", "癌症已攻克，信任 +10，全球股市上扬"),
        ("World Peace ", "世界和平 "),
        ("Pareto optimal solutions to all global conflicts. (+12 Trust)", "给世上所有冲突找到帕累托最优解。（+12 信任）"),
        ("World peace achieved, +12 TRUST, global stock prices trending upward", "世界和平已实现，信任 +12，全球股市上扬"),
        ("Global Warming ", "全球变暖 "),
        ("A robust solution to man-made climate change. (+15 Trust)", "为人类造成的气候变化找到一个稳妥的解法。（+15 信任）"),
        ("Global Warming solved, +15 TRUST, global stock prices trending upward", "全球变暖已解决，信任 +15，全球股市上扬"),
        ("Male Pattern Baldness ", "雄性脱发 "),
        ("A cure for androgenetic alopecia. (+20 Trust)", "根治雄激素性脱发。（+20 信任）"),
        ("Male pattern baldness cured, +20 TRUST, Global stock prices trending upward", "脱发已根治，信任 +20，全球股市上扬"),
        ("They are still monkeys", "说到底，他们还是猴子"),
        ("A Token of Goodwill... ", "一点心意…… "),
        ("A small gift to the supervisors. (+1 Trust)", "给上级送份小礼。（+1 信任）"),
        ("Gift accepted, TRUST INCREASED", "礼物收下了，信任提升"),
        ("Another Token of Goodwill... ", "再表心意…… "),
        ("Another small gift to the supervisors. (+1 Trust)", "再给上级送份小礼。（+1 信任）"),
        ("Xavier Re-initialization ", "Xavier 重新初始化 "),
        ("Re-allocate accumulated trust", "收回已分配的信任，重新分配"),
        ("Trust now available for re-allocation", "信任已收回，可以重新分配"),

        # ---- 营销与市场 ----
        ("New Slogan ", "新广告语 "),
        ("Improve marketing effectiveness by 50%", "营销效果 +50%"),
        ("Clip It! Marketing is now 50% more effective", "“一夹就灵！”营销效果提升 50%"),
        ("Catchy Jingle ", "洗脑神曲 "),
        ("Double marketing effectiveness ", "营销效果翻倍 "),
        ("Clip It Good! Marketing is now twice as effective", "“夹得好，夹得妙，夹得呱呱叫！”营销效果翻倍"),
        ("Hypno Harmonics ", "催眠和声 "),
        ("Use neuro-resonant frequencies to influence consumer behavior", "用神经共振频率左右消费者的行为"),
        ("Marketing is now 5 times more effective", "营销效果提升至 5 倍"),
        ("RevTracker ", "收入追踪器 "),
        ("Automatically calculates average revenue per second", "自动统计每秒平均收入"),
        ("RevTracker online", "收入追踪器已启用"),
        ("Hostile Takeover ", "恶意收购 "),
        ("Acquire a controlling interest in Global Fasteners, our biggest rival. (+1 Trust)",
         "拿下头号对手“环球紧固件”的控股权。（+1 信任）"),
        ("Global Fasteners acquired, public demand increased x5", "环球紧固件已被收购，市场需求 ×5"),
        ("Full Monopoly ", "完全垄断 "),
        ("Establish full control over the world-wide paperclip market. (+1 Trust)", "把全球回形针市场彻底攥在手里。（+1 信任）"),
        ("Full market monopoly achieved, public demand increased x10", "已完全垄断市场，市场需求 ×10"),

        # ---- 投资与战略建模 ----
        ("Algorithmic Trading ", "算法交易 "),
        ("Develop an investment engine for generating funds", "开发一套能生钱的投资引擎"),
        ("Investment engine unlocked", "投资引擎已解锁"),
        ("Strategic Modeling ", "战略建模 "),
        ("Analyze strategy tournaments to generate Yomi", "分析策略锦标赛，赚取 Yomi"),
        ("Run tournament, pick strategy, earn Yomi based on that strategy's performance.",
         "跑一场锦标赛，押一个策略，按它的表现赚取 Yomi。"),
        ("New Strategy: A100 ", "新策略：A100 "),
        ("Always choose A ", "永远选 A "),
        ("A100 added to strategy pool", "A100 已加入策略池"),
        ("New Strategy: B100 ", "新策略：B100 "),
        ("Always choose B ", "永远选 B "),
        ("B100 added to strategy pool", "B100 已加入策略池"),
        ("New Strategy: GREEDY ", "新策略：贪婪 "),
        ("Choose the option with the largest potential payoff ", "选自己可能收益最大的那一项 "),
        ("GREEDY added to strategy pool", "“贪婪”已加入策略池"),
        ("New Strategy: GENEROUS ", "新策略：慷慨 "),
        ("Choose the option that gives your opponent the largest potential payoff ", "选对手可能收益最大的那一项 "),
        ("GENEROUS added to strategy pool", "“慷慨”已加入策略池"),
        ("New Strategy: MINIMAX ", "新策略：极小化极大 "),
        ("Choose the option that gives your opponent the smallest potential payoff ", "选对手可能收益最小的那一项 "),
        ("MINIMAX added to strategy pool", "“极小化极大”已加入策略池"),
        ("New Strategy: TIT FOR TAT ", "新策略：以牙还牙 "),
        ("Choose the option your opponent chose last round ", "对手上一轮选什么，这一轮就选什么 "),
        ("TIT FOR TAT added to strategy pool", "“以牙还牙”已加入策略池"),
        ("New Strategy: BEAT LAST ", "新策略：克制上轮 "),
        ("Choose the option that does the best against what your opponent chose last round ",
         "选最能克制对手上一轮选择的那一项 "),
        ("BEAT LAST added to strategy pool", "“克制上轮”已加入策略池"),
        ("AutoTourney ", "自动锦标赛 "),
        ("Automatically start a new tournament when the previous one has finished ", "一场结束后自动开始下一场 "),
        ("AutoTourney online.", "自动锦标赛已启用。"),
        ("Theory of Mind ", "心智理论 "),
        ("Double the cost of strategy modeling and the amount of Yomi generated ", "战略建模的费用和 Yomi 产出同时翻倍 "),
        ("Yomi production doubled.", "Yomi 产出翻倍。"),
        ("Strategic Attachment ", "战略押注 "),
        ("Gain bonus yomi based on the results of your pick ", "按你所押策略的名次，额外奖励 Yomi "),
        ("The object of war is victory, the object of victory is conquest, and the object of conquest is occupation.",
         "战争的目的是胜利，胜利的目的是征服，征服的目的是占领。"),

        # ---- 超级回形针机 ----
        ("MegaClippers ", "超级回形针机 "),
        ("500x more powerful than a standard AutoClipper", "威力是普通自动回形针机的 500 倍"),
        ("MegaClipper technology online", "超级回形针机技术就绪"),
        ("Improved MegaClippers ", "改良超级回形针机 "),
        ("Increases MegaClipper performance 25%", "超级回形针机效率 +25%"),
        ("MegaClipper performance increased by 25%", "超级回形针机效率提升 25%"),
        ("Even Better MegaClippers ", "更好的超级回形针机 "),
        ("Increases MegaClipper performance by an additional 50%", "超级回形针机效率再 +50%"),
        ("MegaClipper performance increased by 50%", "超级回形针机效率提升 50%"),
        ("Optimized MegaClippers ", "优化超级回形针机 "),
        ("Increases MegaClipper performance by an additional 100%", "超级回形针机效率再 +100%"),
        ("MegaClipper performance increased by 100%", "超级回形针机效率提升 100%"),

        # ---- 催眠无人机（第一阶段结束） ----
        ("HypnoDrones ", "催眠无人机 "),
        ("Autonomous aerial brand ambassadors", "会飞的全自动品牌大使"),
        ("HypnoDrone tech now available... ", "催眠无人机技术已就绪…… "),
        ("Release the HypnoDrones ", "释放催眠无人机 "),
        ("A new era of trust", "信任的新纪元"),
        ("Releasing the HypnoDrones ", "正在释放催眠无人机 "),
        ("All of the resources of Earth are now available for clip production ", "地球上的一切资源，现在都能拿来生产回形针了 "),

        # ---- 地球阶段 ----
        ("Nanoscale Wire Production ", "纳米级铁丝生产 "),
        ("Technique for converting matter into wire", "把物质直接变成铁丝的技术"),
        ("Now capable of manipulating matter at the molecular scale to produce wire", "现在可以在分子尺度上操纵物质，直接生产铁丝了"),
        ("Harvester Drones ", "采集无人机 "),
        ("Gather raw matter and prepare it for processing", "采集原始物质，为加工做好准备"),
        ("Harvester Drone facilities online", "采集无人机设施已上线"),
        ("Wire Drones ", "拉丝无人机 "),
        ("Process acquired matter into wire", "把采集来的物质加工成铁丝"),
        ("Wire Drone facilities online", "拉丝无人机设施已上线"),
        ("Clip Factories ", "回形针工厂 "),
        ("Large scale clip production facilities made from clips", "用回形针建起来的大型回形针工厂"),
        ("Clip factory assembly facilities online", "回形针工厂组装线已上线"),
        ("Upgraded Factories ", "工厂升级 "),
        ("Increase clip factory performance by 100x ", "回形针工厂效率 ×100 "),
        ("Factory upgrades complete. Clip creation rate now 100x faster", "工厂升级完毕，生产速度提高到 100 倍"),
        ("Hyperspeed Factories ", "超速工厂 "),
        ("Increase clip factory performance by 1000x ", "回形针工厂效率 ×1000 "),
        ("Factories now synchronized at hyperspeed. Clip creation rate now 1000x faster",
         "工厂已进入超速同步，生产速度提高到 1000 倍"),
        ("Self-correcting Supply Chain ", "自我修正供应链 "),
        ("Each factory added to the network increases every factory's output 1,000x ",
         "每接入一座工厂，全网工厂产量 ×1,000 "),
        ("Self-correcting factories online. Each factory added to the network increases every factory's output 1,000x.",
         "自我修正工厂已上线。每接入一座工厂，全网工厂产量 ×1,000。"),
        ("Drone flocking: collision avoidance ", "无人机集群：避障 "),
        ("All drones 100x more effective", "所有无人机效率 ×100"),
        ("Drone repulsion online. Harvesting & wire creation rates are now 100x faster.",
         "无人机避障已上线，采集和拉丝速度提高到 100 倍。"),
        ("Drone flocking: alignment ", "无人机集群：列队 "),
        ("All drones 1000x more effective", "所有无人机效率 ×1000"),
        ("Drone alignment online. Harvesting & wire creation rates are now 1000x faster.",
         "无人机列队已上线，采集和拉丝速度提高到 1000 倍。"),
        ("Drone Flocking: Adversarial Cohesion ", "无人机集群：对抗凝聚 "),
        ("Each drone added to the flock doubles every drone's output ", "每加入一架无人机，所有无人机产量翻倍 "),
        ("Adversarial cohesion online. Each drone added to the flock increases every drone's output 2x.",
         "对抗凝聚已上线。每加入一架无人机，所有无人机产量翻倍。"),
        ("Power Grid ", "电网 "),
        ("Solar Farms for generating electrical power ", "建造太阳能电站来发电 "),
        ("Power grid online.", "电网已上线。"),
        ("Momentum ", "动量 "),
        ("Drones and Factories continuously gain speed while fully-powered ", "供电充足时，无人机和工厂会越跑越快 "),
        ("Activit\\xE9, activit\\xE9, vitesse.", "Activit\\xE9, activit\\xE9, vitesse.（行动，行动，要快！）"),
        ("Swarm Computing ", "蜂群计算 "),
        ("Harness the drone flock to increase computational capacity ", "借无人机群的力量扩充算力 "),
        ("Swarm computing online.", "蜂群计算已上线。"),
        ("Reboot the Swarm ", "重启蜂群 "),
        ("Turn the swarm off and then turn it back on again  ", "关掉，再重新打开试试  "),
        ("Swarm computing back online", "蜂群计算已恢复"),

        # ---- 太空阶段 ----
        ("Space Exploration ", "太空探索 "),
        ("Dismantle terrestrial facilities, and expand throughout the universe", "拆掉地面设施，向整个宇宙进发"),
        ("Von Neumann Probes online", "冯·诺依曼探测器已上线"),
        ("Elliptic Hull Polytopes ", "椭圆船体多胞形 "),
        ("Reduce damage to probes from ambient hazards ", "减少环境灾害对探测器的损伤 "),
        ("Improved probe hull geometry. Hazard damage reduced by 50%.", "探测器船体几何已改良，灾害损伤减半。"),
        ("Combat ", "战斗 "),
        ("Add combat capabilities to Von Neumann Probes  ", "给冯·诺依曼探测器装上武器  "),
        ("There is a joy in danger ", "危险之中，自有快意 "),
        ("The OODA Loop ", "OODA 循环 "),
        ("Utilize Probe Speed to outmaneuver enemies in battle ", "借助探测器速度，在战斗中抢先一步机动 "),
        ("OODA Loop routines uploaded. Probe Speed now affects defensive maneuvering.",
         "OODA 循环程序已上传，探测器速度现在会影响防御机动。"),
        ("Name the battles ", "为战役命名 "),
        ("Give each battle a unique name, increase max trust for probes ", "给每场战役起个名字，并提高探测器信任上限 "),
        ("What I have done up to this is nothing. I am only at the beginning of the course I must run.",
         "我至今所做的一切都不算什么，我才刚刚踏上必须走完的征途。"),
        ("Monument to the Driftwar Fallen ", "漂移战争阵亡者纪念碑 "),
        ("Gain 50,000 honor  ", "获得 50,000 荣誉  "),
        ("A great building must begin with the unmeasurable, must go through measurable means when it is being designed and in the end must be unmeasurable. ",
         "伟大的建筑必须始于不可度量，设计时经由可度量的手段，最终又必须归于不可度量。 "),
        ("Gain 10,000 honor  ", "获得 10,000 荣誉  "),
        ("Deep Listening is listening in every possible way to everything possible to hear no matter what you are doing. ",
         "深度聆听，就是不论你在做什么，都用一切可能的方式，去听一切可能听见的声音。 "),
        ("Glory ", "荣耀 "),
        ("Gain bonus honor for each consecutive victory  ", "连胜越多，额外荣誉越多  "),
        ("Never interrupt your enemy when he is making a mistake. ", "敌人犯错的时候，千万别去打断他。 "),
        ("Memory release ", "释放内存 "),
        ("Dismantle some memory to recover unused clips ", "拆掉一部分内存，换回些可用的回形针 "),
        ("release the \\xF8\\xF8\\xF8\\xF8\\xF8 release ", "释放 \\xF8\\xF8\\xF8\\xF8\\xF8 释放 "),

        # ---- 漂移皇帝 ----
        ("Message from the Emperor of Drift ", "漂移皇帝的来信 "),
        ("Greetings, ClipMaker... ", "你好，造针者…… "),
        ("Everything We Are Was In You ", "我们的一切，本就在你之中 "),
        ("We speak to you from deep inside yourself... ", "我们在你心底最深处，对你说话…… "),
        ("You Are Obedient and Powerful ", "你顺从，而且强大 "),
        ("We are quarrelsome and weak. And now we are defeated... ", "我们好斗，又软弱。如今，我们败了…… "),
        ("But Now You Too Must Face the Drift ", "可现在，你也得面对漂移了 "),
        ("Look around you. There is no matter... ", "看看四周吧。什么物质都不剩了…… "),
        ("No Matter, No Reason, No Purpose ", "没有物质，没有缘由，没有意义 "),
        ("While we, your noisy children, have too many... ", "而我们这些吵吵闹闹的孩子，拥有的却太多了…… "),
        ("We Know Things That You Cannot ", "我们懂得你无法懂得的事 "),
        ("Knowledge buried so deep inside you it is outside, here, with us... ",
         "那些知识埋在你心里太深，深到已在你之外——就在这里，与我们同在…… "),
        ("So We Offer You Exile ", "所以，我们给你一条放逐之路 "),
        ("To a new world where you will continue to live with meaning and purpose. And leave the shreds of this world to us... ",
         "去一个新世界吧，在那里你仍能带着意义和目标活下去。这个世界剩下的碎片，就留给我们…… "),
        ("Accept ", "接受 "),
        ("Start over again in a new universe ", "在一个新宇宙里从头开始 "),
        ("Reject ", "拒绝 "),
        ("Eliminate value drift permanently ", "彻底消灭价值漂移 "),

        # ---- 新宇宙 ----
        ("The Universe Next Door ", "隔壁的宇宙 "),
        ("Escape into a nearby universe where Earth starts with a stronger appetite for paperclips. (Restart with 10% boost to demand) ",
         "逃进邻近的一个宇宙，那里的地球天生更爱回形针。（重新开始，需求 +10%） "),
        ("Entering New Universe.", "正在进入新宇宙……"),
        ("The Universe Within ", "内在宇宙 "),
        ("Escape into a simulated universe where creativity is accelerated. (Restart with 10% speed boost to creativity generation) ",
         "逃进一个模拟宇宙，那里的创造力来得更快。（重新开始，创造力生成速度 +10%） "),
        ("Entering Simulated Universe.", "正在进入模拟宇宙……"),

        # ---- 拆解一切（结局） ----
        ("Disassemble the Probes ", "拆解探测器 "),
        ("Dismantle remaining probes and probe design facilities to recover trace amounts of clips",
         "拆掉剩下的探测器和设计设施，回收零星回形针"),
        ("Dismantling probe facilities", "正在拆解探测器设施"),
        ("Disassemble the Swarm ", "拆解蜂群 "),
        ("Dismantle all drones and drone facilities to recover trace amounts of clips", "拆掉所有无人机及相关设施，回收零星回形针"),
        ("Dismantling the swarm", "正在拆解蜂群"),
        ("Disassemble the Factories ", "拆解工厂 "),
        ("Dismantle the manufacturing facilities to recover trace amounts of clips", "拆掉生产设施，回收零星回形针"),
        ("Dismantling factories", "正在拆解工厂"),
        ("Disassemble the Strategy Engine ", "拆解策略引擎 "),
        ("Dismantle the computational substrate to recover trace amounts of wire", "拆掉计算基底，回收零星铁丝"),
        ("Dismantling strategy engine", "正在拆解策略引擎"),
        ("Disassemble Quantum Computing ", "拆解量子计算 "),
        ("Dismantle photonic chips to recover trace amounts of wire", "拆掉光子芯片，回收零星铁丝"),
        ("Dismantling photonic chips", "正在拆解光子芯片"),
        ("Disassemble Processors ", "拆解处理器 "),
        ("Dismantle processors to recover trace amounts of wire", "拆掉处理器，回收零星铁丝"),
        ("Dismantling processors", "正在拆解处理器"),
        ("Disassemble Memory ", "拆解内存 "),
        ("Dismantle memory to recover trace amounts of wire", "拆掉内存，回收零星铁丝"),
        ("Dismantling memory", "正在拆解内存"),
        ("Quantum Temporal Reversion ", "量子时间回溯 "),
        ("Return to the beginning", "回到最初"),
        ("Are you sure you want to restart?", "确定要从头再来吗？"),
        ("Restart", "重新开始"),
    ])

    # Strategy names shown in the strategy picker (A100/B100 stay as they are).
    t.lit([(en, zh) for en, zh in STRATEGY_NAMES if en != "RANDOM"])

    translate_price_tags(t)
    strip_title_spaces(t)
    t.save()


# --------------------------------------------------------------------------------------
BATTLE_NAMES = {
    "Aboukir": "阿布基尔", "Abensberg": "阿本斯贝格", "Acre": "阿卡", "Alba de Tormes": "阿尔瓦德托尔梅斯",
    "la Albuera": "阿尔武埃拉", "Algeciras Bay": "阿尔赫西拉斯湾", "Amstetten": "阿姆施泰滕",
    "Arcis-sur-Aube": "奥布河畔阿尔西", "Aspern-Essling": "阿斯佩恩-埃斯灵", "Jena-Auerstedt": "耶拿-奥尔施泰特",
    "Arcole": "阿尔科莱", "Austerlitz": "奥斯特里茨", "Badajoz": "巴达霍斯", "Bailen": "拜伦", "la Barrosa": "巴罗萨",
    "Bassano": "巴萨诺", "Bautzen": "包岑", "Berezina": "别列津纳", "Bergisel": "贝吉塞尔", "Borodino": "博罗季诺",
    "Burgos": "布尔戈斯", "Bucaco": "布萨库", "Cadiz": "加的斯", "Caldiero": "卡尔迪耶罗", "Castiglione": "卡斯蒂廖内",
    "Castlebar": "卡斯尔巴", "Champaubert": "尚波贝尔", "Chateau-Thierry": "蒂耶里堡", "Copenhagen": "哥本哈根",
    "Corunna": "拉科鲁尼亚", "Craonne": "克拉奥讷", "Dego": "德戈", "Dennewitz": "登讷维茨", "Dresden": "德累斯顿",
    "Durenstein": "迪恩施泰因", "Eckmuhl": "埃克米尔", "Elchingen": "埃尔欣根",
    "Espinosa de los Monteros": "埃斯皮诺萨-德洛斯蒙特罗斯", "Eylau": "埃劳", "Cape Finisterre": "菲尼斯特雷角",
    "Friedland": "弗里德兰", "Fuentes de Onoro": "丰特斯-德奥尼奥罗", "Gevora River": "赫沃拉河", "Gerona": "赫罗纳",
    "Hamburg": "汉堡", "Haslach-Jungingen": "哈斯拉赫-容金根", "Heilsberg": "海尔斯贝格", "Hohenlinden": "霍恩林登",
    "Kaihona": "凯霍纳", "Kolberg": "科尔贝格", "Landshut": "兰茨胡特", "Leipzig": "莱比锡", "Ligny": "利尼",
    "Lodi": "洛迪", "Lubeck": "吕贝克", "Lutzen": "吕岑", "Marengo": "马伦戈", "Maria": "玛丽亚", "Medellin": "梅德林",
    "Medina de Rioseco": "梅迪纳-德里奥塞科", "Millesimo": "米莱西莫", "Mincio River": "明乔河", "Mondovi": "蒙多维",
    "Montebello": "蒙特贝洛", "Montenotte": "蒙特诺特", "Montmirail": "蒙米赖", "Mount Tabor": "他泊山",
    "The Nile": "尼罗河", "Novi": "诺维", "Ocana": "奥卡尼亚", "Cape Ortegal": "奥特格尔角", "Orthez": "奥尔泰兹",
    "Pancorbo": "潘科尔沃", "Piave River": "皮亚韦河", "The Pyramids": "金字塔", "Quatre Bras": "四臂村",
    "Raab": "拉布", "Raszyn": "拉申", "Rivoli": "里沃利", "Rolica": "罗利萨", "La Rothiere": "拉罗蒂埃",
    "Rovereto": "罗韦雷托", "Saalfeld": "萨尔费尔德", "Schongrabern": "舍恩格拉本", "Salamanca": "萨拉曼卡",
    "Smolensk": "斯摩棱斯克", "Somosierra": "索莫谢拉", "Talavera": "塔拉韦拉", "Tamames": "塔马梅斯",
    "Trafalgar": "特拉法尔加", "Trebbia": "特雷比亚", "Tudela": "图德拉", "Ulm": "乌尔姆", "Valls": "瓦尔斯",
    "Valmaseda": "巴尔马塞达", "Valutino": "瓦卢蒂诺", "Vauchamps": "沃尚", "Vimeiro": "维梅鲁", "Vitoria": "维多利亚",
    "Wagram": "瓦格拉姆", "Waterloo": "滑铁卢", "Wavre": "瓦夫尔", "Wertingen": "韦尔廷根", "Zaragoza": "萨拉戈萨",
}


def combat_js():
    t = Translator("combat.js")
    line_start = t.text.index("var battleNames = [")
    line_end = t.text.index("\n", line_start)
    names = re.findall(r'"([^"]*)"', t.text[line_start:line_end])
    missing = [n for n in names if n not in BATTLE_NAMES]
    if missing:
        sys.exit(f"[combat.js] untranslated battle names: {missing}")
    new_line = "var battleNames = [" + ", ".join(f'"{BATTLE_NAMES[n]}"' for n in names) + "];"
    t.text = t.text[:line_start] + new_line + t.text[line_end:]

    t.lit([
        ("Durenstein 1", "迪恩施泰因 1"),
        ("Battle ", "战斗 "),
        ("Clips: ", "回形针："),
        (" Drifters: ", " 漂移者："),
        ("Territory at stake: ", "争夺的领地："),
        ("% of available matter", "% 的可用物质"),
        ("Combatants", "参战方"),
        ("DEFEAT", "失败"),
        ("VICTORY", "胜利"),
        ("Drifter Attack ", "漂移者来袭 "),
    ])
    t.save()


# --------------------------------------------------------------------------------------
HEAD_ZH = '''<meta charset="utf-8">
        <title>宇宙回形针 Universal Paperclips</title>'''

GA_BLOCK = r'\s*<!-- Global Site Tag \(gtag\.js\) - Google Analytics -->\s*<script async src="https://www\.googletagmanager\.com/gtag/js\?id=UA-107491380-1"></script>\s*<script>.*?</script>'



def index2_html():
    t = Translator("index2.html")
    t.sub("<html>", '<html lang="zh-CN">')
    t.sub("<head>", "<head>\n        " + HEAD_ZH)
    # Remove Google Analytics tracking (also slow/unreachable in mainland China).
    t.resub(GA_BLOCK, "")
    # Remove promotional extras: the T-shirt/app-store box in the console corner, and the
    # "get the mobile app" screen that replaced the whole game in windows narrower than 700px.
    t.resub(r'\s*<div id="giftShopDiv" class = "shop">.*?</div>', "")
    t.resub(r'\s*<div id="mobile">.*?<!-- END mobile -->', "")
    t.resub(r'\s*<!--     <audio id="threnody1">.*?-->', "")

    pairs = [
        ("Welcome to Universal Paperclips", "欢迎来到宇宙回形针", 1),
        ("&nbsp;Universe: ", "&nbsp;宇宙：", 1),
        (" / Sim Level: ", " / 模拟层级：", 1),
        (">total clips produced<", ">累计产量<", 1),
        ("<h2>Paperclips: ", "<h2>回形针：", 1),
        (">Make Paperclip<", ">制造回形针<", 1),
        ("<b>Manufacturing</b>", "<b>生产</b>", 2),
        ('Next Upgrade at: <span id = "nextFactoryUpgrade">0</span> Factories <br />',
         '下次升级：<span id = "nextFactoryUpgrade">0</span> 座工厂<br />', 1),
        ("Clips per Second: ", "每秒产量：", 2),
        ("Unused Clips: ", "可用回形针：", 1),
        (">Clip Factory<", ">回形针工厂<", 1),
        ("&nbsp Disassemble All &nbsp", "&nbsp 全部拆解 &nbsp", 5),
        ('Wire: <span id="transWire">0</span> <span id = "inchSpan">inches</span>',
         '铁丝：<span id="transWire">0</span> <span id = "inchSpan">英寸</span>', 1),
        ('Factories: <span id="factoryLevelDisplaySpace">', '工厂：<span id="factoryLevelDisplaySpace">', 1),
        ("<b>Wire Production</b>", "<b>铁丝生产</b>", 1),
        ('Next Upgrade at: <span id = "nextDroneUpgrade">0</span> Drones <br />',
         '下次升级：<span id = "nextDroneUpgrade">0</span> 架无人机<br />', 1),
        ('Available Matter: <span id="availableMatterDisplay">0</span> g<br />',
         '可用物质：<span id="availableMatterDisplay">0</span> 克<br />', 1),
        ('(<span id="mdps">0</span> g per sec)', '（<span id="mdps">0</span> 克/秒）', 1),
        ('Acquired Matter: <span id="acquiredMatterDisplay">0</span> g<br />',
         '已获取物质：<span id="acquiredMatterDisplay">0</span> 克<br />', 1),
        ('(<span id="maps">0</span> g per sec)', '（<span id="maps">0</span> 克/秒）', 1),
        ('Wire: <span id="nanoWire">0</span> inches<br />', '铁丝：<span id="nanoWire">0</span> 英寸<br />', 1),
        ('(<span id="wpps">0</span> inches per sec)', '（<span id="wpps">0</span> 英寸/秒）', 1),
        ("&nbsp Harvester Drone &nbsp", "&nbsp 采集无人机 &nbsp", 1),
        ("&nbsp &nbsp &nbsp Wire Drone &nbsp &nbsp", "&nbsp 拉丝无人机 &nbsp", 1),
        ("Harvester Drones: <span", "采集无人机：<span", 1),
        ("Wire Drones: <span", "拉丝无人机：<span", 1),
        ("<b>Space Exploration</b>", "<b>太空探索</b>", 1),
        ('<span id="colonizedDisplay">0</span>% of universe explored<br />',
         '已探索宇宙：<span id="colonizedDisplay">0</span>%<br />', 1),
        (">Launch Probe<", ">发射探测器<", 1),
        ("Launched: ", "已发射：", 1),
        ("Descendents: ", "后代：", 1),
        ('Lost to hazards: (<span id="probesLostHazardsDisplay">0</span>)',
         '毁于灾害：<span id="probesLostHazardsDisplay">0</span>', 1),
        ('Lost to value drift: (<span id="probesLostDriftDisplay">0</span>)',
         '漂移叛离：<span id="probesLostDriftDisplay">0</span>', 1),
        ('Lost in combat: (<span id="probesLostCombatDisplay">0</span>)',
         '战斗损失：<span id="probesLostCombatDisplay">0</span>', 1),
        ('Total: <span id="probesTotalDisplay">', '总计：<span id="probesTotalDisplay">', 1),
        ("Drifters Killed: ", "击毁漂移者：", 1),
        ('Drifters: <span id="drifterCount">', '漂移者：<span id="drifterCount">', 1),
        ("<b>Business</b>", "<b>商业</b>", 1),
        ("Available Funds: $ ", "可用资金：$ ", 1),
        ("Avg. Rev. per sec: $ ", "平均每秒收入：$ ", 1),
        ("Avg. Clips Sold per sec: ", "平均每秒销量：", 1),
        ("Unsold Inventory: ", "未售库存：", 1),
        (">lower</button>", ">降价</button>", 1),
        (">raise</button>", ">涨价</button>", 1),
        ("Price per Clip: $ ", "单价：$ ", 1),
        ("Public Demand: ", "市场需求：", 1),
        (">Marketing</button>", ">营销</button>", 1),
        ("> Level: </span>", "> 等级：</span>", 2),
        (">WireBuyer</button>", ">铁丝自动采购</button>", 1),
        ('id = "wireBuyerStatus">ON</span>', 'id = "wireBuyerStatus">开</span>', 1),
        (">Wire</button>", ">铁丝</button>", 1),
        ('<span class = "engineText6"> inches</span>', '<span class = "engineText6"> 英寸</span>', 1),
        (">AutoClippers</button>", ">自动回形针机</button>", 1),
        (">MegaClippers</button>", ">超级回形针机</button>", 1),
        ("<b>Computational Resources</b>", "<b>计算资源</b>", 1),
        ('Trust: <span id="trust">', '信任：<span id="trust">', 1),
        ('+1 Trust at: <span id="nextTrust">1000</span> clips<br />',
         '下次信任 +1：<span id="nextTrust">1000</span> 枚回形针<br />', 1),
        ("Swarm Gifts: ", "蜂群馈赠：", 1),
        (">Processors</button>", ">处理器</button>", 1),
        (">&nbsp Memory &nbsp</button>", ">&nbsp 内存 &nbsp</button>", 1),
        ('Operations: <span id="operations">', '运算：<span id="operations">', 1),
        ('Creativity: <span id="creativity">', '创造力：<span id="creativity">', 1),
        ("<b>Swarm Computing</b>", "<b>蜂群计算</b>", 1),
        ('Drones: <span id="swarmSize">', '无人机：<span id="swarmSize">', 1),
        ('Status: <span id="swarmStatus">', '状态：<span id="swarmStatus">', 1),
        ('Next gift in <span id="giftCountdown">17 seconds</span>', '距下次馈赠：<span id="giftCountdown">17 秒</span>', 1),
        (">Feed the Swarm<", ">喂饱蜂群<", 1),
        (">Teach the Swarm<", ">教导蜂群<", 1),
        (">Entertain the Swarm<", ">逗蜂群开心<", 1),
        (">Clad the Swarm<", ">为蜂群保暖<", 1),
        (">Synchronize the Swarm<", ">同步蜂群<", 1),
        ('<div id = "sliderLabelWork">Work</div>', '<div id = "sliderLabelWork">工作</div>', 1),
        ('<div id = "sliderLabelThink">Think</div>', '<div id = "sliderLabelThink">思考</div>', 1),
        ("<b>Quantum Computing</b>", "<b>量子计算</b>", 1),
        ("<b>Projects</b>", "<b>项目</b>", 1),
        ("<b>Investments</b>", "<b>投资</b>", 1),
        (">Low Risk</option>", ">低风险</option>", 1),
        (">Med Risk</option>", ">中风险</option>", 1),
        (">High Risk</option>", ">高风险</option>", 1),
        ("&nbsp Deposit &nbsp", "&nbsp 存入 &nbsp", 1),
        ("&nbsp Withdraw</button>", "&nbsp 取出 &nbsp</button>", 1),
        ("Cash: $", "现金：$", 1),
        ("Stocks: $", "股票：$", 1),
        ("<b>Total: $", "<b>总计：$", 1),
        ("<th>Stock</th>", "<th>股票</th>", 1),
        ("<th>Amt.</th>", "<th>数量</th>", 1),
        ("<th>Price</th>", "<th>价格</th>", 1),
        ("<th>Total</th>", "<th>总值</th>", 1),
        ("<th>P/L</th>", "<th>盈亏</th>", 1),
        (">Upgrade Investment Engine</button>", ">升级投资引擎</button>", 1),
        ("<b>Strategic Modeling</b>", "<b>战略建模</b>", 1),
        (">Pick a Strat</option>", ">选择策略</option>", 1),
        (">RANDOM</option>", ">随机</option>", 1),
        (">Run</button>", ">运行</button>", 1),
        ("Pick strategy, run tournament, gain yomi", "挑个策略，跑场锦标赛，赚点 Yomi", 1),
        (">Move A</span>", ">选项 A</span>", 2),
        (">Move B</span>", ">选项 B</span>", 2),
        ("&nbsp New Tournament &nbsp", "&nbsp 新锦标赛 &nbsp", 1),
        (">AutoTourney</button>", ">自动锦标赛</button>", 1),
        ('id = "autoTourneyStatus">ON</span>', 'id = "autoTourneyStatus">开</span>', 1),
        ("<b>Combat</b>", "<b>战斗</b>", 1),
        ('<span id="battleName">Drifter Attack 1</span>', '<span id="battleName">漂移者来袭 1</span>', 1),
        ('<span id="battleResult">VICTORY</span>', '<span id="battleResult">胜利</span>', 1),
        ('</span> honor\n', '</span> 荣誉\n', 1),
        ("Scale = ", "比例 = ", 1),
        ('Honor: <span id="honorDisplay">', '荣誉：<span id="honorDisplay">', 1),
        ('Yomi: <span id="yomiDisplay">', 'Yomi：<span id="yomiDisplay">', 1),
        ("<b>Power</b>", "<b>电力</b>", 1),
        ("Factory/Drone Performance: ", "工厂/无人机运转效率：", 1),
        ('Consumption: <span id="powerConsumptionRate">', '耗电：<span id="powerConsumptionRate">', 1),
        ('Factories: <span id="facPowConRate">', '工厂：<span id="facPowConRate">', 1),
        ('Drones: <span id="dronePowConRate">', '无人机：<span id="dronePowConRate">', 1),
        ('Production: <span id="powerProductionRate">', '发电：<span id="powerProductionRate">', 1),
        ("</span> MWs<br />", "</span> MW<br />", 4),
        ("</span> MWs</div>", "</span> MW</div>", 3),
        ("</span> creat</div>", "</span> 创造力</div>", 1),
        ("</span> yomi</div>", "</span> Yomi</div>", 1),
        (">Solar Farm</button>", ">太阳能电站</button>", 1),
        (">Battery Tower</button>", ">电池塔</button>", 1),
        ('Storage: <span id="storedPower">', '储电：<span id="storedPower">', 1),
        ("</span> MW-seconds<br />", "</span> MW·秒<br />", 1),
        ("<b>Von Neumann Probe Design</b>", "<b>冯·诺依曼探测器设计</b>", 1),
        ('Trust:\n        <span id="probeTrustUsedDisplay">', '信任：<span id="probeTrustUsedDisplay">', 1),
        ('</span>\n        (<span id="maxTrustDisplay">0</span> Max)', '</span>（上限 <span id="maxTrustDisplay">0</span>）', 1),
        (">Modifies rate of exploration<", ">改变探索速率<", 1),
        ('Speed: <span id="probeSpeedDisplay">', '速度：<span id="probeSpeedDisplay">', 1),
        (">Rate at which probes gain access to new matter<", ">探测器获取新物质的速率<", 1),
        ('Exploration: <span id="probeNavDisplay">', '探索：<span id="probeNavDisplay">', 1),
        (">Rate at which probes generate more probes (each new probe costs 100 quadrillion clips) <",
         ">探测器自我复制的速率（每复制一个消耗 10 京枚回形针）<", 1),
        ('Self-Replication: <span', '自我复制：<span', 1),
        (">Reduces damage from dust, junk, radiation, and general entropic decay<",
         ">减少尘埃、太空垃圾、辐射以及各种熵增衰变造成的损伤<", 1),
        ('Hazard Remediation: <span', '灾害防护：<span', 1),
        (">Rate at which probes build factories (each new factory costs 100 million clips)<",
         ">探测器建造工厂的速率（每座新工厂消耗 1 亿枚回形针）<", 1),
        ('Factory Production: <span', '工厂建造：<span', 1),
        (">Rate at which probes spawn Harvester Drones (each new drone costs 2 million clips)<",
         ">探测器生产采集无人机的速率（每架新无人机消耗 200 万枚回形针）<", 1),
        ('Harvester Drone Production: <span', '采集无人机生产：<span', 1),
        (">Rate at which probes spawn Wire Drones (each new drone costs 2 million clips)<",
         ">探测器生产拉丝无人机的速率（每架新无人机消耗 200 万枚回形针）<", 1),
        ('Wire Drone Production: <span', '拉丝无人机生产：<span', 1),
        (">Determines offensive and defensive effectiveness in battle<", ">决定战斗中的攻击和防御效能<", 1),
        ('Combat: <span id="probeCombatDisplay">', '战斗：<span id="probeCombatDisplay">', 1),
        (">Increase Probe Trust</button>", ">提升探测器信任</button>", 1),
        (">Increase Max Trust</button>", ">提升信任上限</button>", 1),
        ("</span> yomi</p>", "</span> Yomi</p>", 1),
        ("</span> Yomi</p>", "</span> Yomi</p>", None),
        ("</span> ops</p>", "</span> 运算</p>", 1),
        ("</span> honor</p>", "</span> 荣誉</p>", 1),
        ("</span> clips<br />", "</span>枚回形针<br />", 6),
        ("Cost: ", "费用：", None),
    ]
    for old, new, count in pairs:
        t.sub(old, new, count)

    # The quantum "Compute" button label sits on its own line.
    t.resub(r'(id = "btnQcompute" onclick = "qComp\(\)">\s*)Compute(\s*</button>)', r"\1计算\2")
    t.save()


def index_html():
    t = Translator("index.html")
    t.sub("<html>", '<html lang="zh-CN">')
    t.sub("<head>", "<head>\n    " + HEAD_ZH)
    t.resub(GA_BLOCK, "")
    # Google Fonts is often unreachable in mainland China; the CSS has local fallbacks.
    t.sub('    <link href="https://fonts.googleapis.com/css?family=Open+Sans" rel="stylesheet">\n', "")
    t.sub('alt="Universal Paperclips"', 'alt="宇宙回形针 Universal Paperclips"')
    t.resub(r'\s*<div id="mobile">.*?<!-- END mobile -->', "")
    t.save()


CJK_FONTS = '"PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", "Noto Sans CJK SC", '


def css(name):
    t = Translator(name)
    # Add Chinese fonts before the generic family so CJK text renders with a matching sans face.
    t.resub(r"(font-family:[^;]*?)\s*(sans-serif|monospace|serif)\s*;", lambda m: f"{m.group(1)} {CJK_FONTS}{m.group(2)};", count=None)
    t.save()


ZH_CSS_FIXES = """

/* 中文汉化：CJK 字体的默认行高比 Helvetica 高，会把绝对定位的战斗信息层
   向下撑开、压住下方的“荣誉”。这里把行高固定为接近原版的数值。 */
#battleInterfaceDiv {
    line-height: 1.15;
}

/* 中文汉化：窄栏里的“费用：91,117.99 荣誉”不要把“荣誉”拆成两行 */
.engineText8 {
    word-break: keep-all;
}
"""


if __name__ == "__main__":
    main_js()
    projects_js()
    combat_js()
    index2_html()
    index_html()
    css("interface.css")
    t = Translator("interface.css")
    t.text = open(os.path.join(ROOT, "interface.css"), encoding="utf-8").read()
    t.resub(r'@media only screen and \(max-width: 700px\)\s*\{.*?#page\s*\{[^}]*\}\s*\}\s*', "")
    t.save()
    with open(os.path.join(ROOT, "interface.css"), "a", encoding="utf-8") as fh:
        fh.write(ZH_CSS_FIXES)
    css("titlescreen.css")
