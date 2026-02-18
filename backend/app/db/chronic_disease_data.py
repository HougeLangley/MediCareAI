"""
ICD-10 Chronic and Special Disease Data | ICD-10特殊病与慢性病数据

中国医保规定的特殊病和慢性病列表（部分常见疾病）
用于系统初始化

数据来源：国家医保局、各省市医保目录
"""

from typing import List, Dict

# =============================================================================
# 慢性病列表 (Chronic Diseases) - 需要长期治疗和管理的疾病
# =============================================================================

CHRONIC_DISEASES: List[Dict] = [
    # 心血管疾病
    {
        "icd10_code": "I10",
        "icd10_name": "Essential (primary) hypertension",
        "disease_type": "chronic",
        "common_names": ["高血压", "原发性高血压"],
        "category": "心血管疾病",
        "description": "以体循环动脉血压增高为主要特征的临床综合征",
        "medical_notes": "注意降压药物选择，避免使用影响血压的药物"
    },
    {
        "icd10_code": "I25.1",
        "icd10_name": "Atherosclerotic heart disease",
        "disease_type": "chronic",
        "common_names": ["冠状动脉粥样硬化性心脏病", "冠心病"],
        "category": "心血管疾病",
        "description": "冠状动脉发生粥样硬化引起管腔狭窄或闭塞，导致心肌缺血缺氧",
        "medical_notes": "注意抗血小板药物、他汀类药物的使用，警惕心绞痛发作"
    },
    {
        "icd10_code": "I50",
        "icd10_name": "Heart failure",
        "disease_type": "chronic",
        "common_names": ["心力衰竭", "心衰"],
        "category": "心血管疾病",
        "description": "各种心脏病导致心功能下降的一组综合征",
        "medical_notes": "注意液体管理，慎用NSAIDs类药物，监测电解质"
    },
    {
        "icd10_code": "I48",
        "icd10_name": "Atrial fibrillation and flutter",
        "disease_type": "chronic",
        "common_names": ["心房颤动", "房颤"],
        "category": "心血管疾病",
        "description": "心房失去正常节律，代之以快速无序的颤动波",
        "medical_notes": "注意抗凝治疗，控制心室率，警惕脑栓塞风险"
    },
    
    # 内分泌疾病
    {
        "icd10_code": "E11",
        "icd10_name": "Type 2 diabetes mellitus",
        "disease_type": "chronic",
        "common_names": ["2型糖尿病", "成人糖尿病", "非胰岛素依赖型糖尿病"],
        "category": "内分泌疾病",
        "description": "以胰岛素抵抗为主，伴胰岛素分泌不足的代谢性疾病",
        "medical_notes": "注意血糖监测，谨慎使用糖皮质激素，预防低血糖"
    },
    {
        "icd10_code": "E10",
        "icd10_name": "Type 1 diabetes mellitus",
        "disease_type": "chronic",
        "common_names": ["1型糖尿病", "胰岛素依赖型糖尿病", "青少年糖尿病"],
        "category": "内分泌疾病",
        "description": "胰岛β细胞破坏导致胰岛素绝对缺乏的代谢性疾病",
        "medical_notes": "必须胰岛素治疗，密切监测血糖，预防酮症酸中毒"
    },
    {
        "icd10_code": "E03.9",
        "icd10_name": "Hypothyroidism, unspecified",
        "disease_type": "chronic",
        "common_names": ["甲状腺功能减退症", "甲减"],
        "category": "内分泌疾病",
        "description": "甲状腺激素合成及分泌减少，或其生理效应不足所致机体代谢降低",
        "medical_notes": "注意甲状腺激素替代治疗，监测TSH水平"
    },
    {
        "icd10_code": "E05",
        "icd10_name": "Thyrotoxicosis [hyperthyroidism]",
        "disease_type": "chronic",
        "common_names": ["甲状腺功能亢进症", "甲亢"],
        "category": "内分泌疾病",
        "description": "甲状腺激素产生过多引起的临床综合征",
        "medical_notes": "注意心率、体重变化，避免使用含碘药物"
    },
    {
        "icd10_code": "E66",
        "icd10_name": "Obesity",
        "disease_type": "chronic",
        "common_names": ["肥胖症"],
        "category": "内分泌疾病",
        "description": "体内脂肪堆积过多和（或）分布异常，体重增加",
        "medical_notes": "注意体重管理，慎用增加体重的药物"
    },
    
    # 呼吸系统疾病
    {
        "icd10_code": "J44",
        "icd10_name": "Chronic obstructive pulmonary disease",
        "disease_type": "chronic",
        "common_names": ["慢性阻塞性肺疾病", "慢阻肺", "COPD"],
        "category": "呼吸系统疾病",
        "description": "以持续气流受限为特征的可以预防和治疗的疾病",
        "medical_notes": "注意支气管扩张剂使用，避免使用抑制呼吸的药物"
    },
    {
        "icd10_code": "J45",
        "icd10_name": "Asthma",
        "disease_type": "chronic",
        "common_names": ["支气管哮喘", "哮喘"],
        "category": "呼吸系统疾病",
        "description": "以慢性气道炎症和气道高反应性为特征的异质性疾病",
        "medical_notes": "注意吸入激素和支气管扩张剂，警惕哮喘急性发作"
    },
    
    # 神经系统疾病
    {
        "icd10_code": "G20",
        "icd10_name": "Parkinson's disease",
        "disease_type": "chronic",
        "common_names": ["帕金森病", "震颤麻痹"],
        "category": "神经系统疾病",
        "description": "中老年人常见的神经系统变性疾病",
        "medical_notes": "注意多巴胺能药物使用，避免使用多巴胺受体拮抗剂"
    },
    {
        "icd10_code": "G35",
        "icd10_name": "Multiple sclerosis",
        "disease_type": "chronic",
        "common_names": ["多发性硬化症", "MS"],
        "category": "神经系统疾病",
        "description": "中枢神经系统免疫介导的炎性脱髓鞘疾病",
        "medical_notes": "注意免疫调节治疗，避免使用免疫抑制剂"
    },
    {
        "icd10_code": "G40",
        "icd10_name": "Epilepsy",
        "disease_type": "chronic",
        "common_names": ["癫痫", "羊癫疯"],
        "category": "神经系统疾病",
        "description": "大脑神经元突发性异常放电，导致短暂的大脑功能障碍",
        "medical_notes": "注意抗癫痫药物使用，避免使用降低癫痫阈值的药物"
    },
    {
        "icd10_code": "I63",
        "icd10_name": "Cerebral infarction",
        "disease_type": "chronic",
        "common_names": ["脑梗死", "脑梗塞", "缺血性脑卒中"],
        "category": "神经系统疾病",
        "description": "脑部血液循环障碍，缺血、缺氧所致的局限性脑组织缺血性坏死",
        "medical_notes": "注意抗血小板和他汀治疗，血压管理，预防再次卒中"
    },
    
    # 消化系统疾病
    {
        "icd10_code": "K50",
        "icd10_name": "Crohn's disease [regional enteritis]",
        "disease_type": "chronic",
        "common_names": ["克罗恩病", "节段性肠炎"],
        "category": "消化系统疾病",
        "description": "一种慢性肉芽肿性炎症性肠病，可累及消化道任何部位",
        "medical_notes": "注意免疫抑制剂使用，营养支持，监测肠梗阻"
    },
    {
        "icd10_code": "K51",
        "icd10_name": "Ulcerative colitis",
        "disease_type": "chronic",
        "common_names": ["溃疡性结肠炎", "溃结"],
        "category": "消化系统疾病",
        "description": "一种慢性非特异性炎症性肠病，主要累及结肠黏膜和黏膜下层",
        "medical_notes": "注意5-氨基水杨酸制剂使用，监测出血和癌变"
    },
    {
        "icd10_code": "K74",
        "icd10_name": "Fibrosis and cirrhosis of liver",
        "disease_type": "chronic",
        "common_names": ["肝纤维化与肝硬化", "肝硬化"],
        "category": "消化系统疾病",
        "description": "各种慢性肝病发展的晚期阶段，以肝组织弥漫性纤维化、假小叶和再生结节形成为特征",
        "medical_notes": "注意肝功能，避免使用肝毒性药物，监测并发症"
    },
    
    # 肾脏疾病
    {
        "icd10_code": "N18",
        "icd10_name": "Chronic kidney disease",
        "disease_type": "chronic",
        "common_names": ["慢性肾脏病", "CKD", "慢性肾功能不全"],
        "category": "肾脏疾病",
        "description": "肾脏结构或功能异常持续超过3个月，对健康产生影响",
        "medical_notes": "注意药物剂量调整，避免肾毒性药物，监测电解质"
    },
    
    # 精神疾病
    {
        "icd10_code": "F32",
        "icd10_name": "Depressive episode",
        "disease_type": "chronic",
        "common_names": ["抑郁发作", "抑郁症"],
        "category": "精神疾病",
        "description": "以显著而持久的心境低落为主要临床特征的心境障碍",
        "medical_notes": "注意抗抑郁药物使用，监测自杀风险"
    },
    {
        "icd10_code": "F31",
        "icd10_name": "Bipolar affective disorder",
        "disease_type": "chronic",
        "common_names": ["双相情感障碍", "躁郁症"],
        "category": "精神疾病",
        "description": "既有躁狂发作又有抑郁发作的一类精神障碍",
        "medical_notes": "注意心境稳定剂使用，监测情绪变化"
    },
    
    # 风湿免疫疾病
    {
        "icd10_code": "M05",
        "icd10_name": "Rheumatoid arthritis with rheumatoid factor",
        "disease_type": "chronic",
        "common_names": ["类风湿关节炎", "类风湿", "RA"],
        "category": "风湿免疫疾病",
        "description": "以侵蚀性、对称性多关节炎为主要临床表现的慢性、全身性自身免疫性疾病",
        "medical_notes": "注意免疫抑制剂使用，监测关节破坏和药物副作用"
    },
    {
        "icd10_code": "M45",
        "icd10_name": "Ankylosing spondylitis",
        "disease_type": "chronic",
        "common_names": ["强直性脊柱炎", "AS"],
        "category": "风湿免疫疾病",
        "description": "以中轴关节慢性炎症为主的全身性疾病",
        "medical_notes": "注意NSAIDs使用，功能锻炼，监测脊柱活动度"
    },
    {
        "icd10_code": "M32",
        "icd10_name": "Systemic lupus erythematosus",
        "disease_type": "chronic",
        "common_names": ["系统性红斑狼疮", "SLE", "狼疮"],
        "category": "风湿免疫疾病",
        "description": "多系统损害的慢性自身免疫性疾病",
        "medical_notes": "注意糖皮质激素和免疫抑制剂使用，监测多器官功能"
    },
    
    # 肿瘤（部分常见恶性肿瘤）
    {
        "icd10_code": "C78",
        "icd10_name": "Secondary malignant neoplasm of respiratory and digestive organs",
        "disease_type": "chronic",
        "common_names": ["恶性肿瘤（维持治疗期）", "癌症", "肿瘤"],
        "category": "肿瘤",
        "description": "恶性肿瘤维持治疗期或康复期",
        "medical_notes": "注意化疗药物相互作用，骨髓抑制，免疫功能"
    },
]

