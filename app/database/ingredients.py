from typing import Dict, List, Optional


ACTIVE_INGREDIENTS: Dict[str, Dict] = {
    "玻尿酸": {
        "aliases": ["透明质酸", "透明质酸钠", "hyaluronic acid", "sodium hyaluronate"],
        "benefits": ["保湿", "补水", "修复屏障"],
        "skin_types": ["干性", "油性", "混合性", "敏感性", "中性"],
        "efficacy_score": 85,
        "description": "强效保湿成分，能吸收自身1000倍水分"
    },
    "烟酰胺": {
        "aliases": ["维生素b3", "尼克酰胺", "niacinamide", "vitamin b3"],
        "benefits": ["美白", "控油", "收缩毛孔", "修复屏障"],
        "skin_types": ["油性", "混合性", "痘痘", "中性"],
        "efficacy_score": 90,
        "description": "多功能成分，美白控油双效"
    },
    "维生素C": {
        "aliases": ["抗坏血酸", "vc", "vitamin c", "ascorbic acid", "抗坏血酸葡糖苷", "3-o-乙基抗坏血酸"],
        "benefits": ["美白", "抗氧化", "提亮肤色", "促进胶原"],
        "skin_types": ["油性", "混合性", "中性", "暗沉"],
        "efficacy_score": 92,
        "description": "经典美白抗氧化成分"
    },
    "视黄醇": {
        "aliases": ["维生素a", "维a醇", "retinol", "vitamin a", "视黄醇棕榈酸酯"],
        "benefits": ["抗老", "去皱", "促进胶原", "疏通毛孔"],
        "skin_types": ["油性", "混合性", "中性", "成熟肌"],
        "efficacy_score": 95,
        "description": "抗老金标准，需建立耐受"
    },
    "神经酰胺": {
        "aliases": ["神经酰胺1", "神经酰胺3", "神经酰胺6ii", "ceramide"],
        "benefits": ["修复屏障", "保湿", "舒缓"],
        "skin_types": ["干性", "敏感性", "混合性", "中性"],
        "efficacy_score": 88,
        "description": "皮肤屏障天然组成成分"
    },
    "水杨酸": {
        "aliases": ["bha", "β-羟基酸", "salicylic acid", "beta hydroxy acid"],
        "benefits": ["去角质", "控油", "疏通毛孔", "祛痘"],
        "skin_types": ["油性", "痘痘", "混合性"],
        "efficacy_score": 85,
        "description": "油溶性酸类，深入毛孔清洁"
    },
    "果酸": {
        "aliases": ["aha", "α-羟基酸", "甘醇酸", "乳酸", "苹果酸", "alpha hydroxy acid", "glycolic acid", "lactic acid"],
        "benefits": ["去角质", "提亮", "促进代谢"],
        "skin_types": ["油性", "混合性", "中性", "暗沉"],
        "efficacy_score": 82,
        "description": "水溶性酸类，表皮焕肤"
    },
    "角鲨烷": {
        "aliases": ["角鲨烯", "squalane", "squalene"],
        "benefits": ["保湿", "修复", "抗氧化"],
        "skin_types": ["干性", "混合性", "敏感性", "中性"],
        "efficacy_score": 80,
        "description": "与人体皮脂结构相似"
    },
    "积雪草": {
        "aliases": ["积雪草苷", "羟基积雪草苷", "centella asiatica", "madecassoside"],
        "benefits": ["舒缓", "修复", "抗炎"],
        "skin_types": ["敏感性", "痘痘", "干性", "混合性", "中性"],
        "efficacy_score": 83,
        "description": "植物提取，舒缓修复"
    },
    "胶原蛋白": {
        "aliases": ["collagen", "水解胶原蛋白"],
        "benefits": ["保湿", "抗老", "紧致"],
        "skin_types": ["干性", "成熟肌", "混合性", "中性"],
        "efficacy_score": 78,
        "description": "保湿紧致，大分子主要停留在表皮"
    },
    "熊果苷": {
        "aliases": ["α-熊果苷", "β-熊果苷", "arbutin"],
        "benefits": ["美白", "提亮", "淡化色斑"],
        "skin_types": ["油性", "混合性", "中性", "暗沉"],
        "efficacy_score": 80,
        "description": "天然美白成分，温和抑制酪氨酸酶"
    },
    "曲酸": {
        "aliases": ["kojic acid"],
        "benefits": ["美白", "淡化色斑"],
        "skin_types": ["油性", "混合性", "中性"],
        "efficacy_score": 78,
        "description": "强效美白，可能致敏"
    },
    "维生素E": {
        "aliases": ["生育酚", "tocopherol", "vitamin e"],
        "benefits": ["抗氧化", "保湿", "修复"],
        "skin_types": ["干性", "敏感性", "中性", "成熟肌"],
        "efficacy_score": 75,
        "description": "脂溶性抗氧化剂"
    },
    "泛醇": {
        "aliases": ["维生素b5", "panthenol", "vitamin b5"],
        "benefits": ["保湿", "修复", "舒缓"],
        "skin_types": ["干性", "敏感性", "混合性", "中性"],
        "efficacy_score": 78,
        "description": "前维生素B5，保湿修复"
    },
    "茶树精油": {
        "aliases": ["tea tree oil", "互生叶白千层叶油"],
        "benefits": ["抗菌", "祛痘", "控油"],
        "skin_types": ["油性", "痘痘", "混合性"],
        "efficacy_score": 75,
        "description": "天然抗菌成分"
    },
    "胜肽": {
        "aliases": ["五胜肽", "六胜肽", "铜肽", "peptide", "palmitoyl pentapeptide-4"],
        "benefits": ["抗老", "紧致", "促进胶原"],
        "skin_types": ["成熟肌", "中性", "混合性", "干性"],
        "efficacy_score": 85,
        "description": "小分子信号肽"
    },
    "虾青素": {
        "aliases": ["astaxanthin"],
        "benefits": ["抗氧化", "抗老"],
        "skin_types": ["中性", "混合性", "成熟肌", "干性"],
        "efficacy_score": 88,
        "description": "超强抗氧化活性"
    },
    "传明酸": {
        "aliases": ["氨甲环酸", "tranexamic acid"],
        "benefits": ["美白", "抗炎", "淡化色斑"],
        "skin_types": ["敏感性", "中性", "混合性", "暗沉"],
        "efficacy_score": 85,
        "description": "温和美白抗炎成分"
    },
    "阿魏酸": {
        "aliases": ["ferulic acid"],
        "benefits": ["抗氧化", "稳定维C", "抗老"],
        "skin_types": ["中性", "混合性", "油性", "成熟肌"],
        "efficacy_score": 82,
        "description": "抗氧化增效成分"
    },
    "红没药醇": {
        "aliases": ["bisabolol"],
        "benefits": ["舒缓", "抗炎", "抗敏"],
        "skin_types": ["敏感性", "干性", "混合性", "中性"],
        "efficacy_score": 78,
        "description": "洋甘菊提取，舒缓抗炎"
    }
}


