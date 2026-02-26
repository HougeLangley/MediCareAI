/**
 * China Administrative Divisions Data | 中国行政区划数据
 * 
 * 包含省市区三级行政区划数据
 * 数据来源：国家统计局最新行政区划代码
 */

export interface District {
  code: string;
  name: string;
}

export interface City {
  code: string;
  name: string;
  districts: District[];
}

export interface Province {
  code: string;
  name: string;
  cities: City[];
}

// 中国省级行政区划数据
export const provinces: Province[] = [
  {
    code: "110000",
    name: "北京市",
    cities: [
      {
        code: "110100",
        name: "北京市",
        districts: [
          { code: "110101", name: "东城区" },
          { code: "110102", name: "西城区" },
          { code: "110105", name: "朝阳区" },
          { code: "110106", name: "丰台区" },
          { code: "110107", name: "石景山区" },
          { code: "110108", name: "海淀区" },
          { code: "110109", name: "门头沟区" },
          { code: "110111", name: "房山区" },
          { code: "110112", name: "通州区" },
          { code: "110113", name: "顺义区" },
          { code: "110114", name: "昌平区" },
          { code: "110115", name: "大兴区" },
          { code: "110116", name: "怀柔区" },
          { code: "110117", name: "平谷区" },
          { code: "110118", name: "密云区" },
          { code: "110119", name: "延庆区" },
        ],
      },
    ],
  },
  {
    code: "120000",
    name: "天津市",
    cities: [
      {
        code: "120100",
        name: "天津市",
        districts: [
          { code: "120101", name: "和平区" },
          { code: "120102", name: "河东区" },
          { code: "120103", name: "河西区" },
          { code: "120104", name: "南开区" },
          { code: "120105", name: "河北区" },
          { code: "120106", name: "红桥区" },
          { code: "120110", name: "东丽区" },
          { code: "120111", name: "西青区" },
          { code: "120112", name: "津南区" },
          { code: "120113", name: "北辰区" },
          { code: "120114", name: "武清区" },
          { code: "120115", name: "宝坻区" },
          { code: "120116", name: "滨海新区" },
          { code: "120117", name: "宁河区" },
          { code: "120118", name: "静海区" },
          { code: "120119", name: "蓟州区" },
        ],
      },
    ],
  },
  {
    code: "130000",
    name: "河北省",
    cities: [
      {
        code: "130100",
        name: "石家庄市",
        districts: [
          { code: "130102", name: "长安区" },
          { code: "130104", name: "桥西区" },
          { code: "130105", name: "新华区" },
          { code: "130107", name: "井陉矿区" },
          { code: "130108", name: "裕华区" },
          { code: "130109", name: "藁城区" },
          { code: "130110", name: "鹿泉区" },
          { code: "130111", name: "栾城区" },
          { code: "130121", name: "井陉县" },
          { code: "130123", name: "正定县" },
          { code: "130125", name: "行唐县" },
          { code: "130126", name: "灵寿县" },
          { code: "130127", name: "高邑县" },
          { code: "130128", name: "深泽县" },
          { code: "130129", name: "赞皇县" },
          { code: "130130", name: "无极县" },
          { code: "130131", name: "平山县" },
          { code: "130132", name: "元氏县" },
          { code: "130133", name: "赵县" },
          { code: "130181", name: "辛集市" },
          { code: "130183", name: "晋州市" },
          { code: "130184", name: "新乐市" },
        ],
      },
      {
        code: "130200",
        name: "唐山市",
        districts: [
          { code: "130202", name: "路南区" },
          { code: "130203", name: "路北区" },
          { code: "130204", name: "古冶区" },
          { code: "130205", name: "开平区" },
          { code: "130207", name: "丰南区" },
          { code: "130208", name: "丰润区" },
          { code: "130209", name: "曹妃甸区" },
          { code: "130224", name: "滦南县" },
          { code: "130225", name: "乐亭县" },
          { code: "130227", name: "迁西县" },
          { code: "130229", name: "玉田县" },
          { code: "130281", name: "遵化市" },
          { code: "130283", name: "迁安市" },
          { code: "130284", name: "滦州市" },
        ],
      },
      {
        code: "130300",
        name: "秦皇岛市",
        districts: [
          { code: "130302", name: "海港区" },
          { code: "130303", name: "山海关区" },
          { code: "130304", name: "北戴河区" },
          { code: "130306", name: "抚宁区" },
          { code: "130321", name: "青龙满族自治县" },
          { code: "130322", name: "昌黎县" },
          { code: "130324", name: "卢龙县" },
        ],
      },
      {
        code: "130400",
        name: "邯郸市",
        districts: [
          { code: "130402", name: "邯山区" },
          { code: "130403", name: "丛台区" },
          { code: "130404", name: "复兴区" },
          { code: "130406", name: "峰峰矿区" },
          { code: "130407", name: "肥乡区" },
          { code: "130408", name: "永年区" },
          { code: "130423", name: "临漳县" },
          { code: "130424", name: "成安县" },
          { code: "130425", name: "大名县" },
          { code: "130426", name: "涉县" },
          { code: "130427", name: "磁县" },
          { code: "130430", name: "邱县" },
          { code: "130431", name: "鸡泽县" },
          { code: "130432", name: "广平县" },
          { code: "130433", name: "馆陶县" },
          { code: "130434", name: "魏县" },
          { code: "130435", name: "曲周县" },
          { code: "130481", name: "武安市" },
        ],
      },
      {
        code: "130500",
        name: "邢台市",
        districts: [
          { code: "130502", name: "襄都区" },
          { code: "130503", name: "信都区" },
          { code: "130505", name: "任泽区" },
          { code: "130506", name: "南和区" },
          { code: "130522", name: "临城县" },
          { code: "130523", name: "内丘县" },
          { code: "130524", name: "柏乡县" },
          { code: "130525", name: "隆尧县" },
          { code: "130528", name: "宁晋县" },
          { code: "130529", name: "巨鹿县" },
          { code: "130530", name: "新河县" },
          { code: "130531", name: "广宗县" },
          { code: "130532", name: "平乡县" },
          { code: "130533", name: "威县" },
          { code: "130534", name: "清河县" },
          { code: "130535", name: "临西县" },
          { code: "130581", name: "南宫市" },
          { code: "130582", name: "沙河市" },
        ],
      },
      {
        code: "130600",
        name: "保定市",
        districts: [
          { code: "130602", name: "竞秀区" },
          { code: "130606", name: "莲池区" },
          { code: "130607", name: "满城区" },
          { code: "130608", name: "清苑区" },
          { code: "130609", name: "徐水区" },
          { code: "130623", name: "涞水县" },
          { code: "130624", name: "阜平县" },
          { code: "130626", name: "定兴县" },
          { code: "130627", name: "唐县" },
          { code: "130628", name: "高阳县" },
          { code: "130629", name: "容城县" },
          { code: "130630", name: "涞源县" },
          { code: "130631", name: "望都县" },
          { code: "130632", name: "安新县" },
          { code: "130633", name: "易县" },
          { code: "130634", name: "曲阳县" },
          { code: "130635", name: "蠡县" },
          { code: "130636", name: "顺平县" },
          { code: "130637", name: "博野县" },
          { code: "130638", name: "雄县" },
          { code: "130681", name: "涿州市" },
          { code: "130682", name: "定州市" },
          { code: "130683", name: "安国市" },
          { code: "130684", name: "高碑店市" },
        ],
      },
      {
        code: "130700",
        name: "张家口市",
        districts: [
          { code: "130702", name: "桥东区" },
          { code: "130703", name: "桥西区" },
          { code: "130705", name: "宣化区" },
          { code: "130706", name: "下花园区" },
          { code: "130708", name: "万全区" },
          { code: "130709", name: "崇礼区" },
          { code: "130722", name: "张北县" },
          { code: "130723", name: "康保县" },
          { code: "130724", name: "沽源县" },
          { code: "130725", name: "尚义县" },
          { code: "130726", name: "蔚县" },
          { code: "130727", name: "阳原县" },
          { code: "130728", name: "怀安县" },
          { code: "130730", name: "怀来县" },
          { code: "130731", name: "涿鹿县" },
          { code: "130732", name: "赤城县" },
        ],
      },
      {
        code: "130800",
        name: "承德市",
        districts: [
          { code: "130802", name: "双桥区" },
          { code: "130803", name: "双滦区" },
          { code: "130804", name: "鹰手营子矿区" },
          { code: "130821", name: "承德县" },
          { code: "130822", name: "兴隆县" },
          { code: "130824", name: "滦平县" },
          { code: "130825", name: "隆化县" },
          { code: "130826", name: "丰宁满族自治县" },
          { code: "130827", name: "宽城满族自治县" },
          { code: "130828", name: "围场满族蒙古族自治县" },
          { code: "130881", name: "平泉市" },
        ],
      },
      {
        code: "130900",
        name: "沧州市",
        districts: [
          { code: "130902", name: "新华区" },
          { code: "130903", name: "运河区" },
          { code: "130921", name: "沧县" },
          { code: "130922", name: "青县" },
          { code: "130923", name: "东光县" },
          { code: "130924", name: "海兴县" },
          { code: "130925", name: "盐山县" },
          { code: "130926", name: "肃宁县" },
          { code: "130927", name: "南皮县" },
          { code: "130928", name: "吴桥县" },
          { code: "130929", name: "献县" },
          { code: "130930", name: "孟村回族自治县" },
          { code: "130981", name: "泊头市" },
          { code: "130982", name: "任丘市" },
          { code: "130983", name: "黄骅市" },
          { code: "130984", name: "河间市" },
        ],
      },
      {
        code: "131000",
        name: "廊坊市",
        districts: [
          { code: "131002", name: "安次区" },
          { code: "131003", name: "广阳区" },
          { code: "131022", name: "固安县" },
          { code: "131023", name: "永清县" },
          { code: "131024", name: "香河县" },
          { code: "131025", name: "大城县" },
          { code: "131026", name: "文安县" },
          { code: "131028", name: "大厂回族自治县" },
          { code: "131081", name: "霸州市" },
          { code: "131082", name: "三河市" },
        ],
      },
      {
        code: "131100",
        name: "衡水市",
        districts: [
          { code: "131102", name: "桃城区" },
          { code: "131103", name: "冀州区" },
          { code: "131121", name: "枣强县" },
          { code: "131122", name: "武邑县" },
          { code: "131123", name: "武强县" },
          { code: "131124", name: "饶阳县" },
          { code: "131125", name: "安平县" },
          { code: "131126", name: "故城县" },
          { code: "131127", name: "景县" },
          { code: "131128", name: "阜城县" },
          { code: "131182", name: "深州市" },
        ],
      },
    ],
  },
  {
    code: "140000",
    name: "山西省",
    cities: [
      {
        code: "140100",
        name: "太原市",
        districts: [
          { code: "140105", name: "小店区" },
          { code: "140106", name: "迎泽区" },
          { code: "140107", name: "杏花岭区" },
          { code: "140108", name: "尖草坪区" },
          { code: "140109", name: "万柏林区" },
          { code: "140110", name: "晋源区" },
          { code: "140121", name: "清徐县" },
          { code: "140122", name: "阳曲县" },
          { code: "140123", name: "娄烦县" },
          { code: "140181", name: "古交市" },
        ],
      },
      {
        code: "140200",
        name: "大同市",
        districts: [
          { code: "140212", name: "新荣区" },
          { code: "140213", name: "平城区" },
          { code: "140214", name: "云冈区" },
          { code: "140215", name: "云州区" },
          { code: "140221", name: "阳高县" },
          { code: "140222", name: "天镇县" },
          { code: "140223", name: "广灵县" },
          { code: "140224", name: "灵丘县" },
          { code: "140225", name: "浑源县" },
          { code: "140226", name: "左云县" },
        ],
      },
      {
        code: "140300",
        name: "阳泉市",
        districts: [
          { code: "140302", name: "城区" },
          { code: "140303", name: "矿区" },
          { code: "140311", name: "郊区" },
          { code: "140321", name: "平定县" },
          { code: "140322", name: "盂县" },
        ],
      },
      {
        code: "140400",
        name: "长治市",
        districts: [
          { code: "140403", name: "潞州区" },
          { code: "140404", name: "上党区" },
          { code: "140405", name: "屯留区" },
          { code: "140406", name: "潞城区" },
          { code: "140423", name: "襄垣县" },
          { code: "140425", name: "平顺县" },
          { code: "140426", name: "黎城县" },
          { code: "140427", name: "壶关县" },
          { code: "140428", name: "长子县" },
          { code: "140429", name: "武乡县" },
          { code: "140430", name: "沁县" },
          { code: "140431", name: "沁源县" },
        ],
      },
      {
        code: "140500",
        name: "晋城市",
        districts: [
          { code: "140502", name: "城区" },
          { code: "140521", name: "沁水县" },
          { code: "140522", name: "阳城县" },
          { code: "140524", name: "陵川县" },
          { code: "140525", name: "泽州县" },
          { code: "140581", name: "高平市" },
        ],
      },
      {
        code: "140600",
        name: "朔州市",
        districts: [
          { code: "140602", name: "朔城区" },
          { code: "140603", name: "平鲁区" },
          { code: "140621", name: "山阴县" },
          { code: "140622", name: "应县" },
          { code: "140623", name: "右玉县" },
          { code: "140681", name: "怀仁市" },
        ],
      },
      {
        code: "140700",
        name: "晋中市",
        districts: [
          { code: "140702", name: "榆次区" },
          { code: "140703", name: "太谷区" },
          { code: "140721", name: "榆社县" },
          { code: "140722", name: "左权县" },
          { code: "140723", name: "和顺县" },
          { code: "140724", name: "昔阳县" },
          { code: "140725", name: "寿阳县" },
          { code: "140727", name: "祁县" },
          { code: "140728", name: "平遥县" },
          { code: "140729", name: "灵石县" },
          { code: "140781", name: "介休市" },
        ],
      },
      {
        code: "140800",
        name: "运城市",
        districts: [
          { code: "140802", name: "盐湖区" },
          { code: "140821", name: "临猗县" },
          { code: "140822", name: "万荣县" },
          { code: "140823", name: "闻喜县" },
          { code: "140824", name: "稷山县" },
          { code: "140825", name: "新绛县" },
          { code: "140826", name: "绛县" },
          { code: "140827", name: "垣曲县" },
          { code: "140828", name: "夏县" },
          { code: "140829", name: "平陆县" },
          { code: "140830", name: "芮城县" },
          { code: "140881", name: "永济市" },
          { code: "140882", name: "河津市" },
        ],
      },
      {
        code: "140900",
        name: "忻州市",
        districts: [
          { code: "140902", name: "忻府区" },
          { code: "140921", name: "定襄县" },
          { code: "140922", name: "五台县" },
          { code: "140923", name: "代县" },
          { code: "140924", name: "繁峙县" },
          { code: "140925", name: "宁武县" },
          { code: "140926", name: "静乐县" },
          { code: "140927", name: "神池县" },
          { code: "140928", name: "五寨县" },
          { code: "140929", name: "岢岚县" },
          { code: "140930", name: "河曲县" },
          { code: "140931", name: "保德县" },
          { code: "140932", name: "偏关县" },
          { code: "140981", name: "原平市" },
        ],
      },
      {
        code: "141000",
        name: "临汾市",
        districts: [
          { code: "141002", name: "尧都区" },
          { code: "141021", name: "曲沃县" },
          { code: "141022", name: "翼城县" },
          { code: "141023", name: "襄汾县" },
          { code: "141024", name: "洪洞县" },
          { code: "141025", name: "古县" },
          { code: "141026", name: "安泽县" },
          { code: "141027", name: "浮山县" },
          { code: "141028", name: "吉县" },
          { code: "141029", name: "乡宁县" },
          { code: "141030", name: "大宁县" },
          { code: "141031", name: "隰县" },
          { code: "141032", name: "永和县" },
          { code: "141033", name: "蒲县" },
          { code: "141034", name: "汾西县" },
          { code: "141081", name: "侯马市" },
          { code: "141082", name: "霍州市" },
        ],
      },
      {
        code: "141100",
        name: "吕梁市",
        districts: [
          { code: "141102", name: "离石区" },
          { code: "141121", name: "文水县" },
          { code: "141122", name: "交城县" },
          { code: "141123", name: "兴县" },
          { code: "141124", name: "临县" },
          { code: "141125", name: "柳林县" },
          { code: "141126", name: "石楼县" },
          { code: "141127", name: "岚县" },
          { code: "141128", name: "方山县" },
          { code: "141129", name: "中阳县" },
          { code: "141130", name: "交口县" },
          { code: "141181", name: "孝义市" },
          { code: "141182", name: "汾阳市" },
        ],
      },
    ],
  },
  // 更多省份数据...
];