# =============================================================================
# 特殊病列表 (Special Diseases) - 需要特殊门诊管理的重大疾病
# =============================================================================

SPECIAL_DISEASES: List[Dict] = [
    # 恶性肿瘤
    {
        "icd10_code": "C00-C97",
        "icd10_name": "Malignant neoplasms",
        "disease_type": "special",
        "common_names": ["恶性肿瘤门诊治疗", "癌症门诊化疗", "肿瘤特殊门诊"],
        "category": "恶性肿瘤",
        "description": "各类恶性肿瘤的门诊化疗、放疗、靶向治疗等",
        "medical_notes": "注意化疗方案，药物相互作用，骨髓抑制监测"
    },
    {
        "icd10_code": "C90",
        "icd10_name": "Multiple myeloma and malignant plasma cell neoplasms",
        "disease_type": "special",
        "common_names": ["多发性骨髓瘤", "MM"],
        "category": "恶性肿瘤",
        "description": "恶性浆细胞病，骨髓中单克隆浆细胞异常增生",
        "medical_notes": "注意骨质破坏，肾功能，高钙血症"
    },
    
    # 器官移植术后
    {
        "icd10_code": "Z94",
        "icd10_name": "Transplanted organ and tissue status",
        "disease_type": "special",
        "common_names": ["器官移植术后", "肾移植术后", "肝移植术后"],
        "category": "器官移植",
        "description": "肾移植、肝移植、心脏移植等术后的抗排异治疗",
        "medical_notes": "必须免疫抑制剂治疗，监测排异反应和感染"
    },
    
    # 终末期肾病
    {
        "icd10_code": "N18.5",
        "icd10_name": "Chronic kidney disease, stage 5",
        "disease_type": "special",
        "common_names": ["终末期肾病", "尿毒症", "CKD5期"],
        "category": "肾脏疾病",
        "description": "慢性肾脏病终末期，需要透析或肾移植",
        "medical_notes": "注意透析管理，水电解质平衡，贫血纠正"
    },
    
    # 血友病
    {
        "icd10_code": "D66",
        "icd10_name": "Hereditary factor VIII deficiency",
        "disease_type": "special",
        "common_names": ["血友病A", "血友病", "第八因子缺乏症"],
        "category": "血液病",
        "description": "X连锁隐性遗传性出血性疾病，凝血因子VIII缺乏",
        "medical_notes": "注意凝血因子替代治疗，避免肌肉注射，预防出血"
    },
    {
        "icd10_code": "D67",
        "icd10_name": "Hereditary factor IX deficiency",
        "disease_type": "special",
        "common_names": ["血友病B", "Christmas病", "第九因子缺乏症"],
        "category": "血液病",
        "description": "X连锁隐性遗传性出血性疾病，凝血因子IX缺乏",
        "medical_notes": "注意凝血因子替代治疗，避免肌肉注射，预防出血"
    },
    
    # 地中海贫血
    {
        "icd10_code": "D56",
        "icd10_name": "Thalassaemia",
        "disease_type": "special",
        "common_names": ["地中海贫血", "海洋性贫血", "珠蛋白生成障碍性贫血"],
        "category": "血液病",
        "description": "遗传性溶血性贫血，珠蛋白肽链合成障碍",
        "medical_notes": "注意输血和祛铁治疗，骨髓移植评估"
    },
    
    # 再生障碍性贫血
    {
        "icd10_code": "D61",
        "icd10_name": "Aplastic anaemia",
        "disease_type": "special",
        "common_names": ["再生障碍性贫血", "再障"],
        "category": "血液病",
        "description": "骨髓造血功能衰竭症，全血细胞减少",
        "medical_notes": "注意免疫抑制剂或造血干细胞移植，预防感染和出血"
    },
    
    # 系统性红斑狼疮（重症）
    {
        "icd10_code": "M32.1",
        "icd10_name": "Systemic lupus erythematosus with organ or system involvement",
        "disease_type": "special",
        "common_names": ["系统性红斑狼疮（重症）", "重症SLE"],
        "category": "风湿免疫",
        "description": "伴有重要脏器损害的系统性红斑狼疮",
        "medical_notes": "注意大剂量激素和免疫抑制剂，监测狼疮活动度"
    },
    
    # 肝硬化失代偿期
    {
        "icd10_code": "K74.6",
        "icd10_name": "Other and unspecified cirrhosis of liver",
        "disease_type": "special",
        "common_names": ["肝硬化失代偿期", "失代偿性肝硬化"],
        "category": "消化系统",
        "description": "肝硬化伴腹水、食管胃底静脉曲张破裂出血、肝性脑病等并发症",
        "medical_notes": "注意并发症管理，肝移植评估"
    },
    
    # 重性精神病
    {
        "icd10_code": "F20",
        "icd10_name": "Schizophrenia",
        "disease_type": "special",
        "common_names": ["精神分裂症", "重性精神病"],
        "category": "精神卫生",
        "description": "严重的精神障碍，以思维、情感、行为的分裂为主要特征",
        "medical_notes": "注意抗精神病药物长期使用，社会功能康复"
    },
    
    # 耐多药肺结核
    {
        "icd10_code": "A15.0",
        "icd10_name": "Tuberculosis of lung, confirmed by sputum microscopy with or without culture",
        "disease_type": "special",
        "common_names": ["肺结核", "耐多药肺结核"],
        "category": "传染病",
        "description": "结核分枝杆菌引起的肺部慢性传染病，耐多药株感染",
        "medical_notes": "注意长期抗结核治疗，药物不良反应，隔离措施"
    },
    
    # 帕金森病（重症）
    {
        "icd10_code": "G20.1",
        "icd10_name": "Parkinson's disease with severe disability",
        "disease_type": "special",
        "common_names": ["帕金森病（重症）", "重症帕金森"],
        "category": "神经系统",
        "description": "帕金森病伴严重运动障碍，日常生活能力严重受损",
        "medical_notes": "注意多巴丝肼等药物调整，预防跌倒"
    },
    
    # 运动神经元病
    {
        "icd10_code": "G12.2",
        "icd10_name": "Motor neuron disease",
        "disease_type": "special",
        "common_names": ["运动神经元病", "渐冻症", "ALS", "肌萎缩侧索硬化"],
        "category": "神经系统",
        "description": "选择性侵犯脊髓前角细胞、脑干运动神经元等的神经系统变性疾病",
        "medical_notes": "注意呼吸支持和营养支持，利鲁唑治疗"
    },
    
    # 尘肺病
    {
        "icd10_code": "J60-J65",
        "icd10_name": "Pneumoconiosis",
        "disease_type": "special",
        "common_names": ["尘肺病", "矽肺", "煤工尘肺"],
        "category": "职业病",
        "description": "在职业活动中长期吸入生产性粉尘并在肺内潴留而引起的以肺组织弥漫性纤维化为主的疾病",
        "medical_notes": "注意肺功能保护，预防感染，肺移植评估"
    },
]