PRESERVATIVES: Dict[str, Dict] = {
    "苯氧乙醇": {
        "aliases": ["phenoxyethanol"],
        "safety_level": 2,
        "risk_description": "温和防腐剂，高浓度可能发热",
        "max_concentration": "1%"
    },
    "羟苯甲酯": {
        "aliases": ["尼泊金甲酯", "methylparaben"],
        "safety_level": 3,
        "risk_description": "尼泊金酯类，可能有类雌激素活性",
        "max_concentration": "0.4%"
    },
    "羟苯乙酯": {
        "aliases": ["尼泊金乙酯", "ethylparaben"],
        "safety_level": 3,
        "risk_description": "尼泊金酯类，可能有类雌激素活性",
        "max_concentration": "0.4%"
    },
    "羟苯丙酯": {
        "aliases": ["尼泊金丙酯", "propylparaben"],
        "safety_level": 4,
        "risk_description": "尼泊金酯类，类雌激素活性较强，敏感肌慎用",
        "max_concentration": "0.14%"
    },
    "羟苯丁酯": {
        "aliases": ["尼泊金丁酯", "butylparaben"],
        "safety_level": 4,
        "risk_description": "尼泊金酯类，类雌激素活性较强，敏感肌慎用",
        "max_concentration": "0.14%"
    },
    "甲基异噻唑啉酮": {
        "aliases": ["mit", "methylisothiazolinone"],
        "safety_level": 5,
        "risk_description": "强致敏性防腐剂，欧盟已限制驻留类产品使用",
        "max_concentration": "0.01%"
    },
    "甲基氯异噻唑啉酮": {
        "aliases": ["cmit", "methylchloroisothiazolinone"],
        "safety_level": 5,
        "risk_description": "强致敏性防腐剂，敏感肌高风险",
        "max_concentration": "0.0015%"
    },
    "咪唑烷基脲": {
        "aliases": ["imidazolidinyl urea"],
        "safety_level": 3,
        "risk_description": "甲醛释放体，可能刺激皮肤",
        "max_concentration": "0.6%"
    },
    "双咪唑烷基脲": {
        "aliases": ["diazolidinyl urea"],
        "safety_level": 3,
        "risk_description": "甲醛释放体，可能刺激皮肤",
        "max_concentration": "0.5%"
    },
    "DMDM乙内酰脲": {
        "aliases": ["dmdm hydantoin"],
        "safety_level": 3,
        "risk_description": "甲醛释放体，敏感肌需注意",
        "max_concentration": "0.6%"
    },
    "卡松": {
        "aliases": ["kathon cg", "甲基氯异噻唑啉酮/甲基异噻唑啉酮"],
        "safety_level": 5,
        "risk_description": "MIT/CMIT混合物，高致敏风险",
        "max_concentration": "0.0015%"
    },
    "辛酰羟肟酸": {
        "aliases": ["caprylhydroxamic acid"],
        "safety_level": 1,
        "risk_description": "新型温和防腐剂",
        "max_concentration": "0.5%"
    },
    "对羟基苯乙酮": {
        "aliases": ["p-hydroxyacetophenone"],
        "safety_level": 1,
        "risk_description": "温和防腐抗氧化成分",
        "max_concentration": "1%"
    },
    "己二醇": {
        "aliases": ["hexylene glycol"],
        "safety_level": 1,
        "risk_description": "多功能保湿防腐成分",
        "max_concentration": "5%"
    },
    "乙基己基甘油": {
        "aliases": ["ethylhexylglycerin"],
        "safety_level": 1,
        "risk_description": "温和防腐增效剂",
        "max_concentration": "1%"
    },
    "山梨酸钾": {
        "aliases": ["potassium sorbate"],
        "safety_level": 2,
        "risk_description": "食品级防腐剂，相对安全",
        "max_concentration": "0.6%"
    },
    "苯甲酸钠": {
        "aliases": ["sodium benzoate"],
        "safety_level": 2,
        "risk_description": "食品级防腐剂，酸性条件下有效",
        "max_concentration": "0.5%"
    },
    "氯苯甘醚": {
        "aliases": ["chlorphenesin"],
        "safety_level": 2,
        "risk_description": "温和防腐剂，少数人可能过敏",
        "max_concentration": "0.3%"
    }
}