// 常用省份列表（简化版）
export const commonProvinces = [
  "北京市",
  "天津市",
  "河北省",
  "山西省",
  "内蒙古自治区",
  "辽宁省",
  "吉林省",
  "黑龙江省",
  "上海市",
  "江苏省",
  "浙江省",
  "安徽省",
  "福建省",
  "江西省",
  "山东省",
  "河南省",
  "湖北省",
  "湖南省",
  "广东省",
  "广西壮族自治区",
  "海南省",
  "重庆市",
  "四川省",
  "贵州省",
  "云南省",
  "西藏自治区",
  "陕西省",
  "甘肃省",
  "青海省",
  "宁夏回族自治区",
  "新疆维吾尔自治区",
  "台湾省",
  "香港特别行政区",
  "澳门特别行政区",
];

// 根据省份名称获取城市列表
export const getCitiesByProvince = (provinceName: string): City[] => {
  const province = provinces.find((p) => p.name === provinceName);
  return province?.cities || [];
};

// 根据城市名称获取区县列表
export const getDistrictsByCity = (provinceName: string, cityName: string): District[] => {
  const province = provinces.find((p) => p.name === provinceName);
  const city = province?.cities.find((c) => c.name === cityName);
  return city?.districts || [];
};

// 格式化完整地址
export const formatFullAddress = (
  province: string,
  city: string,
  district: string,
  detail: string
): string => {
  return `${province}${city}${district}${detail}`;
};

// 解析地址字符串（简化版）
export const parseAddress = (fullAddress: string) => {
  // 尝试匹配省市区
  const provinceMatch = fullAddress.match(/^(.*?省|.*?自治区|.*?市|.*?特别行政区)/);
  const province = provinceMatch ? provinceMatch[1] : "";
  
  let remaining = province ? fullAddress.replace(province, "") : fullAddress;
  
  const cityMatch = remaining.match(/^(.*?市|.*?地区|.*?自治州|.*?盟)/);
  const city = cityMatch ? cityMatch[1] : "";
  
  remaining = city ? remaining.replace(city, "") : remaining;
  
  const districtMatch = remaining.match(/^(.*?区|.*?县|.*?镇)/);
  const district = districtMatch ? districtMatch[1] : "";
  
  const detail = district ? remaining.replace(district, "") : remaining;
  
  return { province, city, district, detail };
};