# =============================================================================
# 既是慢性病又是特殊病的疾病 (Both Chronic and Special)
# =============================================================================

BOTH_DISEASES: List[Dict] = [
    {
        "icd10_code": "E11.6",
        "icd10_name": "Type 2 diabetes mellitus with other specified complications",
        "disease_type": "both",
        "common_names": ["2型糖尿病（伴并发症）", "糖尿病并发症"],
        "category": "内分泌/特殊病",
        "description": "2型糖尿病伴有糖尿病肾病、糖尿病足等严重并发症",
        "medical_notes": "注意血糖控制和并发症管理，综合治疗"
    },
    {
        "icd10_code": "I25.5",
        "icd10_name": "Ischaemic cardiomyopathy",
        "disease_type": "both",
        "common_names": ["缺血性心肌病", "冠心病心力衰竭"],
        "category": "心血管/特殊病",
        "description": "心肌长期缺血导致心肌纤维化，心脏扩大和心力衰竭",
        "medical_notes": "注意心衰管理，血运重建评估"
    },
    {
        "icd10_code": "I20-I25",
        "icd10_name": "Ischaemic heart diseases",
        "disease_type": "both",
        "common_names": ["冠心病（支架术后）", "PCI术后", "CABG术后"],
        "category": "心血管/特殊病",
        "description": "冠状动脉介入治疗或搭桥术后需要长期抗血小板治疗",
        "medical_notes": "注意双联抗血小板治疗，再狭窄监测"
    },
]

# 合并所有疾病
ALL_CHRONIC_DISEASES = CHRONIC_DISEASES + SPECIAL_DISEASES + BOTH_DISEASES