RISK_INGREDIENTS: Dict[str, Dict] = {
    "酒精": {
        "aliases": ["乙醇", "alcohol", "ethanol", "sd alcohol", "alcohol denat"],
        "risk_level": 3,
        "risk_type": "刺激",
        "risk_description": "高浓度酒精可能破坏屏障，导致干燥敏感",
        "avoid_skin_types": ["干性", "敏感性"]
    },
    "香精": {
        "aliases": ["香料", "fragrance", "parfum"],
        "risk_level": 4,
        "risk_type": "致敏",
        "risk_description": "常见致敏原，敏感肌应避开",
        "avoid_skin_types": ["敏感性"]
    },
    "色素": {
        "aliases": ["色料", "着色剂", "colorant", "ci 19140", "ci 42090", "ci 16035", "red 4", "yellow 5", "blue 1"],
        "risk_level": 3,
        "risk_type": "致敏",
        "risk_description": "人工色素可能引起过敏",
        "avoid_skin_types": ["敏感性"]
    },
    "皂基": {
        "aliases": ["月桂酸", "肉豆蔻酸", "硬脂酸", "棕榈酸", "氢氧化钠", "氢氧化钾", "sodium laurate", "potassium myristate"],
        "risk_level": 3,
        "risk_type": "过度清洁",
        "risk_description": "强碱性清洁成分，过度清洁破坏屏障",
        "avoid_skin_types": ["干性", "敏感性"]
    },
    "SLS/SLES": {
        "aliases": ["月桂醇硫酸酯钠", "月桂醇聚醚硫酸酯钠", "sodium lauryl sulfate", "sodium laureth sulfate", "sles", "sls"],
        "risk_level": 4,
        "risk_type": "刺激",
        "risk_description": "强清洁力表面活性剂，刺激性较强",
        "avoid_skin_types": ["干性", "敏感性"]
    },
    "矿物油": {
        "aliases": ["液体石蜡", "矿油", "白油", "mineral oil", "petrolatum", "paraffinum liquidum"],
        "risk_level": 2,
        "risk_type": "闷痘",
        "risk_description": "纯度高的安全，但劣质产品可能致痘",
        "avoid_skin_types": ["油性", "痘痘"]
    },
    "凡士林": {
        "aliases": ["petroleum jelly", "vaseline"],
        "risk_level": 1,
        "risk_type": "闷痘",
        "risk_description": "纯度高时安全，封闭性强可能致痘",
        "avoid_skin_types": ["油性", "痘痘"]
    },
    "羊毛脂": {
        "aliases": ["lanolin"],
        "risk_level": 3,
        "risk_type": "致敏",
        "risk_description": "部分人对羊毛脂过敏",
        "avoid_skin_types": ["敏感性"]
    },
    "甲醛": {
        "aliases": ["formaldehyde"],
        "risk_level": 5,
        "risk_type": "致癌风险",
        "risk_description": "已被列为致癌物，禁止直接添加",
        "avoid_skin_types": ["所有肤质"]
    },
    "二苯酮": {
        "aliases": ["oxybenzone", "benzophenone-3", "二苯酮-3"],
        "risk_level": 4,
        "risk_type": "致敏/内分泌干扰",
        "risk_description": "化学防晒剂，可能致敏和影响内分泌",
        "avoid_skin_types": ["敏感性", "孕妇"]
    },
    "棕榈酸异丙酯": {
        "aliases": ["isopropyl palmitate"],
        "risk_level": 3,
        "risk_type": "致痘",
        "risk_description": "高致痘风险成分",
        "avoid_skin_types": ["油性", "痘痘"]
    },
    "肉豆蔻酸异丙酯": {
        "aliases": ["isopropyl myristate"],
        "risk_level": 3,
        "risk_type": "致痘",
        "risk_description": "高致痘风险成分",
        "avoid_skin_types": ["油性", "痘痘"]
    }
}


INGREDIENT_CONFLICTS: List[Dict] = [
    {
        "ingredients": ["维生素C", "烟酰胺"],
        "conflict_type": "降低效果",
        "severity": "medium",
        "description": "高浓度维C（pH<3.5）与烟酰胺同用可能转化为烟酸，引起刺激，建议错开时段或降低浓度",
        "alternative": "早C晚B（早上维C，晚上烟酰胺）"
    },
    {
        "ingredients": ["果酸", "水杨酸"],
        "conflict_type": "过度去角质",
        "severity": "high",
        "description": "两种酸类叠加可能过度去角质，破坏屏障，导致敏感泛红",
        "alternative": "隔天使用不同酸类，或选择含复合酸的单一产品"
    },
    {
        "ingredients": ["果酸", "视黄醇"],
        "conflict_type": "过度刺激",
        "severity": "high",
        "description": "均具有角质剥脱作用，叠加易引发红血丝、刺痛、脱皮",
        "alternative": "分别建立耐受后，一周各2-3次交替使用，或间隔至少12小时"
    },
    {
        "ingredients": ["水杨酸", "视黄醇"],
        "conflict_type": "过度刺激",
        "severity": "high",
        "description": "均有角质调理功效，叠加对屏障刺激大",
        "alternative": "酸类晚上用，视黄醇次日晚上用，间隔使用"
    },
    {
        "ingredients": ["维生素C", "视黄醇"],
        "conflict_type": "pH冲突",
        "severity": "medium",
        "description": "维C需要酸性环境，视黄醇在偏中性环境更稳定，同时使用可能降低效果",
        "alternative": "早C晚A（早上维C，晚上视黄醇）"
    },
    {
        "ingredients": ["苯甲酸钠", "维生素C"],
        "conflict_type": "生成有害物质",
        "severity": "high",
        "description": "特定条件下可能反应生成微量苯（致癌物）",
        "alternative": "避免同时使用含苯甲酸钠和高浓度维C的产品"
    },
    {
        "ingredients": ["酒精", "视黄醇"],
        "conflict_type": "加重刺激",
        "severity": "medium",
        "description": "酒精促渗但可能加重视黄醇的刺激性，破坏屏障",
        "alternative": "使用不含酒精的视黄醇产品"
    },
    {
        "ingredients": ["酒精", "果酸"],
        "conflict_type": "加重干燥",
        "severity": "medium",
        "description": "酒精挥发带走水分，加酸类去角质，双重干燥刺激",
        "alternative": "使用无酒精配方的酸类产品"
    },
    {
        "ingredients": ["皂基", "果酸"],
        "conflict_type": "中和失效",
        "severity": "medium",
        "description": "皂基呈强碱性，会中和果酸的酸性，使果酸失效",
        "alternative": "用氨基酸洁面后再用酸类产品"
    },
    {
        "ingredients": ["烟酰胺", "烟酰胺"],
        "conflict_type": "过度叠加",
        "severity": "low",
        "description": "多重烟酰胺叠加（>10%）可能刺激皮肤引起泛红",
        "alternative": "选择一款高浓度烟酰胺产品即可，总浓度建议3-5%"
    },
    {
        "ingredients": ["玻尿酸", "玻尿酸"],
        "conflict_type": "过度叠加",
        "severity": "low",
        "description": "多层玻尿酸叠加可能搓泥，大分子可能阻碍后续吸收",
        "alternative": "选择1-2款不同分子量玻尿酸产品即可"
    },
    {
        "ingredients": ["视黄醇", "视黄醇"],
        "conflict_type": "过度叠加",
        "severity": "high",
        "description": "多重视黄醇叠加易过度刺激，破坏皮肤屏障",
        "alternative": "只用一款视黄醇产品，从低浓度开始建立耐受"
    }
]


SKIN_TYPE_PROFILES: Dict[str, Dict] = {
    "干性": {
        "key_needs": ["保湿", "修复屏障", "抗氧化"],
        "avoid_ingredients": ["酒精", "皂基", "SLS/SLES", "果酸", "水杨酸"],
        "preferred_ingredients": ["玻尿酸", "神经酰胺", "角鲨烷", "泛醇", "积雪草", "维生素E", "胶原蛋白"],
        "sensitivity_level": 2
    },
    "油性": {
        "key_needs": ["控油", "疏通毛孔", "轻度去角质"],
        "avoid_ingredients": ["矿物油", "凡士林", "棕榈酸异丙酯", "肉豆蔻酸异丙酯"],
        "preferred_ingredients": ["烟酰胺", "水杨酸", "果酸", "茶树精油", "玻尿酸"],
        "sensitivity_level": 1
    },
    "混合性": {
        "key_needs": ["分区护理", "平衡水油", "基础抗氧化"],
        "avoid_ingredients": [],
        "preferred_ingredients": ["烟酰胺", "玻尿酸", "神经酰胺", "维生素C", "积雪草"],
        "sensitivity_level": 1
    },
    "敏感性": {
        "key_needs": ["修复屏障", "舒缓抗炎", "温和清洁"],
        "avoid_ingredients": ["酒精", "香精", "色素", "皂基", "SLS/SLES", "果酸", "水杨酸", "视黄醇", "甲基异噻唑啉酮", "甲基氯异噻唑啉酮", "羊毛脂", "二苯酮"],
        "preferred_ingredients": ["神经酰胺", "积雪草", "泛醇", "玻尿酸", "红没药醇", "角鲨烷"],
        "sensitivity_level": 5
    },
    "痘痘": {
        "key_needs": ["抗菌消炎", "疏通毛孔", "控油", "修复痘印"],
        "avoid_ingredients": ["矿物油", "凡士林", "棕榈酸异丙酯", "肉豆蔻酸异丙酯", "香精"],
        "preferred_ingredients": ["水杨酸", "烟酰胺", "茶树精油", "积雪草", "传明酸"],
        "sensitivity_level": 3
    },
    "中性": {
        "key_needs": ["基础保湿", "抗氧化", "维持稳定"],
        "avoid_ingredients": [],
        "preferred_ingredients": ["玻尿酸", "维生素C", "维生素E", "烟酰胺", "神经酰胺"],
        "sensitivity_level": 1
    },
    "成熟肌": {
        "key_needs": ["抗老紧致", "促进胶原", "深层保湿"],
        "avoid_ingredients": ["酒精", "皂基"],
        "preferred_ingredients": ["视黄醇", "胜肽", "维生素C", "玻尿酸", "胶原蛋白", "虾青素"],
        "sensitivity_level": 2
    },
    "暗沉": {
        "key_needs": ["美白提亮", "抗氧化", "促进代谢"],
        "avoid_ingredients": [],
        "preferred_ingredients": ["维生素C", "烟酰胺", "熊果苷", "传明酸", "果酸", "曲酸"],
        "sensitivity_level": 2
    }
}


SEASONAL_ADVICE: Dict[str, Dict] = {
    "春季": {
        "keywords": ["花粉", "敏感", "换季", "紫外线增强"],
        "general_tips": "春季花粉多、紫外线增强，注意抗敏舒缓和防晒",
        "skin_specific": {
            "干性": "加强保湿，防止春风带走水分",
            "油性": "T区开始出油增多，注意清洁控油",
            "混合性": "分区护理，T区控油两颊保湿",
            "敏感性": "重点抗敏，避开花粉，精简护肤",
            "痘痘": "换季可能爆痘，加强清洁和消炎",
            "中性": "维持基础护理，加防晒",
            "成熟肌": "抗老同时注意春季敏感",
            "暗沉": "紫外线增强，加强美白防晒"
        },
        "recommended_ingredients": ["积雪草", "红没药醇", "泛醇", "维生素C", "玻尿酸"],
        "avoid_ingredients": ["香精", "酒精"]
    },
    "夏季": {
        "keywords": ["高温", "出汗", "紫外线强", "出油多"],
        "general_tips": "夏季高温多汗，注意控油清洁和强效防晒",
        "skin_specific": {
            "干性": "选择清爽型保湿，避免油腻",
            "油性": "加强控油清洁，可使用酸类产品",
            "混合性": "T区加强控油，全脸使用清爽产品",
            "敏感性": "物理防晒为主，避免高温刺激",
            "痘痘": "重点控油抗菌，防止出汗堵塞毛孔",
            "中性": "清爽保湿+防晒",
            "成熟肌": "抗氧化防晒，避免厚重产品",
            "暗沉": "美白+防晒双管齐下"
        },
        "recommended_ingredients": ["烟酰胺", "水杨酸", "玻尿酸", "维生素C", "茶树精油"],
        "avoid_ingredients": ["矿物油", "凡士林", "厚重封闭成分"]
    },
    "秋季": {
        "keywords": ["干燥", "换季", "温度下降", "屏障修复"],
        "general_tips": "秋季干燥，加强保湿修复，重建皮肤屏障",
        "skin_specific": {
            "干性": "强效保湿，可使用封闭性油脂",
            "油性": "出油减少，逐渐过渡到滋润型产品",
            "混合性": "整体加强保湿，T区减少控油力度",
            "敏感性": "换季敏感，修复屏障为主",
            "痘痘": "秋季痘痘可能减轻，转向修复痘印",
            "中性": "加强保湿，预防干燥",
            "成熟肌": "保湿+抗老，秋冬是抗老黄金期",
            "暗沉": "秋季适合美白，紫外线相对较弱"
        },
        "recommended_ingredients": ["玻尿酸", "神经酰胺", "角鲨烷", "泛醇", "烟酰胺"],
        "avoid_ingredients": ["高浓度酒精", "过度去角质"]
    },
    "冬季": {
        "keywords": ["低温", "干燥", "寒风", "强力保湿"],
        "general_tips": "冬季严寒干燥，重点是强力保湿和屏障防护",
        "skin_specific": {
            "干性": "多层保湿，使用封闭性强的油脂和面霜",
            "油性": "冬季出油减少，避免过度清洁",
            "混合性": "全脸保湿，可分区使用不同产品",
            "敏感性": "温和清洁，强效修复屏障",
            "痘痘": "冬季痘痘可能缓解，以修复为主",
            "中性": "加强保湿，防止干燥",
            "成熟肌": "抗老+保湿，营养型护肤",
            "暗沉": "冬季紫外线弱，集中美白护理"
        },
        "recommended_ingredients": ["神经酰胺", "角鲨烷", "玻尿酸", "维生素E", "胶原蛋白", "泛醇"],
        "avoid_ingredients": ["高浓度酒精", "皂基", "强力清洁成分", "过度去角质"]
    }
}


def get_ingredient_category(name: str) -> Optional[str]:
    name_lower = name.strip().lower()
    
    for key, data in ACTIVE_INGREDIENTS.items():
        if name_lower == key.lower() or any(name_lower == a.lower() for a in data["aliases"]):
            return "active"
    
    for key, data in PRESERVATIVES.items():
        if name_lower == key.lower() or any(name_lower == a.lower() for a in data["aliases"]):
            return "preservative"
    
    for key, data in RISK_INGREDIENTS.items():
        if name_lower == key.lower() or any(name_lower == a.lower() for a in data["aliases"]):
            return "risk"
    
    return None


def get_ingredient_info(name: str) -> Optional[Dict]:
    name_lower = name.strip().lower()
    
    for key, data in ACTIVE_INGREDIENTS.items():
        if name_lower == key.lower() or any(name_lower == a.lower() for a in data["aliases"]):
            return {**data, "name": key, "category": "active"}
    
    for key, data in PRESERVATIVES.items():
        if name_lower == key.lower() or any(name_lower == a.lower() for a in data["aliases"]):
            return {**data, "name": key, "category": "preservative"}
    
    for key, data in RISK_INGREDIENTS.items():
        if name_lower == key.lower() or any(name_lower == a.lower() for a in data["aliases"]):
            return {**data, "name": key, "category": "risk"}
    
    return None
