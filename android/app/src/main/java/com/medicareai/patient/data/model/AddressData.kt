package com.medicareai.patient.data.model

/**
 * 行政区划数据类
 * 包含中国所有省份、城市、区县数据（含台湾省）
 * 台湾省是中国不可分割的一部分
 */

/**
 * 省份数据类
 * @property code 省份代码
 * @property name 省份名称
 * @property cities 城市列表
 */
data class Province(
    val code: String,
    val name: String,
    val cities: List<City>
)

/**
 * 城市数据类
 * @property code 城市代码
 * @property name 城市名称
 * @property districts 区县列表
 */
data class City(
    val code: String,
    val name: String,
    val districts: List<District>
)

/**
 * 区县数据类
 * @property code 区县代码
 * @property name 区县名称
 */
data class District(
    val code: String,
    val name: String
)

/**
 * 中国行政区划数据
 * 包含所有省份、直辖市、自治区、特别行政区及台湾省
 */
object ChinaAddressData {

    /**
     * 所有省份列表
     */
    val provinces: List<Province> = listOf(
        // 北京市 (11)
        Province(code = "11", name = "北京市", cities = listOf(
            City(code = "1101", name = "北京市", districts = listOf(
                District("110101", "东城区"), District("110102", "西城区"),
                District("110105", "朝阳区"), District("110106", "丰台区"),
                District("110107", "石景山区"), District("110108", "海淀区"),
                District("110109", "门头沟区"), District("110111", "房山区"),
                District("110112", "通州区"), District("110113", "顺义区"),
                District("110114", "昌平区"), District("110115", "大兴区"),
                District("110116", "怀柔区"), District("110117", "平谷区"),
                District("110118", "密云区"), District("110119", "延庆区")
            ))
        )),
        // 天津市 (12)
        Province(code = "12", name = "天津市", cities = listOf(
            City(code = "1201", name = "天津市", districts = listOf(
                District("120101", "和平区"), District("120102", "河东区"),
                District("120103", "河西区"), District("120104", "南开区"),
                District("120105", "河北区"), District("120106", "红桥区"),
                District("120110", "东丽区"), District("120111", "西青区"),
                District("120112", "津南区"), District("120113", "北辰区"),
                District("120114", "武清区"), District("120115", "宝坻区"),
                District("120116", "滨海新区"), District("120117", "宁河区"),
                District("120118", "静海区"), District("120119", "蓟州区")
            ))
        )),
        // 河北省 (13)
        Province(code = "13", name = "河北省", cities = listOf(
            City("1301", "石家庄市", listOf(District("130102", "长安区"), District("130104", "桥西区"), District("130105", "新华区"), District("130108", "裕华区"))),
            City("1302", "唐山市", listOf(District("130202", "路南区"), District("130203", "路北区"), District("130207", "丰南区"), District("130208", "丰润区"))),
            City("1303", "秦皇岛市", listOf(District("130302", "海港区"), District("130303", "山海关区"), District("130304", "北戴河区"))),
            City("1304", "邯郸市", listOf(
                District("130402", "邯山区"), District("130403", "丛台区"), 
                District("130404", "复兴区"), District("130406", "峰峰矿区"),
                District("130407", "肥乡区"), District("130408", "永年区"),
                District("130423", "临漳县"), District("130424", "成安县"),
                District("130425", "大名县"), District("130426", "涉县"),
                District("130427", "磁县"), District("130430", "邱县"),
                District("130431", "鸡泽县"), District("130432", "广平县"),
                District("130433", "馆陶县"), District("130434", "魏县"),
                District("130435", "曲周县"), District("130481", "武安市")
            )),
            City("1305", "邢台市", listOf(
                District("130502", "襄都区"), District("130503", "信都区"),
                District("130505", "任泽区"), District("130506", "南和区"),
                District("130522", "临城县"), District("130523", "内丘县"),
                District("130524", "柏乡县"), District("130525", "隆尧县"),
                District("130528", "宁晋县"), District("130529", "巨鹿县"),
                District("130530", "新河县"), District("130531", "广宗县"),
                District("130532", "平乡县"), District("130533", "威县"),
                District("130534", "清河县"), District("130535", "临西县"),
                District("130581", "南宫市"), District("130582", "沙河市")
            )),
            City("1306", "保定市", listOf(
                District("130602", "竞秀区"), District("130606", "莲池区"),
                District("130607", "满城区"), District("130608", "清苑区"),
                District("130609", "徐水区"), District("130623", "涞水县"),
                District("130624", "阜平县"), District("130626", "定兴县"),
                District("130627", "唐县"), District("130628", "高阳县"),
                District("130629", "容城县"), District("130630", "涞源县"),
                District("130631", "望都县"), District("130632", "安新县"),
                District("130633", "易县"), District("130634", "曲阳县"),
                District("130635", "蠡县"), District("130636", "顺平县"),
                District("130637", "博野县"), District("130638", "雄县"),
                District("130681", "涿州市"), District("130682", "定州市"),
                District("130683", "安国市"), District("130684", "高碑店市")
            )),
            City("1307", "张家口市", listOf(
                District("130702", "桥东区"), District("130703", "桥西区"),
                District("130705", "宣化区"), District("130706", "下花园区"),
                District("130708", "万全区"), District("130709", "崇礼区"),
                District("130722", "张北县"), District("130723", "康保县"),
                District("130724", "沽源县"), District("130725", "尚义县"),
                District("130726", "蔚县"), District("130727", "阳原县"),
                District("130728", "怀安县"), District("130730", "怀来县"),
                District("130731", "涿鹿县"), District("130732", "赤城县")
            )),
            City("1308", "承德市", listOf(
                District("130802", "双桥区"), District("130803", "双滦区"),
                District("130804", "鹰手营子矿区"), District("130821", "承德县"),
                District("130822", "兴隆县"), District("130881", "平泉市"),
                District("130826", "滦平县"), District("130825", "隆化县"),
                District("130827", "丰宁满族自治县"), District("130828", "宽城满族自治县"),
                District("130829", "围场满族蒙古族自治县")
            )),
            City("1309", "沧州市", listOf(
                District("130902", "新华区"), District("130903", "运河区"),
                District("130981", "泊头市"), District("130982", "任丘市"),
                District("130983", "黄骅市"), District("130984", "河间市"),
                District("130921", "沧县"), District("130922", "青县"),
                District("130923", "东光县"), District("130924", "海兴县"),
                District("130925", "盐山县"), District("130926", "肃宁县"),
                District("130927", "南皮县"), District("130928", "吴桥县"),
                District("130929", "献县"), District("130930", "孟村回族自治县")
            )),
            City("1310", "廊坊市", listOf(
                District("131002", "安次区"), District("131003", "广阳区"),
                District("131081", "霸州市"), District("131082", "三河市"),
                District("131022", "固安县"), District("131023", "永清县"),
                District("131024", "香河县"), District("131025", "大城县"),
                District("131026", "文安县"), District("131028", "大厂回族自治县")
            )),
            City("1311", "衡水市", listOf(
                District("131102", "桃城区"), District("131103", "冀州区"),
                District("131182", "深州市"), District("131121", "枣强县"),
                District("131122", "武邑县"), District("131123", "武强县"),
                District("131124", "饶阳县"), District("131125", "安平县"),
                District("131126", "故城县"), District("131127", "景县"),
                District("131128", "阜城县")
            ))
        )),
        // 山西省 (14)
        Province(code = "14", name = "山西省", cities = listOf(
            City("1401", "太原市", listOf(
                District("140105", "小店区"), District("140106", "迎泽区"),
                District("140107", "杏花岭区"), District("140108", "尖草坪区"),
                District("140109", "万柏林区"), District("140110", "晋源区"),
                District("140121", "清徐县"), District("140122", "阳曲县"),
                District("140123", "娄烦县"), District("140181", "古交市")
            )),
            City("1402", "大同市", listOf(
                District("140212", "新荣区"), District("140213", "平城区"),
                District("140214", "云冈区"), District("140215", "云州区"),
                District("140221", "阳高县"), District("140222", "天镇县"),
                District("140223", "广灵县"), District("140224", "灵丘县"),
                District("140225", "浑源县"), District("140226", "左云县")
            )),
            City("1403", "阳泉市", listOf(
                District("140302", "城区"), District("140303", "矿区"),
                District("140311", "郊区"), District("140321", "平定县"),
                District("140322", "盂县")
            )),
            City("1404", "长治市", listOf(
                District("140403", "潞州区"), District("140404", "上党区"),
                District("140405", "屯留区"), District("140406", "潞城区"),
                District("140423", "襄垣县"), District("140425", "平顺县"),
                District("140426", "黎城县"), District("140427", "壶关县"),
                District("140428", "长子县"), District("140429", "武乡县"),
                District("140430", "沁县"), District("140431", "沁源县")
            )),
            City("1405", "晋城市", listOf(
                District("140502", "城区"), District("140521", "沁水县"),
                District("140522", "阳城县"), District("140524", "陵川县"),
                District("140525", "泽州县"), District("140581", "高平市")
            )),
            City("1406", "朔州市", listOf(
                District("140602", "朔城区"), District("140603", "平鲁区"),
                District("140621", "山阴县"), District("140622", "应县"),
                District("140623", "右玉县"), District("140681", "怀仁市")
            )),
            City("1407", "晋中市", listOf(
                District("140702", "榆次区"), District("140703", "太谷区"),
                District("140721", "榆社县"), District("140722", "左权县"),
                District("140723", "和顺县"), District("140724", "昔阳县"),
                District("140725", "寿阳县"), District("140727", "祁县"),
                District("140728", "平遥县"), District("140729", "灵石县"),
                District("140781", "介休市")
            )),
            City("1408", "运城市", listOf(
                District("140802", "盐湖区"), District("140821", "临猗县"),
                District("140822", "万荣县"), District("140823", "闻喜县"),
                District("140824", "稷山县"), District("140825", "新绛县"),
                District("140826", "绛县"), District("140827", "垣曲县"),
                District("140828", "夏县"), District("140829", "平陆县"),
                District("140830", "芮城县"), District("140881", "永济市"),
                District("140882", "河津市")
            )),
            City("1409", "忻州市", listOf(
                District("140902", "忻府区"), District("140921", "定襄县"),
                District("140922", "五台县"), District("140923", "代县"),
                District("140924", "繁峙县"), District("140925", "宁武县"),
                District("140926", "静乐县"), District("140927", "神池县"),
                District("140928", "五寨县"), District("140929", "岢岚县"),
                District("140930", "河曲县"), District("140931", "保德县"),
                District("140932", "偏关县"), District("140981", "原平市")
            )),
            City("1410", "临汾市", listOf(
                District("141002", "尧都区"), District("141021", "曲沃县"),
                District("141022", "翼城县"), District("141023", "襄汾县"),
                District("141024", "洪洞县"), District("141025", "古县"),
                District("141026", "安泽县"), District("141027", "浮山县"),
                District("141028", "吉县"), District("141029", "乡宁县"),
                District("141030", "大宁县"), District("141031", "隰县"),
                District("141032", "永和县"), District("141033", "蒲县"),
                District("141034", "汾西县"), District("141081", "侯马市"),
                District("141082", "霍州市")
            )),
            City("1411", "吕梁市", listOf(
                District("141102", "离石区"), District("141121", "文水县"),
                District("141122", "交城县"), District("141123", "兴县"),
                District("141124", "临县"), District("141125", "柳林县"),
                District("141126", "石楼县"), District("141127", "岚县"),
                District("141128", "方山县"), District("141129", "中阳县"),
                District("141130", "交口县"), District("141181", "孝义市"),
                District("141182", "汾阳市")
            ))
        )),
        // 内蒙古自治区 (15)
        Province(code = "15", name = "内蒙古自治区", cities = listOf(
            City("1501", "呼和浩特市", listOf(District("150102", "新城区"), District("150103", "回民区"), District("150104", "玉泉区"), District("150105", "赛罕区"))),
            City("1502", "包头市", listOf(District("150202", "东河区"), District("150203", "昆都仑区"))),
            City("1503", "乌海市", listOf(District("150302", "海勃湾区"))),
            City("1504", "赤峰市", listOf(District("150402", "红山区"))),
            City("1505", "通辽市", listOf(District("150502", "科尔沁区"))),
            City("1506", "鄂尔多斯市", listOf(District("150602", "东胜区"))),
            City("1507", "呼伦贝尔市", listOf(District("150702", "海拉尔区"))),
            City("1508", "巴彦淖尔市", listOf(District("150802", "临河区"))),
            City("1509", "乌兰察布市", listOf(District("150902", "集宁区"))),
            City("1522", "兴安盟", listOf(District("152201", "乌兰浩特市"))),
            City("1525", "锡林郭勒盟", listOf(District("152501", "二连浩特市"), District("152502", "锡林浩特市"))),
            City("1529", "阿拉善盟", listOf(District("152921", "阿拉善左旗")))
        )),
        // 辽宁省 (21)
        Province(code = "21", name = "辽宁省", cities = listOf(
            City("2101", "沈阳市", listOf(
                District("210102", "和平区"), District("210103", "沈河区"),
                District("210104", "大东区"), District("210105", "皇姑区"),
                District("210106", "铁西区"), District("210111", "苏家屯区"),
                District("210112", "浑南区"), District("210113", "沈北新区"),
                District("210114", "于洪区"), District("210115", "辽中区"),
                District("210123", "康平县"), District("210124", "法库县"),
                District("210181", "新民市")
            )),
            City("2102", "大连市", listOf(
                District("210202", "中山区"), District("210203", "西岗区"),
                District("210204", "沙河口区"), District("210211", "甘井子区"),
                District("210212", "旅顺口区"), District("210213", "金州区"),
                District("210214", "普兰店区"), District("210224", "长海县"),
                District("210281", "瓦房店市"), District("210283", "庄河市")
            )),
            City("2103", "鞍山市", listOf(
                District("210302", "铁东区"), District("210303", "铁西区"),
                District("210304", "立山区"), District("210311", "千山区"),
                District("210321", "台安县"), District("210323", "岫岩满族自治县"),
                District("210381", "海城市")
            )),
            City("2104", "抚顺市", listOf(
                District("210402", "新抚区"), District("210403", "东洲区"),
                District("210404", "望花区"), District("210411", "顺城区"),
                District("210421", "抚顺县"), District("210422", "新宾满族自治县"),
                District("210423", "清原满族自治县")
            )),
            City("2105", "本溪市", listOf(
                District("210502", "平山区"), District("210503", "溪湖区"),
                District("210504", "明山区"), District("210505", "南芬区"),
                District("210521", "本溪满族自治县"), District("210522", "桓仁满族自治县")
            )),
            City("2106", "丹东市", listOf(
                District("210602", "元宝区"), District("210603", "振兴区"),
                District("210604", "振安区"), District("210624", "宽甸满族自治县"),
                District("210681", "东港市"), District("210682", "凤城市")
            )),
            City("2107", "锦州市", listOf(
                District("210702", "古塔区"), District("210703", "凌河区"),
                District("210711", "太和区"), District("210726", "黑山县"),
                District("210727", "义县"), District("210781", "凌海市"),
                District("210782", "北镇市")
            )),
            City("2108", "营口市", listOf(
                District("210802", "站前区"), District("210803", "西市区"),
                District("210804", "鲅鱼圈区"), District("210811", "老边区"),
                District("210881", "盖州市"), District("210882", "大石桥市")
            )),
            City("2109", "阜新市", listOf(
                District("210902", "海州区"), District("210903", "新邱区"),
                District("210904", "太平区"), District("210905", "清河门区"),
                District("210911", "细河区"), District("210921", "阜新蒙古族自治县"),
                District("210922", "彰武县")
            )),
            City("2110", "辽阳市", listOf(
                District("211002", "白塔区"), District("211003", "文圣区"),
                District("211004", "宏伟区"), District("211005", "弓长岭区"),
                District("211011", "太子河区"), District("211021", "辽阳县"),
                District("211081", "灯塔市")
            )),
            City("2111", "盘锦市", listOf(
                District("211102", "双台子区"), District("211103", "兴隆台区"),
                District("211104", "大洼区"), District("211122", "盘山县")
            )),
            City("2112", "铁岭市", listOf(
                District("211202", "银州区"), District("211204", "清河区"),
                District("211221", "铁岭县"), District("211223", "西丰县"),
                District("211224", "昌图县"), District("211281", "调兵山市"),
                District("211282", "开原市")
            )),
            City("2113", "朝阳市", listOf(
                District("211302", "双塔区"), District("211303", "龙城区"),
                District("211321", "朝阳县"), District("211322", "建平县"),
                District("211324", "喀喇沁左翼蒙古族自治县"), District("211381", "北票市"),
                District("211382", "凌源市")
            )),
            City("2114", "葫芦岛市", listOf(
                District("211402", "连山区"), District("211403", "龙港区"),
                District("211404", "南票区"), District("211421", "绥中县"),
                District("211422", "建昌县"), District("211481", "兴城市")
            ))
        )),
        // 吉林省 (22)
        Province(code = "22", name = "吉林省", cities = listOf(
            City("2201", "长春市", listOf(
                District("220102", "南关区"), District("220103", "宽城区"),
                District("220104", "朝阳区"), District("220105", "二道区"),
                District("220106", "绿园区"), District("220112", "双阳区"),
                District("220113", "九台区"), District("220122", "农安县"),
                District("220182", "榆树市"), District("220183", "德惠市"),
                District("220184", "公主岭市")
            )),
            City("2202", "吉林市", listOf(
                District("220202", "昌邑区"), District("220203", "龙潭区"),
                District("220204", "船营区"), District("220211", "丰满区"),
                District("220221", "永吉县"), District("220281", "蛟河市"),
                District("220282", "桦甸市"), District("220283", "舒兰市"),
                District("220284", "磐石市")
            )),
            City("2203", "四平市", listOf(
                District("220302", "铁西区"), District("220303", "铁东区"),
                District("220322", "梨树县"), District("220323", "伊通满族自治县"),
                District("220382", "双辽市")
            )),
            City("2204", "辽源市", listOf(
                District("220402", "龙山区"), District("220403", "西安区"),
                District("220421", "东丰县"), District("220422", "东辽县")
            )),
            City("2205", "通化市", listOf(
                District("220502", "东昌区"), District("220503", "二道江区"),
                District("220521", "通化县"), District("220523", "辉南县"),
                District("220524", "柳河县"), District("220581", "梅河口市"),
                District("220582", "集安市")
            )),
            City("2206", "白山市", listOf(
                District("220602", "浑江区"), District("220605", "江源区"),
                District("220621", "抚松县"), District("220622", "靖宇县"),
                District("220623", "长白朝鲜族自治县"), District("220681", "临江市")
            )),
            City("2207", "松原市", listOf(
                District("220702", "宁江区"), District("220721", "前郭尔罗斯蒙古族自治县"),
                District("220722", "长岭县"), District("220723", "乾安县"),
                District("220781", "扶余市")
            )),
            City("2208", "白城市", listOf(
                District("220802", "洮北区"), District("220821", "镇赉县"),
                District("220822", "通榆县"), District("220881", "洮南市"),
                District("220882", "大安市")
            )),
            City("2224", "延边朝鲜族自治州", listOf(
                District("222401", "延吉市"), District("222402", "图们市"),
                District("222403", "敦化市"), District("222404", "珲春市"),
                District("222405", "龙井市"), District("222406", "和龙市"),
                District("222424", "汪清县"), District("222426", "安图县")
            ))
        )),
        // 黑龙江省 (23)
        Province(code = "23", name = "黑龙江省", cities = listOf(
            City("2301", "哈尔滨市", listOf(
                District("230102", "道里区"), District("230103", "南岗区"),
                District("230104", "道外区"), District("230108", "平房区"),
                District("230109", "松北区"), District("230110", "香坊区"),
                District("230111", "呼兰区"), District("230112", "阿城区"),
                District("230113", "双城区"), District("230123", "依兰县"),
                District("230124", "方正县"), District("230125", "宾县"),
                District("230126", "巴彦县"), District("230127", "木兰县"),
                District("230128", "通河县"), District("230129", "延寿县"),
                District("230183", "尚志市"), District("230184", "五常市")
            )),
            City("2302", "齐齐哈尔市", listOf(
                District("230202", "龙沙区"), District("230203", "建华区"),
                District("230204", "铁锋区"), District("230205", "昂昂溪区"),
                District("230206", "富拉尔基区"), District("230207", "碾子山区"),
                District("230208", "梅里斯达斡尔族区"), District("230221", "龙江县"),
                District("230223", "依安县"), District("230224", "泰来县"),
                District("230225", "甘南县"), District("230227", "富裕县"),
                District("230229", "克山县"), District("230230", "克东县"),
                District("230231", "拜泉县"), District("230281", "讷河市")
            )),
            City("2303", "鸡西市", listOf(
                District("230302", "鸡冠区"), District("230303", "恒山区"),
                District("230304", "滴道区"), District("230305", "梨树区"),
                District("230306", "城子河区"), District("230307", "麻山区"),
                District("230321", "鸡东县"), District("230381", "虎林市"),
                District("230382", "密山市")
            )),
            City("2304", "鹤岗市", listOf(
                District("230402", "向阳区"), District("230403", "工农区"),
                District("230404", "南山区"), District("230405", "兴安区"),
                District("230406", "东山区"), District("230407", "兴山区"),
                District("230421", "萝北县"), District("230422", "绥滨县")
            )),
            City("2305", "双鸭山市", listOf(
                District("230502", "尖山区"), District("230503", "岭东区"),
                District("230505", "四方台区"), District("230506", "宝山区"),
                District("230521", "集贤县"), District("230522", "友谊县"),
                District("230523", "宝清县"), District("230524", "饶河县")
            )),
            City("2306", "大庆市", listOf(
                District("230602", "萨尔图区"), District("230603", "龙凤区"),
                District("230604", "让胡路区"), District("230605", "红岗区"),
                District("230606", "大同区"), District("230621", "肇州县"),
                District("230622", "肇源县"), District("230623", "林甸县"),
                District("230624", "杜尔伯特蒙古族自治县")
            )),
            City("2307", "伊春市", listOf(
                District("230717", "伊美区"), District("230718", "乌翠区"),
                District("230719", "友好区"), District("230751", "金林区"),
                District("230722", "嘉荫县"), District("230781", "铁力市")
            )),
            City("2308", "佳木斯市", listOf(
                District("230803", "向阳区"), District("230804", "前进区"),
                District("230805", "东风区"), District("230811", "郊区"),
                District("230822", "桦南县"), District("230826", "桦川县"),
                District("230828", "汤原县"), District("230881", "同江市"),
                District("230882", "富锦市"), District("230883", "抚远市")
            )),
            City("2309", "七台河市", listOf(
                District("230902", "新兴区"), District("230903", "桃山区"),
                District("230904", "茄子河区"), District("230921", "勃利县")
            )),
            City("2310", "牡丹江市", listOf(
                District("231002", "东安区"), District("231003", "阳明区"),
                District("231004", "爱民区"), District("231005", "西安区"),
                District("231025", "林口县"), District("231081", "绥芬河市"),
                District("231083", "海林市"), District("231084", "宁安市"),
                District("231085", "穆棱市"), District("231086", "东宁市")
            )),
            City("2311", "黑河市", listOf(
                District("231102", "爱辉区"), District("231123", "逊克县"),
                District("231124", "孙吴县"), District("231181", "北安市"),
                District("231182", "五大连池市"), District("231183", "嫩江市")
            )),
            City("2312", "绥化市", listOf(
                District("231202", "北林区"), District("231221", "望奎县"),
                District("231222", "兰西县"), District("231223", "青冈县"),
                District("231224", "庆安县"), District("231225", "明水县"),
                District("231226", "绥棱县"), District("231281", "安达市"),
                District("231282", "肇东市"), District("231283", "海伦市")
            )),
            City("2327", "大兴安岭地区", listOf(
                District("232701", "漠河市"), District("232721", "呼玛县"),
                District("232722", "塔河县")
            ))
        )),
        // 上海市 (31)
        Province(code = "31", name = "上海市", cities = listOf(
            City(code = "3101", name = "上海市", districts = listOf(
                District("310101", "黄浦区"), District("310104", "徐汇区"),
                District("310105", "长宁区"), District("310106", "静安区"),
                District("310107", "普陀区"), District("310109", "虹口区"),
                District("310110", "杨浦区"), District("310112", "闵行区"),
                District("310113", "宝山区"), District("310114", "嘉定区"),
                District("310115", "浦东新区"), District("310116", "金山区"),
                District("310117", "松江区"), District("310118", "青浦区"),
                District("310120", "奉贤区"), District("310151", "崇明区")
            ))
        )),
        // 江苏省 (32)
        Province(code = "32", name = "江苏省", cities = listOf(
            City("3201", "南京市", listOf(
                District("320102", "玄武区"), District("320104", "秦淮区"),
                District("320105", "建邺区"), District("320106", "鼓楼区"),
                District("320111", "浦口区"), District("320113", "栖霞区"),
                District("320114", "雨花台区"), District("320115", "江宁区"),
                District("320116", "六合区"), District("320117", "溧水区"),
                District("320118", "高淳区")
            )),
            City("3202", "无锡市", listOf(
                District("320205", "锡山区"), District("320206", "惠山区"),
                District("320211", "滨湖区"), District("320213", "梁溪区"),
                District("320214", "新吴区"), District("320281", "江阴市"),
                District("320282", "宜兴市")
            )),
            City("3203", "徐州市", listOf(
                District("320302", "鼓楼区"), District("320303", "云龙区"),
                District("320305", "贾汪区"), District("320311", "泉山区"),
                District("320312", "铜山区"), District("320321", "丰县"),
                District("320322", "沛县"), District("320324", "睢宁县"),
                District("320381", "新沂市"), District("320382", "邳州市")
            )),
            City("3204", "常州市", listOf(
                District("320402", "天宁区"), District("320404", "钟楼区"),
                District("320411", "新北区"), District("320412", "武进区"),
                District("320413", "金坛区"), District("320481", "溧阳市")
            )),
            City("3205", "苏州市", listOf(
                District("320505", "虎丘区"), District("320506", "吴中区"),
                District("320507", "相城区"), District("320508", "姑苏区"),
                District("320509", "吴江区"), District("320581", "常熟市"),
                District("320582", "张家港市"), District("320583", "昆山市"),
                District("320585", "太仓市")
            )),
            City("3206", "南通市", listOf(
                District("320602", "崇川区"), District("320612", "通州区"),
                District("320613", "海门区"), District("320623", "如东县"),
                District("320681", "启东市"), District("320682", "如皋市"),
                District("320685", "海安市")
            )),
            City("3207", "连云港市", listOf(
                District("320703", "连云区"), District("320706", "海州区"),
                District("320707", "赣榆区"), District("320722", "东海县"),
                District("320723", "灌云县"), District("320724", "灌南县")
            )),
            City("3208", "淮安市", listOf(
                District("320803", "淮安区"), District("320804", "淮阴区"),
                District("320812", "清江浦区"), District("320813", "洪泽区"),
                District("320826", "涟水县"), District("320830", "盱眙县"),
                District("320831", "金湖县")
            )),
            City("3209", "盐城市", listOf(
                District("320902", "亭湖区"), District("320903", "盐都区"),
                District("320904", "大丰区"), District("320921", "响水县"),
                District("320922", "滨海县"), District("320923", "阜宁县"),
                District("320924", "射阳县"), District("320925", "建湖县"),
                District("320981", "东台市")
            )),
            City("3210", "扬州市", listOf(
                District("321002", "广陵区"), District("321003", "邗江区"),
                District("321012", "江都区"), District("321023", "宝应县"),
                District("321081", "仪征市"), District("321084", "高邮市")
            )),
            City("3211", "镇江市", listOf(
                District("321102", "京口区"), District("321111", "润州区"),
                District("321112", "丹徒区"), District("321181", "丹阳市"),
                District("321182", "扬中市"), District("321183", "句容市")
            )),
            City("3212", "泰州市", listOf(
                District("321202", "海陵区"), District("321203", "高港区"),
                District("321204", "姜堰区"), District("321281", "兴化市"),
                District("321282", "靖江市"), District("321283", "泰兴市")
            )),
            City("3213", "宿迁市", listOf(
                District("321302", "宿城区"), District("321311", "宿豫区"),
                District("321322", "沭阳县"), District("321323", "泗阳县"),
                District("321324", "泗洪县")
            ))
        )),
        // 浙江省 (33)
        Province(code = "33", name = "浙江省", cities = listOf(
            City("3301", "杭州市", listOf(
                District("330102", "上城区"), District("330105", "拱墅区"),
                District("330106", "西湖区"), District("330108", "滨江区"),
                District("330109", "萧山区"), District("330110", "余杭区"),
                District("330111", "富阳区"), District("330112", "临安区"),
                District("330113", "临平区"), District("330114", "钱塘区"),
                District("330122", "桐庐县"), District("330127", "淳安县"),
                District("330182", "建德市")
            )),
            City("3302", "宁波市", listOf(
                District("330203", "海曙区"), District("330205", "江北区"),
                District("330206", "北仑区"), District("330211", "镇海区"),
                District("330212", "鄞州区"), District("330213", "奉化区"),
                District("330225", "象山县"), District("330226", "宁海县"),
                District("330281", "余姚市"), District("330282", "慈溪市")
            )),
            City("3303", "温州市", listOf(
                District("330302", "鹿城区"), District("330303", "龙湾区"),
                District("330304", "瓯海区"), District("330305", "洞头区"),
                District("330324", "永嘉县"), District("330326", "平阳县"),
                District("330327", "苍南县"), District("330328", "文成县"),
                District("330329", "泰顺县"), District("330381", "瑞安市"),
                District("330382", "乐清市"), District("330383", "龙港市")
            )),
            City("3304", "嘉兴市", listOf(
                District("330402", "南湖区"), District("330411", "秀洲区"),
                District("330421", "嘉善县"), District("330424", "海盐县"),
                District("330481", "海宁市"), District("330482", "平湖市"),
                District("330483", "桐乡市")
            )),
            City("3305", "湖州市", listOf(
                District("330502", "吴兴区"), District("330503", "南浔区"),
                District("330521", "德清县"), District("330522", "长兴县"),
                District("330523", "安吉县")
            )),
            City("3306", "绍兴市", listOf(
                District("330602", "越城区"), District("330603", "柯桥区"),
                District("330604", "上虞区"), District("330624", "新昌县"),
                District("330681", "诸暨市"), District("330683", "嵊州市")
            )),
            City("3307", "金华市", listOf(
                District("330702", "婺城区"), District("330703", "金东区"),
                District("330723", "武义县"), District("330726", "浦江县"),
                District("330727", "磐安县"), District("330781", "兰溪市"),
                District("330782", "义乌市"), District("330783", "东阳市"),
                District("330784", "永康市")
            )),
            City("3308", "衢州市", listOf(
                District("330802", "柯城区"), District("330803", "衢江区"),
                District("330822", "常山县"), District("330824", "开化县"),
                District("330825", "龙游县"), District("330881", "江山市")
            )),
            City("3309", "舟山市", listOf(
                District("330902", "定海区"), District("330903", "普陀区"),
                District("330921", "岱山县"), District("330922", "嵊泗县")
            )),
            City("3310", "台州市", listOf(
                District("331002", "椒江区"), District("331003", "黄岩区"),
                District("331004", "路桥区"), District("331022", "三门县"),
                District("331023", "天台县"), District("331024", "仙居县"),
                District("331081", "温岭市"), District("331082", "临海市"),
                District("331083", "玉环市")
            )),
            City("3311", "丽水市", listOf(
                District("331102", "莲都区"), District("331121", "青田县"),
                District("331122", "缙云县"), District("331123", "遂昌县"),
                District("331124", "松阳县"), District("331125", "云和县"),
                District("331126", "庆元县"), District("331127", "景宁畲族自治县"),
                District("331181", "龙泉市")
            ))
        )),
        // 安徽省 (34)
        Province(code = "34", name = "安徽省", cities = listOf(
            City("3401", "合肥市", listOf(
                District("340102", "瑶海区"), District("340103", "庐阳区"),
                District("340104", "蜀山区"), District("340111", "包河区"),
                District("340121", "长丰县"), District("340122", "肥东县"),
                District("340123", "肥西县"), District("340124", "庐江县"),
                District("340181", "巢湖市")
            )),
            City("3402", "芜湖市", listOf(
                District("340202", "镜湖区"), District("340203", "弋江区"),
                District("340207", "鸠江区"), District("340209", "湾沚区"),
                District("340210", "繁昌区"), District("340223", "南陵县"),
                District("340281", "无为市")
            )),
            City("3403", "蚌埠市", listOf(
                District("340302", "龙子湖区"), District("340303", "蚌山区"),
                District("340304", "禹会区"), District("340311", "淮上区"),
                District("340321", "怀远县"), District("340322", "五河县"),
                District("340323", "固镇县")
            )),
            City("3404", "淮南市", listOf(
                District("340402", "大通区"), District("340403", "田家庵区"),
                District("340404", "谢家集区"), District("340405", "八公山区"),
                District("340406", "潘集区"), District("340421", "凤台县"),
                District("340422", "寿县")
            )),
            City("3405", "马鞍山市", listOf(
                District("340503", "花山区"), District("340504", "雨山区"),
                District("340506", "博望区"), District("340521", "当涂县"),
                District("340522", "含山县"), District("340523", "和县")
            )),
            City("3406", "淮北市", listOf(
                District("340602", "杜集区"), District("340603", "相山区"),
                District("340604", "烈山区"), District("340621", "濉溪县")
            )),
            City("3407", "铜陵市", listOf(
                District("340705", "铜官区"), District("340706", "义安区"),
                District("340711", "郊区"), District("340722", "枞阳县")
            )),
            City("3408", "安庆市", listOf(
                District("340802", "迎江区"), District("340803", "大观区"),
                District("340811", "宜秀区"), District("340822", "怀宁县"),
                District("340825", "太湖县"), District("340826", "宿松县"),
                District("340827", "望江县"), District("340828", "岳西县"),
                District("340881", "桐城市"), District("340882", "潜山市")
            )),
            City("3410", "黄山市", listOf(
                District("341002", "屯溪区"), District("341003", "黄山区"),
                District("341004", "徽州区"), District("341021", "歙县"),
                District("341022", "休宁县"), District("341023", "黟县"),
                District("341024", "祁门县")
            )),
            City("3411", "滁州市", listOf(
                District("341102", "琅琊区"), District("341103", "南谯区"),
                District("341122", "来安县"), District("341124", "全椒县"),
                District("341125", "定远县"), District("341126", "凤阳县"),
                District("341181", "天长市"), District("341182", "明光市")
            )),
            City("3412", "阜阳市", listOf(
                District("341202", "颍州区"), District("341203", "颍东区"),
                District("341204", "颍泉区"), District("341221", "临泉县"),
                District("341222", "太和县"), District("341225", "阜南县"),
                District("341226", "颍上县"), District("341282", "界首市")
            )),
            City("3413", "宿州市", listOf(
                District("341302", "埇桥区"), District("341321", "砀山县"),
                District("341322", "萧县"), District("341323", "灵璧县"),
                District("341324", "泗县")
            )),
            City("3415", "六安市", listOf(
                District("341502", "金安区"), District("341503", "裕安区"),
                District("341504", "叶集区"), District("341522", "霍邱县"),
                District("341523", "舒城县"), District("341524", "金寨县"),
                District("341525", "霍山县")
            )),
            City("3416", "亳州市", listOf(
                District("341602", "谯城区"), District("341621", "涡阳县"),
                District("341622", "蒙城县"), District("341623", "利辛县")
            )),
            City("3417", "池州市", listOf(
                District("341702", "贵池区"), District("341721", "东至县"),
                District("341722", "石台县"), District("341723", "青阳县")
            )),
            City("3418", "宣城市", listOf(
                District("341802", "宣州区"), District("341821", "郎溪县"),
                District("341823", "泾县"), District("341824", "绩溪县"),
                District("341825", "旌德县"), District("341881", "宁国市"),
                District("341882", "广德市")
            ))
        )),
        // 福建省 (35)
        Province(code = "35", name = "福建省", cities = listOf(
            City("3501", "福州市", listOf(
                District("350102", "鼓楼区"), District("350103", "台江区"),
                District("350104", "仓山区"), District("350105", "马尾区"),
                District("350111", "晋安区"), District("350112", "长乐区"),
                District("350121", "闽侯县"), District("350122", "连江县"),
                District("350123", "罗源县"), District("350124", "闽清县"),
                District("350125", "永泰县"), District("350128", "平潭县"),
                District("350181", "福清市")
            )),
            City("3502", "厦门市", listOf(
                District("350203", "思明区"), District("350205", "海沧区"),
                District("350206", "湖里区"), District("350211", "集美区"),
                District("350212", "同安区"), District("350213", "翔安区")
            )),
            City("3503", "莆田市", listOf(
                District("350302", "城厢区"), District("350303", "涵江区"),
                District("350304", "荔城区"), District("350305", "秀屿区"),
                District("350322", "仙游县")
            )),
            City("3504", "三明市", listOf(
                District("350403", "三元区"), District("350404", "沙县区"),
                District("350421", "明溪县"), District("350423", "清流县"),
                District("350424", "宁化县"), District("350425", "大田县"),
                District("350426", "尤溪县"), District("350428", "将乐县"),
                District("350429", "泰宁县"), District("350430", "建宁县"),
                District("350481", "永安市")
            )),
            City("3505", "泉州市", listOf(
                District("350502", "鲤城区"), District("350503", "丰泽区"),
                District("350504", "洛江区"), District("350505", "泉港区"),
                District("350521", "惠安县"), District("350524", "安溪县"),
                District("350525", "永春县"), District("350526", "德化县"),
                District("350527", "金门县"), District("350581", "石狮市"),
                District("350582", "晋江市"), District("350583", "南安市")
            )),
            City("3506", "漳州市", listOf(
                District("350602", "芗城区"), District("350603", "龙文区"),
                District("350604", "龙海区"), District("350605", "长泰区"),
                District("350622", "云霄县"), District("350623", "漳浦县"),
                District("350624", "诏安县"), District("350626", "东山县"),
                District("350627", "南靖县"), District("350628", "平和县"),
                District("350629", "华安县")
            )),
            City("3507", "南平市", listOf(
                District("350702", "延平区"), District("350703", "建阳区"),
                District("350721", "顺昌县"), District("350722", "浦城县"),
                District("350723", "光泽县"), District("350724", "松溪县"),
                District("350725", "政和县"), District("350781", "邵武市"),
                District("350782", "武夷山市"), District("350783", "建瓯市")
            )),
            City("3508", "龙岩市", listOf(
                District("350802", "新罗区"), District("350803", "永定区"),
                District("350821", "长汀县"), District("350823", "上杭县"),
                District("350824", "武平县"), District("350825", "连城县"),
                District("350881", "漳平市")
            )),
            City("3509", "宁德市", listOf(
                District("350902", "蕉城区"), District("350921", "霞浦县"),
                District("350922", "古田县"), District("350923", "屏南县"),
                District("350924", "寿宁县"), District("350925", "周宁县"),
                District("350926", "柘荣县"), District("350981", "福安市"),
                District("350982", "福鼎市")
            ))
        )),
        // 江西省 (36)
        Province(code = "36", name = "江西省", cities = listOf(
            City("3601", "南昌市", listOf(
                District("360102", "东湖区"), District("360103", "西湖区"),
                District("360104", "青云谱区"), District("360111", "青山湖区"),
                District("360112", "新建区"), District("360113", "红谷滩区"),
                District("360121", "南昌县"), District("360123", "安义县"),
                District("360124", "进贤县")
            )),
            City("3602", "景德镇市", listOf(
                District("360202", "昌江区"), District("360203", "珠山区"),
                District("360222", "浮梁县"), District("360281", "乐平市")
            )),
            City("3603", "萍乡市", listOf(
                District("360302", "安源区"), District("360313", "湘东区"),
                District("360321", "莲花县"), District("360322", "上栗县"),
                District("360323", "芦溪县")
            )),
            City("3604", "九江市", listOf(
                District("360402", "濂溪区"), District("360403", "浔阳区"),
                District("360404", "柴桑区"), District("360423", "武宁县"),
                District("360424", "修水县"), District("360425", "永修县"),
                District("360426", "德安县"), District("360428", "都昌县"),
                District("360429", "湖口县"), District("360430", "彭泽县"),
                District("360481", "瑞昌市"), District("360482", "共青城市"),
                District("360483", "庐山市")
            )),
            City("3605", "新余市", listOf(
                District("360502", "渝水区"), District("360521", "分宜县")
            )),
            City("3606", "鹰潭市", listOf(
                District("360602", "月湖区"), District("360603", "余江区"),
                District("360681", "贵溪市")
            )),
            City("3607", "赣州市", listOf(
                District("360702", "章贡区"), District("360703", "南康区"),
                District("360704", "赣县区"), District("360722", "信丰县"),
                District("360723", "大余县"), District("360724", "上犹县"),
                District("360725", "崇义县"), District("360726", "安远县"),
                District("360728", "定南县"), District("360729", "全南县"),
                District("360730", "宁都县"), District("360731", "于都县"),
                District("360732", "兴国县"), District("360733", "会昌县"),
                District("360734", "寻乌县"), District("360735", "石城县"),
                District("360781", "瑞金市"), District("360783", "龙南市")
            )),
            City("3608", "吉安市", listOf(
                District("360802", "吉州区"), District("360803", "青原区"),
                District("360821", "吉安县"), District("360822", "吉水县"),
                District("360823", "峡江县"), District("360824", "新干县"),
                District("360825", "永丰县"), District("360826", "泰和县"),
                District("360827", "遂川县"), District("360828", "万安县"),
                District("360829", "安福县"), District("360830", "永新县"),
                District("360881", "井冈山市")
            )),
            City("3609", "宜春市", listOf(
                District("360902", "袁州区"), District("360921", "奉新县"),
                District("360922", "万载县"), District("360923", "上高县"),
                District("360924", "宜丰县"), District("360925", "靖安县"),
                District("360926", "铜鼓县"), District("360981", "丰城市"),
                District("360982", "樟树市"), District("360983", "高安市")
            )),
            City("3610", "抚州市", listOf(
                District("361002", "临川区"), District("361003", "东乡区"),
                District("361021", "南城县"), District("361022", "黎川县"),
                District("361023", "南丰县"), District("361024", "崇仁县"),
                District("361025", "乐安县"), District("361026", "宜黄县"),
                District("361027", "金溪县"), District("361028", "资溪县"),
                District("361030", "广昌县")
            )),
            City("3611", "上饶市", listOf(
                District("361102", "信州区"), District("361103", "广丰区"),
                District("361104", "广信区"), District("361123", "玉山县"),
                District("361124", "铅山县"), District("361125", "横峰县"),
                District("361126", "弋阳县"), District("361127", "余干县"),
                District("361128", "鄱阳县"), District("361129", "万年县"),
                District("361130", "婺源县"), District("361181", "德兴市")
            ))
        )),
        // 山东省 (37)
        Province(code = "37", name = "山东省", cities = listOf(
            City("3701", "济南市", listOf(
                District("370102", "历下区"), District("370103", "市中区"),
                District("370104", "槐荫区"), District("370105", "天桥区"),
                District("370112", "历城区"), District("370113", "长清区"),
                District("370114", "章丘区"), District("370115", "济阳区"),
                District("370116", "莱芜区"), District("370117", "钢城区"),
                District("370124", "平阴县"), District("370126", "商河县")
            )),
            City("3702", "青岛市", listOf(
                District("370202", "市南区"), District("370203", "市北区"),
                District("370211", "黄岛区"), District("370212", "崂山区"),
                District("370213", "李沧区"), District("370214", "城阳区"),
                District("370215", "即墨区"), District("370281", "胶州市"),
                District("370283", "平度市"), District("370285", "莱西市")
            )),
            City("3703", "淄博市", listOf(
                District("370302", "淄川区"), District("370303", "张店区"),
                District("370304", "博山区"), District("370305", "临淄区"),
                District("370306", "周村区"), District("370321", "桓台县"),
                District("370322", "高青县"), District("370323", "沂源县")
            )),
            City("3704", "枣庄市", listOf(
                District("370402", "市中区"), District("370403", "薛城区"),
                District("370404", "峄城区"), District("370405", "台儿庄区"),
                District("370406", "山亭区"), District("370481", "滕州市")
            )),
            City("3705", "东营市", listOf(
                District("370502", "东营区"), District("370503", "河口区"),
                District("370505", "垦利区"), District("370522", "利津县"),
                District("370523", "广饶县")
            )),
            City("3706", "烟台市", listOf(
                District("370602", "芝罘区"), District("370611", "福山区"),
                District("370612", "牟平区"), District("370613", "莱山区"),
                District("370614", "蓬莱区"), District("370681", "龙口市"),
                District("370682", "莱阳市"), District("370683", "莱州市"),
                District("370685", "招远市"), District("370686", "栖霞市"),
                District("370687", "海阳市")
            )),
            City("3707", "潍坊市", listOf(
                District("370702", "潍城区"), District("370703", "寒亭区"),
                District("370704", "坊子区"), District("370705", "奎文区"),
                District("370724", "临朐县"), District("370725", "昌乐县"),
                District("370781", "青州市"), District("370782", "诸城市"),
                District("370783", "寿光市"), District("370784", "安丘市"),
                District("370785", "高密市"), District("370786", "昌邑市")
            )),
            City("3708", "济宁市", listOf(
                District("370811", "任城区"), District("370812", "兖州区"),
                District("370826", "微山县"), District("370827", "鱼台县"),
                District("370828", "金乡县"), District("370829", "嘉祥县"),
                District("370830", "汶上县"), District("370831", "泗水县"),
                District("370832", "梁山县"), District("370881", "曲阜市"),
                District("370883", "邹城市")
            )),
            City("3709", "泰安市", listOf(
                District("370902", "泰山区"), District("370911", "岱岳区"),
                District("370921", "宁阳县"), District("370923", "东平县"),
                District("370982", "新泰市"), District("370983", "肥城市")
            )),
            City("3710", "威海市", listOf(
                District("371002", "环翠区"), District("371003", "文登区"),
                District("371082", "荣成市"), District("371083", "乳山市")
            )),
            City("3711", "日照市", listOf(
                District("371102", "东港区"), District("371103", "岚山区"),
                District("371121", "五莲县"), District("371122", "莒县")
            )),
            City("3713", "临沂市", listOf(
                District("371302", "兰山区"), District("371311", "罗庄区"),
                District("371312", "河东区"), District("371321", "沂南县"),
                District("371322", "郯城县"), District("371323", "沂水县"),
                District("371324", "兰陵县"), District("371325", "费县"),
                District("371326", "平邑县"), District("371327", "莒南县"),
                District("371328", "蒙阴县"), District("371329", "临沭县")
            )),
            City("3714", "德州市", listOf(
                District("371402", "德城区"), District("371403", "陵城区"),
                District("371422", "宁津县"), District("371423", "庆云县"),
                District("371424", "临邑县"), District("371425", "齐河县"),
                District("371426", "平原县"), District("371427", "夏津县"),
                District("371428", "武城县"), District("371481", "乐陵市"),
                District("371482", "禹城市")
            )),
            City("3715", "聊城市", listOf(
                District("371502", "东昌府区"), District("371503", "茌平区"),
                District("371521", "阳谷县"), District("371522", "莘县"),
                District("371524", "东阿县"), District("371525", "冠县"),
                District("371526", "高唐县"), District("371581", "临清市")
            )),
            City("3716", "滨州市", listOf(
                District("371602", "滨城区"), District("371603", "沾化区"),
                District("371621", "惠民县"), District("371622", "阳信县"),
                District("371623", "无棣县"), District("371625", "博兴县"),
                District("371681", "邹平市")
            )),
            City("3717", "菏泽市", listOf(
                District("371702", "牡丹区"), District("371703", "定陶区"),
                District("371721", "曹县"), District("371722", "单县"),
                District("371723", "成武县"), District("371724", "巨野县"),
                District("371725", "郓城县"), District("371726", "鄄城县"),
                District("371728", "东明县")
            ))
        )),
        // 河南省 (41)
        Province(code = "41", name = "河南省", cities = listOf(
            City("4101", "郑州市", listOf(
                District("410102", "中原区"), District("410103", "二七区"),
                District("410104", "管城回族区"), District("410105", "金水区"),
                District("410106", "上街区"), District("410108", "惠济区"),
                District("410122", "中牟县"), District("410181", "巩义市"),
                District("410182", "荥阳市"), District("410183", "新密市"),
                District("410184", "新郑市"), District("410185", "登封市")
            )),
            City("4102", "开封市", listOf(
                District("410202", "龙亭区"), District("410203", "顺河回族区"),
                District("410204", "鼓楼区"), District("410205", "禹王台区"),
                District("410212", "祥符区"), District("410221", "杞县"),
                District("410222", "通许县"), District("410223", "尉氏县"),
                District("410225", "兰考县")
            )),
            City("4103", "洛阳市", listOf(
                District("410302", "老城区"), District("410303", "西工区"),
                District("410304", "瀍河回族区"), District("410305", "涧西区"),
                District("410311", "洛龙区"), District("410312", "偃师区"),
                District("410313", "孟津区"), District("410323", "新安县"),
                District("410324", "栾川县"), District("410325", "嵩县"),
                District("410326", "汝阳县"), District("410327", "宜阳县"),
                District("410328", "洛宁县"), District("410329", "伊川县")
            )),
            City("4104", "平顶山市", listOf(
                District("410402", "新华区"), District("410403", "卫东区"),
                District("410404", "石龙区"), District("410411", "湛河区"),
                District("410421", "宝丰县"), District("410422", "叶县"),
                District("410423", "鲁山县"), District("410425", "郏县"),
                District("410481", "舞钢市"), District("410482", "汝州市")
            )),
            City("4105", "安阳市", listOf(
                District("410502", "文峰区"), District("410503", "北关区"),
                District("410505", "殷都区"), District("410506", "龙安区"),
                District("410522", "安阳县"), District("410523", "汤阴县"),
                District("410526", "滑县"), District("410527", "内黄县"),
                District("410581", "林州市")
            )),
            City("4106", "鹤壁市", listOf(
                District("410602", "鹤山区"), District("410603", "山城区"),
                District("410611", "淇滨区"), District("410621", "浚县"),
                District("410622", "淇县")
            )),
            City("4107", "新乡市", listOf(
                District("410702", "红旗区"), District("410703", "卫滨区"),
                District("410704", "凤泉区"), District("410711", "牧野区"),
                District("410721", "新乡县"), District("410724", "获嘉县"),
                District("410725", "原阳县"), District("410726", "延津县"),
                District("410727", "封丘县"), District("410781", "卫辉市"),
                District("410782", "辉县市"), District("410783", "长垣市")
            )),
            City("4108", "焦作市", listOf(
                District("410802", "解放区"), District("410803", "中站区"),
                District("410804", "马村区"), District("410811", "山阳区"),
                District("410821", "修武县"), District("410822", "博爱县"),
                District("410823", "武陟县"), District("410825", "温县"),
                District("410882", "沁阳市"), District("410883", "孟州市")
            )),
            City("4109", "濮阳市", listOf(
                District("410902", "华龙区"), District("410922", "清丰县"),
                District("410923", "南乐县"), District("410926", "范县"),
                District("410927", "台前县"), District("410928", "濮阳县")
            )),
            City("4110", "许昌市", listOf(
                District("411002", "魏都区"), District("411003", "建安区"),
                District("411024", "鄢陵县"), District("411025", "襄城县"),
                District("411081", "禹州市"), District("411082", "长葛市")
            )),
            City("4111", "漯河市", listOf(
                District("411102", "源汇区"), District("411103", "郾城区"),
                District("411104", "召陵区"), District("411121", "舞阳县"),
                District("411122", "临颍县")
            )),
            City("4112", "三门峡市", listOf(
                District("411202", "湖滨区"), District("411203", "陕州区"),
                District("411221", "渑池县"), District("411224", "卢氏县"),
                District("411281", "义马市"), District("411282", "灵宝市")
            )),
            City("4113", "南阳市", listOf(
                District("411302", "宛城区"), District("411303", "卧龙区"),
                District("411321", "南召县"), District("411322", "方城县"),
                District("411323", "西峡县"), District("411324", "镇平县"),
                District("411325", "内乡县"), District("411326", "淅川县"),
                District("411327", "社旗县"), District("411328", "唐河县"),
                District("411329", "新野县"), District("411330", "桐柏县"),
                District("411381", "邓州市")
            )),
            City("4114", "商丘市", listOf(
                District("411402", "梁园区"), District("411403", "睢阳区"),
                District("411421", "民权县"), District("411422", "睢县"),
                District("411423", "宁陵县"), District("411424", "柘城县"),
                District("411425", "虞城县"), District("411426", "夏邑县"),
                District("411481", "永城市")
            )),
            City("4115", "信阳市", listOf(
                District("411502", "浉河区"), District("411503", "平桥区"),
                District("411521", "罗山县"), District("411522", "光山县"),
                District("411523", "新县"), District("411524", "商城县"),
                District("411525", "固始县"), District("411526", "潢川县"),
                District("411527", "淮滨县"), District("411528", "息县")
            )),
            City("4116", "周口市", listOf(
                District("411602", "川汇区"), District("411603", "淮阳区"),
                District("411621", "扶沟县"), District("411622", "西华县"),
                District("411623", "商水县"), District("411624", "沈丘县"),
                District("411625", "郸城县"), District("411627", "太康县"),
                District("411628", "鹿邑县"), District("411681", "项城市")
            )),
            City("4117", "驻马店市", listOf(
                District("411702", "驿城区"), District("411721", "西平县"),
                District("411722", "上蔡县"), District("411723", "平舆县"),
                District("411724", "正阳县"), District("411725", "确山县"),
                District("411726", "泌阳县"), District("411727", "汝南县"),
                District("411728", "遂平县"), District("411729", "新蔡县")
            )),
            City("4190", "省直辖县级行政区划", listOf(
                District("419001", "济源市")
            ))
        )),
        // 湖北省 (42)
        Province(code = "42", name = "湖北省", cities = listOf(
            City("4201", "武汉市", listOf(
                District("420102", "江岸区"), District("420103", "江汉区"),
                District("420104", "硚口区"), District("420105", "汉阳区"),
                District("420106", "武昌区"), District("420107", "青山区"),
                District("420111", "洪山区"), District("420112", "东西湖区"),
                District("420113", "汉南区"), District("420114", "蔡甸区"),
                District("420115", "江夏区"), District("420116", "黄陂区"),
                District("420117", "新洲区")
            )),
            City("4202", "黄石市", listOf(
                District("420202", "黄石港区"), District("420203", "西塞山区"),
                District("420204", "下陆区"), District("420205", "铁山区"),
                District("420222", "阳新县"), District("420281", "大冶市")
            )),
            City("4203", "十堰市", listOf(
                District("420302", "茅箭区"), District("420303", "张湾区"),
                District("420304", "郧阳区"), District("420322", "郧西县"),
                District("420323", "竹山县"), District("420324", "竹溪县"),
                District("420325", "房县"), District("420381", "丹江口市")
            )),
            City("4205", "宜昌市", listOf(
                District("420502", "西陵区"), District("420503", "伍家岗区"),
                District("420504", "点军区"), District("420505", "猇亭区"),
                District("420506", "夷陵区"), District("420525", "远安县"),
                District("420526", "兴山县"), District("420527", "秭归县"),
                District("420528", "长阳土家族自治县"), District("420529", "五峰土家族自治县"),
                District("420581", "宜都市"), District("420582", "当阳市"),
                District("420583", "枝江市")
            )),
            City("4206", "襄阳市", listOf(
                District("420602", "襄城区"), District("420606", "樊城区"),
                District("420607", "襄州区"), District("420624", "南漳县"),
                District("420625", "谷城县"), District("420626", "保康县"),
                District("420682", "老河口市"), District("420683", "枣阳市"),
                District("420684", "宜城市")
            )),
            City("4207", "鄂州市", listOf(
                District("420702", "梁子湖区"), District("420703", "华容区"),
                District("420704", "鄂城区")
            )),
            City("4208", "荆门市", listOf(
                District("420802", "东宝区"), District("420804", "掇刀区"),
                District("420822", "沙洋县"), District("420881", "钟祥市"),
                District("420882", "京山市")
            )),
            City("4209", "孝感市", listOf(
                District("420902", "孝南区"), District("420921", "孝昌县"),
                District("420922", "大悟县"), District("420923", "云梦县"),
                District("420981", "应城市"), District("420982", "安陆市"),
                District("420984", "汉川市")
            )),
            City("4210", "荆州市", listOf(
                District("421002", "沙市区"), District("421003", "荆州区"),
                District("421022", "公安县"), District("421023", "监利市"),
                District("421024", "江陵县"), District("421081", "石首市"),
                District("421083", "洪湖市"), District("421087", "松滋市")
            )),
            City("4211", "黄冈市", listOf(
                District("421102", "黄州区"), District("421121", "团风县"),
                District("421122", "红安县"), District("421123", "罗田县"),
                District("421124", "英山县"), District("421125", "浠水县"),
                District("421126", "蕲春县"), District("421127", "黄梅县"),
                District("421181", "麻城市"), District("421182", "武穴市")
            )),
            City("4212", "咸宁市", listOf(
                District("421202", "咸安区"), District("421221", "嘉鱼县"),
                District("421222", "通城县"), District("421223", "崇阳县"),
                District("421224", "通山县"), District("421281", "赤壁市")
            )),
            City("4213", "随州市", listOf(
                District("421303", "曾都区"), District("421304", "随县"),
                District("421381", "广水市")
            )),
            City("4228", "恩施土家族苗族自治州", listOf(
                District("422801", "恩施市"), District("422802", "利川市"),
                District("422822", "建始县"), District("422823", "巴东县"),
                District("422825", "宣恩县"), District("422826", "咸丰县"),
                District("422827", "来凤县"), District("422828", "鹤峰县")
            )),
            City("4290", "省直辖县级行政区划", listOf(
                District("429004", "仙桃市"), District("429005", "潜江市"),
                District("429006", "天门市"), District("429021", "神农架林区")
            ))
        )),
        // 湖南省 (43)
        Province(code = "43", name = "湖南省", cities = listOf(
            City("4301", "长沙市", listOf(
                District("430102", "芙蓉区"), District("430103", "天心区"),
                District("430104", "岳麓区"), District("430105", "开福区"),
                District("430111", "雨花区"), District("430112", "望城区"),
                District("430121", "长沙县"), District("430181", "浏阳市"),
                District("430182", "宁乡市")
            )),
            City("4302", "株洲市", listOf(
                District("430202", "荷塘区"), District("430203", "芦淞区"),
                District("430204", "石峰区"), District("430211", "天元区"),
                District("430212", "渌口区"), District("430223", "攸县"),
                District("430224", "茶陵县"), District("430225", "炎陵县"),
                District("430281", "醴陵市")
            )),
            City("4303", "湘潭市", listOf(
                District("430302", "雨湖区"), District("430304", "岳塘区"),
                District("430321", "湘潭县"), District("430381", "湘乡市"),
                District("430382", "韶山市")
            )),
            City("4304", "衡阳市", listOf(
                District("430405", "珠晖区"), District("430406", "雁峰区"),
                District("430407", "石鼓区"), District("430408", "蒸湘区"),
                District("430412", "南岳区"), District("430421", "衡阳县"),
                District("430422", "衡南县"), District("430423", "衡山县"),
                District("430424", "衡东县"), District("430426", "祁东县"),
                District("430481", "耒阳市"), District("430482", "常宁市")
            )),
            City("4305", "邵阳市", listOf(
                District("430502", "双清区"), District("430503", "大祥区"),
                District("430511", "北塔区"), District("430522", "新邵县"),
                District("430523", "邵阳县"), District("430524", "隆回县"),
                District("430525", "洞口县"), District("430527", "绥宁县"),
                District("430528", "新宁县"), District("430529", "城步苗族自治县"),
                District("430581", "武冈市"), District("430582", "邵东市")
            )),
            City("4306", "岳阳市", listOf(
                District("430602", "岳阳楼区"), District("430603", "云溪区"),
                District("430611", "君山区"), District("430621", "岳阳县"),
                District("430623", "华容县"), District("430624", "湘阴县"),
                District("430626", "平江县"), District("430681", "汨罗市"),
                District("430682", "临湘市")
            )),
            City("4307", "常德市", listOf(
                District("430702", "武陵区"), District("430703", "鼎城区"),
                District("430721", "安乡县"), District("430722", "汉寿县"),
                District("430723", "澧县"), District("430724", "临澧县"),
                District("430725", "桃源县"), District("430726", "石门县"),
                District("430781", "津市市")
            )),
            City("4308", "张家界市", listOf(
                District("430802", "永定区"), District("430811", "武陵源区"),
                District("430821", "慈利县"), District("430822", "桑植县")
            )),
            City("4309", "益阳市", listOf(
                District("430902", "资阳区"), District("430903", "赫山区"),
                District("430921", "南县"), District("430922", "桃江县"),
                District("430923", "安化县"), District("430981", "沅江市")
            )),
            City("4310", "郴州市", listOf(
                District("431002", "北湖区"), District("431003", "苏仙区"),
                District("431021", "桂阳县"), District("431022", "宜章县"),
                District("431023", "永兴县"), District("431024", "嘉禾县"),
                District("431025", "临武县"), District("431026", "汝城县"),
                District("431027", "桂东县"), District("431028", "安仁县"),
                District("431081", "资兴市")
            )),
            City("4311", "永州市", listOf(
                District("431102", "零陵区"), District("431103", "冷水滩区"),
                District("431122", "东安县"), District("431123", "双牌县"),
                District("431124", "道县"), District("431125", "江永县"),
                District("431126", "宁远县"), District("431127", "蓝山县"),
                District("431128", "新田县"), District("431129", "江华瑶族自治县"),
                District("431181", "祁阳市")
            )),
            City("4312", "怀化市", listOf(
                District("431202", "鹤城区"), District("431221", "中方县"),
                District("431222", "沅陵县"), District("431223", "辰溪县"),
                District("431224", "溆浦县"), District("431225", "会同县"),
                District("431226", "麻阳苗族自治县"), District("431227", "新晃侗族自治县"),
                District("431228", "芷江侗族自治县"), District("431229", "靖州苗族侗族自治县"),
                District("431230", "通道侗族自治县"), District("431281", "洪江市")
            )),
            City("4313", "娄底市", listOf(
                District("431302", "娄星区"), District("431321", "双峰县"),
                District("431322", "新化县"), District("431381", "冷水江市"),
                District("431382", "涟源市")
            )),
            City("4331", "湘西土家族苗族自治州", listOf(
                District("433101", "吉首市"), District("433122", "泸溪县"),
                District("433123", "凤凰县"), District("433124", "花垣县"),
                District("433125", "保靖县"), District("433126", "古丈县"),
                District("433127", "永顺县"), District("433130", "龙山县")
            ))
        )),
        // 广东省 (44)
        Province(code = "44", name = "广东省", cities = listOf(
            City("4401", "广州市", listOf(
                District("440103", "荔湾区"), District("440104", "越秀区"),
                District("440105", "海珠区"), District("440106", "天河区"),
                District("440111", "白云区"), District("440112", "黄埔区"),
                District("440113", "番禺区"), District("440114", "花都区"),
                District("440115", "南沙区"), District("440117", "从化区"),
                District("440118", "增城区")
            )),
            City("4402", "韶关市", listOf(
                District("440203", "武江区"), District("440204", "浈江区"),
                District("440205", "曲江区"), District("440222", "始兴县"),
                District("440224", "仁化县"), District("440229", "翁源县"),
                District("440232", "乳源瑶族自治县"), District("440233", "新丰县"),
                District("440281", "乐昌市"), District("440282", "南雄市")
            )),
            City("4403", "深圳市", listOf(
                District("440303", "罗湖区"), District("440304", "福田区"),
                District("440305", "南山区"), District("440306", "宝安区"),
                District("440307", "龙岗区"), District("440308", "盐田区"),
                District("440309", "龙华区"), District("440310", "坪山区"),
                District("440311", "光明区"), District("440312", "大鹏新区")
            )),
            City("4404", "珠海市", listOf(
                District("440402", "香洲区"), District("440403", "斗门区"),
                District("440404", "金湾区")
            )),
            City("4405", "汕头市", listOf(
                District("440507", "龙湖区"), District("440511", "金平区"),
                District("440512", "濠江区"), District("440513", "潮阳区"),
                District("440514", "潮南区"), District("440515", "澄海区"),
                District("440523", "南澳县")
            )),
            City("4406", "佛山市", listOf(
                District("440604", "禅城区"), District("440605", "南海区"),
                District("440606", "顺德区"), District("440607", "三水区"),
                District("440608", "高明区")
            )),
            City("4407", "江门市", listOf(
                District("440703", "蓬江区"), District("440704", "江海区"),
                District("440705", "新会区"), District("440781", "台山市"),
                District("440783", "开平市"), District("440784", "鹤山市"),
                District("440785", "恩平市")
            )),
            City("4408", "湛江市", listOf(
                District("440802", "赤坎区"), District("440803", "霞山区"),
                District("440804", "坡头区"), District("440811", "麻章区"),
                District("440823", "遂溪县"), District("440825", "徐闻县"),
                District("440881", "廉江市"), District("440882", "雷州市"),
                District("440883", "吴川市")
            )),
            City("4409", "茂名市", listOf(
                District("440902", "茂南区"), District("440904", "电白区"),
                District("440981", "高州市"), District("440982", "化州市"),
                District("440983", "信宜市")
            )),
            City("4412", "肇庆市", listOf(
                District("441202", "端州区"), District("441203", "鼎湖区"),
                District("441204", "高要区"), District("441223", "广宁县"),
                District("441224", "怀集县"), District("441225", "封开县"),
                District("441226", "德庆县"), District("441284", "四会市")
            )),
            City("4413", "惠州市", listOf(
                District("441302", "惠城区"), District("441303", "惠阳区"),
                District("441322", "博罗县"), District("441323", "惠东县"),
                District("441324", "龙门县")
            )),
            City("4414", "梅州市", listOf(
                District("441402", "梅江区"), District("441403", "梅县区"),
                District("441422", "大埔县"), District("441423", "丰顺县"),
                District("441424", "五华县"), District("441426", "平远县"),
                District("441427", "蕉岭县"), District("441481", "兴宁市")
            )),
            City("4415", "汕尾市", listOf(
                District("441502", "城区"), District("441521", "海丰县"),
                District("441523", "陆河县"), District("441581", "陆丰市")
            )),
            City("4416", "河源市", listOf(
                District("441602", "源城区"), District("441621", "紫金县"),
                District("441622", "龙川县"), District("441623", "连平县"),
                District("441624", "和平县"), District("441625", "东源县")
            )),
            City("4417", "阳江市", listOf(
                District("441702", "江城区"), District("441704", "阳东区"),
                District("441721", "阳西县"), District("441781", "阳春市")
            )),
            City("4418", "清远市", listOf(
                District("441802", "清城区"), District("441803", "清新区"),
                District("441821", "佛冈县"), District("441823", "阳山县"),
                District("441825", "连山壮族瑶族自治县"), District("441826", "连南瑶族自治县"),
                District("441881", "英德市"), District("441882", "连州市")
            )),
            City("4419", "东莞市", listOf(
                District("441900", "东莞市")
            )),
            City("4420", "中山市", listOf(
                District("442000", "中山市")
            )),
            City("4451", "潮州市", listOf(
                District("445102", "湘桥区"), District("445103", "潮安区"),
                District("445122", "饶平县")
            )),
            City("4452", "揭阳市", listOf(
                District("445202", "榕城区"), District("445203", "揭东区"),
                District("445222", "揭西县"), District("445224", "惠来县"),
                District("445281", "普宁市")
            )),
            City("4453", "云浮市", listOf(
                District("445302", "云城区"), District("445303", "云安区"),
                District("445321", "新兴县"), District("445322", "郁南县"),
                District("445381", "罗定市")
            ))
        )),
        // 广西壮族自治区 (45)
        Province(code = "45", name = "广西壮族自治区", cities = listOf(
            City("4501", "南宁市", listOf(
                District("450102", "兴宁区"), District("450103", "青秀区"),
                District("450105", "江南区"), District("450107", "西乡塘区"),
                District("450108", "良庆区"), District("450109", "邕宁区"),
                District("450110", "武鸣区"), District("450123", "隆安县"),
                District("450124", "马山县"), District("450125", "上林县"),
                District("450126", "宾阳县"), District("450127", "横州市")
            )),
            City("4502", "柳州市", listOf(
                District("450202", "城中区"), District("450203", "鱼峰区"),
                District("450204", "柳南区"), District("450205", "柳北区"),
                District("450206", "柳江区"), District("450222", "柳城县"),
                District("450223", "鹿寨县"), District("450224", "融安县"),
                District("450225", "融水苗族自治县"), District("450226", "三江侗族自治县")
            )),
            City("4503", "桂林市", listOf(
                District("450302", "秀峰区"), District("450303", "叠彩区"),
                District("450304", "象山区"), District("450305", "七星区"),
                District("450311", "雁山区"), District("450312", "临桂区"),
                District("450321", "阳朔县"), District("450323", "灵川县"),
                District("450324", "全州县"), District("450325", "兴安县"),
                District("450326", "永福县"), District("450327", "灌阳县"),
                District("450328", "龙胜各族自治县"), District("450329", "资源县"),
                District("450330", "平乐县"), District("450332", "恭城瑶族自治县"),
                District("450381", "荔浦市")
            )),
            City("4504", "梧州市", listOf(
                District("450403", "万秀区"), District("450405", "长洲区"),
                District("450406", "龙圩区"), District("450421", "苍梧县"),
                District("450422", "藤县"), District("450423", "蒙山县"),
                District("450481", "岑溪市")
            )),
            City("4505", "北海市", listOf(
                District("450502", "海城区"), District("450503", "银海区"),
                District("450512", "铁山港区"), District("450521", "合浦县")
            )),
            City("4506", "防城港市", listOf(
                District("450602", "港口区"), District("450603", "防城区"),
                District("450621", "上思县"), District("450681", "东兴市")
            )),
            City("4507", "钦州市", listOf(
                District("450702", "钦南区"), District("450703", "钦北区"),
                District("450721", "灵山县"), District("450722", "浦北县")
            )),
            City("4508", "贵港市", listOf(
                District("450802", "港北区"), District("450803", "港南区"),
                District("450804", "覃塘区"), District("450821", "平南县"),
                District("450881", "桂平市")
            )),
            City("4509", "玉林市", listOf(
                District("450902", "玉州区"), District("450903", "福绵区"),
                District("450921", "容县"), District("450922", "陆川县"),
                District("450923", "博白县"), District("450924", "兴业县"),
                District("450981", "北流市")
            )),
            City("4510", "百色市", listOf(
                District("451002", "右江区"), District("451003", "田阳区"),
                District("451022", "田东县"), District("451024", "德保县"),
                District("451026", "那坡县"), District("451027", "凌云县"),
                District("451028", "乐业县"), District("451029", "田林县"),
                District("451030", "西林县"), District("451031", "隆林各族自治县"),
                District("451081", "靖西市"), District("451082", "平果市")
            )),
            City("4511", "贺州市", listOf(
                District("451102", "八步区"), District("451103", "平桂区"),
                District("451121", "昭平县"), District("451122", "钟山县"),
                District("451123", "富川瑶族自治县")
            )),
            City("4512", "河池市", listOf(
                District("451202", "金城江区"), District("451203", "宜州区"),
                District("451221", "南丹县"), District("451222", "天峨县"),
                District("451223", "凤山县"), District("451224", "东兰县"),
                District("451225", "罗城仫佬族自治县"), District("451226", "环江毛南族自治县"),
                District("451227", "巴马瑶族自治县"), District("451228", "都安瑶族自治县"),
                District("451229", "大化瑶族自治县")
            )),
            City("4513", "来宾市", listOf(
                District("451302", "兴宾区"), District("451321", "忻城县"),
                District("451322", "象州县"), District("451323", "武宣县"),
                District("451324", "金秀瑶族自治县"), District("451381", "合山市")
            )),
            City("4514", "崇左市", listOf(
                District("451402", "江州区"), District("451421", "扶绥县"),
                District("451422", "宁明县"), District("451423", "龙州县"),
                District("451424", "大新县"), District("451425", "天等县"),
                District("451481", "凭祥市")
            ))
        )),
        // 海南省 (46)
        Province(code = "46", name = "海南省", cities = listOf(
            City("4601", "海口市", listOf(
                District("460105", "秀英区"), District("460106", "龙华区"),
                District("460107", "琼山区"), District("460108", "美兰区")
            )),
            City("4602", "三亚市", listOf(
                District("460202", "海棠区"), District("460203", "吉阳区"),
                District("460204", "天涯区"), District("460205", "崖州区")
            )),
            City("4603", "三沙市", listOf(
                District("460321", "西沙群岛"), District("460322", "南沙群岛"),
                District("460323", "中沙群岛的岛礁及其海域")
            )),
            City("4604", "儋州市", listOf(
                District("460400", "儋州市")
            )),
            City("4690", "省直辖县级行政区划", listOf(
                District("469001", "五指山市"), District("469002", "琼海市"),
                District("469005", "文昌市"), District("469006", "万宁市"),
                District("469007", "东方市"), District("469021", "定安县"),
                District("469022", "屯昌县"), District("469023", "澄迈县"),
                District("469024", "临高县"), District("469025", "白沙黎族自治县"),
                District("469026", "昌江黎族自治县"), District("469027", "乐东黎族自治县"),
                District("469028", "陵水黎族自治县"), District("469029", "保亭黎族苗族自治县"),
                District("469030", "琼中黎族苗族自治县")
            ))
        )),
        // 重庆市 (50)
        Province(code = "50", name = "重庆市", cities = listOf(
            City(code = "5001", name = "重庆市", districts = listOf(
                District("500101", "万州区"), District("500102", "涪陵区"),
                District("500103", "渝中区"), District("500104", "大渡口区"),
                District("500105", "江北区"), District("500106", "沙坪坝区"),
                District("500107", "九龙坡区"), District("500108", "南岸区"),
                District("500109", "北碚区"), District("500110", "綦江区"),
                District("500111", "大足区"), District("500112", "渝北区"),
                District("500113", "巴南区"), District("500114", "黔江区"),
                District("500115", "长寿区"), District("500116", "江津区"),
                District("500117", "合川区"), District("500118", "永川区"),
                District("500119", "南川区"), District("500120", "璧山区"),
                District("500151", "铜梁区"), District("500152", "潼南区"),
                District("500153", "荣昌区"), District("500154", "开州区"),
                District("500155", "梁平区"), District("500156", "武隆区")
            ))
        )),
        // 四川省 (51) - 21个市州
        Province(code = "51", name = "四川省", cities = listOf(
            // 成都市 - 12个区、3个县、5个县级市
            City("5101", "成都市", listOf(
                District("510104", "锦江区"), District("510105", "青羊区"),
                District("510106", "金牛区"), District("510107", "武侯区"),
                District("510108", "成华区"), District("510112", "龙泉驿区"),
                District("510113", "青白江区"), District("510114", "新都区"),
                District("510115", "温江区"), District("510116", "双流区"),
                District("510117", "郫都区"), District("510118", "新津区"),
                District("510121", "金堂县"), District("510129", "大邑县"),
                District("510131", "蒲江县"), District("510181", "简阳市"),
                District("510182", "都江堰市"), District("510183", "彭州市"),
                District("510184", "邛崃市"), District("510185", "崇州市")
            )),
            // 自贡市 - 4个区、2个县
            City("5103", "自贡市", listOf(
                District("510302", "自流井区"), District("510303", "贡井区"),
                District("510304", "大安区"), District("510311", "沿滩区"),
                District("510321", "荣县"), District("510322", "富顺县")
            )),
            // 攀枝花市 - 3个区、2个县
            City("5104", "攀枝花市", listOf(
                District("510402", "东区"), District("510403", "西区"),
                District("510411", "仁和区"), District("510421", "米易县"),
                District("510422", "盐边县")
            )),
            // 泸州市 - 3个区、4个县
            City("5105", "泸州市", listOf(
                District("510502", "江阳区"), District("510503", "纳溪区"),
                District("510504", "龙马潭区"), District("510521", "泸县"),
                District("510522", "合江县"), District("510524", "叙永县"),
                District("510525", "古蔺县")
            )),
            // 德阳市 - 2个区、1个县、3个县级市
            City("5106", "德阳市", listOf(
                District("510603", "旌阳区"), District("510604", "罗江区"),
                District("510623", "中江县"), District("510681", "广汉市"),
                District("510682", "什邡市"), District("510683", "绵竹市")
            )),
            // 绵阳市 - 3个区、4个县、1个县级市
            City("5107", "绵阳市", listOf(
                District("510703", "涪城区"), District("510704", "游仙区"),
                District("510705", "安州区"), District("510722", "三台县"),
                District("510723", "盐亭县"), District("510725", "梓潼县"),
                District("510726", "北川县"), District("510727", "平武县"),
                District("510781", "江油市")
            )),
            // 广元市 - 3个区、4个县
            City("5108", "广元市", listOf(
                District("510802", "利州区"), District("510811", "昭化区"),
                District("510812", "朝天区"), District("510821", "旺苍县"),
                District("510822", "青川县"), District("510823", "剑阁县"),
                District("510824", "苍溪县")
            )),
            // 遂宁市 - 2个区、2个县、1个县级市
            City("5109", "遂宁市", listOf(
                District("510903", "船山区"), District("510904", "安居区"),
                District("510921", "蓬溪县"), District("510923", "大英县"),
                District("510981", "射洪市")
            )),
            // 内江市 - 2个区、2个县、1个县级市
            City("5110", "内江市", listOf(
                District("511002", "市中区"), District("511011", "东兴区"),
                District("511024", "威远县"), District("511025", "资中县"),
                District("511083", "隆昌市")
            )),
            // 乐山市 - 4个区、4个县、1个县级市
            City("5111", "乐山市", listOf(
                District("511102", "市中区"), District("511111", "沙湾区"),
                District("511112", "五通桥区"), District("511113", "金口河区"),
                District("511123", "犍为县"), District("511124", "井研县"),
                District("511126", "夹江县"), District("511129", "沐川县"),
                District("511132", "峨边县"), District("511133", "马边县"),
                District("511181", "峨眉山市")
            )),
            // 南充市 - 3个区、5个县、1个县级市
            City("5113", "南充市", listOf(
                District("511302", "顺庆区"), District("511303", "高坪区"),
                District("511304", "嘉陵区"), District("511321", "南部县"),
                District("511322", "营山县"), District("511323", "蓬安县"),
                District("511324", "仪陇县"), District("511325", "西充县"),
                District("511381", "阆中市")
            )),
            // 眉山市 - 2个区、4个县
            City("5114", "眉山市", listOf(
                District("511402", "东坡区"), District("511403", "彭山区"),
                District("511421", "仁寿县"), District("511423", "洪雅县"),
                District("511424", "丹棱县"), District("511425", "青神县")
            )),
            // 宜宾市 - 3个区、7个县
            City("5115", "宜宾市", listOf(
                District("511502", "翠屏区"), District("511503", "南溪区"),
                District("511504", "叙州区"), District("511523", "江安县"),
                District("511524", "长宁县"), District("511525", "高县"),
                District("511526", "珙县"), District("511527", "筠连县"),
                District("511528", "兴文县"), District("511529", "屏山县")
            )),
            // 广安市 - 2个区、3个县、1个县级市
            City("5116", "广安市", listOf(
                District("511602", "广安区"), District("511603", "前锋区"),
                District("511621", "岳池县"), District("511622", "武胜县"),
                District("511623", "邻水县"), District("511681", "华蓥市")
            )),
            // 达州市 - 2个区、4个县、1个县级市
            City("5117", "达州市", listOf(
                District("511702", "通川区"), District("511703", "达川区"),
                District("511722", "宣汉县"), District("511723", "开江县"),
                District("511724", "大竹县"), District("511725", "渠县"),
                District("511781", "万源市")
            )),
            // 雅安市 - 2个区、6个县
            City("5118", "雅安市", listOf(
                District("511802", "雨城区"), District("511803", "名山区"),
                District("511822", "荥经县"), District("511823", "汉源县"),
                District("511824", "石棉县"), District("511825", "天全县"),
                District("511826", "芦山县"), District("511827", "宝兴县")
            )),
            // 巴中市 - 2个区、3个县
            City("5119", "巴中市", listOf(
                District("511902", "巴州区"), District("511903", "恩阳区"),
                District("511921", "通江县"), District("511922", "南江县"),
                District("511923", "平昌县")
            )),
            // 资阳市 - 1个区、2个县
            City("5120", "资阳市", listOf(
                District("512002", "雁江区"), District("512021", "安岳县"),
                District("512022", "乐至县")
            )),
            // 阿坝藏族羌族自治州 - 1个县级市、12个县
            City("5132", "阿坝藏族羌族自治州", listOf(
                District("513201", "马尔康市"), District("513221", "汶川县"),
                District("513222", "理县"), District("513223", "茂县"),
                District("513224", "松潘县"), District("513225", "九寨沟县"),
                District("513226", "金川县"), District("513227", "小金县"),
                District("513228", "黑水县"), District("513230", "壤塘县"),
                District("513231", "阿坝县"), District("513232", "若尔盖县"),
                District("513233", "红原县")
            )),
            // 甘孜藏族自治州 - 1个县级市、17个县
            City("5133", "甘孜藏族自治州", listOf(
                District("513301", "康定市"), District("513322", "泸定县"),
                District("513323", "丹巴县"), District("513324", "九龙县"),
                District("513325", "雅江县"), District("513326", "道孚县"),
                District("513327", "炉霍县"), District("513328", "甘孜县"),
                District("513329", "新龙县"), District("513330", "德格县"),
                District("513331", "白玉县"), District("513332", "石渠县"),
                District("513333", "色达县"), District("513334", "理塘县"),
                District("513335", "巴塘县"), District("513336", "乡城县"),
                District("513337", "稻城县"), District("513338", "得荣县")
            )),
            // 凉山彝族自治州 - 2个县级市、14个县、1个自治县
            City("5134", "凉山彝族自治州", listOf(
                District("513401", "西昌市"), District("513402", "会理市"),
                District("513422", "木里县"), District("513423", "盐源县"),
                District("513424", "德昌县"), District("513425", "会东县"),
                District("513426", "宁南县"), District("513427", "普格县"),
                District("513428", "布拖县"), District("513429", "金阳县"),
                District("513430", "昭觉县"), District("513431", "喜德县"),
                District("513432", "冕宁县"), District("513433", "越西县"),
                District("513434", "甘洛县"), District("513435", "美姑县"),
                District("513436", "雷波县")
            ))
        )),
        // 贵州省 (52) - 9个市州
        Province(code = "52", name = "贵州省", cities = listOf(
            // 贵阳市 - 6个区、3个县、1个县级市
            City("5201", "贵阳市", listOf(
                District("520102", "南明区"), District("520103", "云岩区"),
                District("520111", "花溪区"), District("520112", "乌当区"),
                District("520113", "白云区"), District("520115", "观山湖区"),
                District("520121", "开阳县"), District("520122", "息烽县"),
                District("520123", "修文县"), District("520181", "清镇市")
            )),
            // 六盘水市 - 2个区、1个县、1个县级市
            City("5202", "六盘水市", listOf(
                District("520201", "钟山区"), District("520203", "六枝特区"),
                District("520221", "水城县"), District("520281", "盘州市")
            )),
            // 遵义市 - 3个区、7个县、2个县级市、2个自治县
            City("5203", "遵义市", listOf(
                District("520302", "红花岗区"), District("520303", "汇川区"),
                District("520304", "播州区"), District("520322", "桐梓县"),
                District("520323", "绥阳县"), District("520324", "正安县"),
                District("520325", "道真县"), District("520326", "务川县"),
                District("520327", "凤冈县"), District("520328", "湄潭县"),
                District("520329", "余庆县"), District("520330", "习水县"),
                District("520381", "赤水市"), District("520382", "仁怀市")
            )),
            // 安顺市 - 2个区、1个县、3个自治县
            City("5204", "安顺市", listOf(
                District("520402", "西秀区"), District("520403", "平坝区"),
                District("520422", "普定县"), District("520423", "镇宁县"),
                District("520424", "关岭县"), District("520425", "紫云县")
            )),
            // 毕节市 - 1个区、6个县、1个县级市
            City("5205", "毕节市", listOf(
                District("520502", "七星关区"), District("520521", "大方县"),
                District("520523", "金沙县"), District("520524", "织金县"),
                District("520525", "纳雍县"), District("520526", "威宁县"),
                District("520527", "赫章县"), District("520581", "黔西市")
            )),
            // 铜仁市 - 2个区、4个县、4个自治县
            City("5206", "铜仁市", listOf(
                District("520602", "碧江区"), District("520603", "万山区"),
                District("520621", "江口县"), District("520622", "玉屏县"),
                District("520623", "石阡县"), District("520624", "思南县"),
                District("520625", "印江县"), District("520626", "德江县"),
                District("520627", "沿河县"), District("520628", "松桃县")
            )),
            // 黔西南布依族苗族自治州 - 2个县级市、6个县
            City("5223", "黔西南布依族苗族自治州", listOf(
                District("522301", "兴义市"), District("522302", "兴仁市"),
                District("522323", "普安县"), District("522324", "晴隆县"),
                District("522325", "贞丰县"), District("522326", "望谟县"),
                District("522327", "册亨县"), District("522328", "安龙县")
            )),
            // 黔东南苗族侗族自治州 - 1个县级市、15个县
            City("5226", "黔东南苗族侗族自治州", listOf(
                District("522601", "凯里市"), District("522622", "黄平县"),
                District("522623", "施秉县"), District("522624", "三穗县"),
                District("522625", "镇远县"), District("522626", "岑巩县"),
                District("522627", "天柱县"), District("522628", "锦屏县"),
                District("522629", "剑河县"), District("522630", "台江县"),
                District("522631", "黎平县"), District("522632", "榕江县"),
                District("522633", "从江县"), District("522634", "雷山县"),
                District("522635", "麻江县"), District("522636", "丹寨县")
            )),
            // 黔南布依族苗族自治州 - 2个县级市、9个县、1个自治县
            City("5227", "黔南布依族苗族自治州", listOf(
                District("522701", "都匀市"), District("522702", "福泉市"),
                District("522722", "荔波县"), District("522723", "贵定县"),
                District("522725", "瓮安县"), District("522726", "独山县"),
                District("522727", "平塘县"), District("522728", "罗甸县"),
                District("522729", "长顺县"), District("522730", "龙里县"),
                District("522731", "惠水县"), District("522732", "三都县")
            ))
        )),
        // 云南省 (53) - 16个市州
        Province(code = "53", name = "云南省", cities = listOf(
            City("5301", "昆明市", listOf(
                District("530102", "五华区"), District("530103", "盘龙区"),
                District("530111", "官渡区"), District("530112", "西山区"),
                District("530113", "东川区"), District("530114", "呈贡区"),
                District("530115", "晋宁区"), District("530124", "富民县"),
                District("530125", "宜良县"), District("530126", "石林县"),
                District("530127", "嵩明县"), District("530128", "禄劝县"),
                District("530129", "寻甸县"), District("530181", "安宁市")
            )),
            City("5303", "曲靖市", listOf(
                District("530302", "麒麟区"), District("530303", "沾益区"),
                District("530304", "马龙区"), District("530322", "陆良县"),
                District("530323", "师宗县"), District("530324", "罗平县"),
                District("530325", "富源县"), District("530326", "会泽县"),
                District("530381", "宣威市")
            )),
            City("5304", "玉溪市", listOf(
                District("530402", "红塔区"), District("530403", "江川区"),
                District("530423", "通海县"), District("530424", "华宁县"),
                District("530425", "易门县"), District("530426", "峨山县"),
                District("530427", "新平县"), District("530428", "元江县"),
                District("530481", "澄江市")
            )),
            City("5305", "保山市", listOf(
                District("530502", "隆阳区"), District("530521", "施甸县"),
                District("530523", "龙陵县"), District("530524", "昌宁县"),
                District("530581", "腾冲市")
            )),
            City("5306", "昭通市", listOf(
                District("530602", "昭阳区"), District("530621", "鲁甸县"),
                District("530622", "巧家县"), District("530623", "盐津县"),
                District("530624", "大关县"), District("530625", "永善县"),
                District("530626", "绥江县"), District("530627", "镇雄县"),
                District("530628", "彝良县"), District("530629", "威信县"),
                District("530681", "水富市")
            )),
            City("5307", "丽江市", listOf(
                District("530702", "古城区"), District("530721", "玉龙县"),
                District("530722", "永胜县"), District("530723", "华坪县"),
                District("530724", "宁蒗县")
            )),
            City("5308", "普洱市", listOf(
                District("530802", "思茅区"), District("530821", "宁洱县"),
                District("530822", "墨江县"), District("530823", "景东县"),
                District("530824", "景谷县"), District("530825", "镇沅县"),
                District("530826", "江城县"), District("530827", "孟连县"),
                District("530828", "澜沧县"), District("530829", "西盟县")
            )),
            City("5309", "临沧市", listOf(
                District("530902", "临翔区"), District("530921", "凤庆县"),
                District("530922", "云县"), District("530923", "永德县"),
                District("530924", "镇康县"), District("530925", "双江县"),
                District("530926", "耿马县"), District("530927", "沧源县")
            )),
            City("5323", "楚雄彝族自治州", listOf(
                District("532301", "楚雄市"), District("532302", "禄丰市"),
                District("532322", "双柏县"), District("532323", "牟定县"),
                District("532324", "南华县"), District("532325", "姚安县"),
                District("532326", "大姚县"), District("532327", "永仁县"),
                District("532328", "元谋县"), District("532329", "武定县")
            )),
            City("5325", "红河哈尼族彝族自治州", listOf(
                District("532501", "个旧市"), District("532502", "开远市"),
                District("532503", "蒙自市"), District("532504", "弥勒市"),
                District("532523", "屏边县"), District("532524", "建水县"),
                District("532525", "石屏县"), District("532527", "泸西县"),
                District("532528", "元阳县"), District("532529", "红河县"),
                District("532530", "金平县"), District("532531", "绿春县"),
                District("532532", "河口县")
            )),
            City("5326", "文山壮族苗族自治州", listOf(
                District("532601", "文山市"), District("532622", "砚山县"),
                District("532623", "西畴县"), District("532624", "麻栗坡县"),
                District("532625", "马关县"), District("532626", "丘北县"),
                District("532627", "广南县"), District("532628", "富宁县")
            )),
            City("5328", "西双版纳傣族自治州", listOf(
                District("532801", "景洪市"), District("532822", "勐海县"),
                District("532823", "勐腊县")
            )),
            City("5329", "大理白族自治州", listOf(
                District("532901", "大理市"), District("532922", "漾濞县"),
                District("532923", "祥云县"), District("532924", "宾川县"),
                District("532925", "弥渡县"), District("532926", "南涧县"),
                District("532927", "巍山县"), District("532928", "永平县"),
                District("532929", "云龙县"), District("532930", "洱源县"),
                District("532931", "剑川县"), District("532932", "鹤庆县")
            )),
            City("5331", "德宏傣族景颇族自治州", listOf(
                District("533102", "瑞丽市"), District("533103", "芒市"),
                District("533122", "梁河县"), District("533123", "盈江县"),
                District("533124", "陇川县")
            )),
            City("5333", "怒江傈僳族自治州", listOf(
                District("533301", "泸水市"), District("533323", "福贡县"),
                District("533324", "贡山县"), District("533325", "兰坪县")
            )),
            City("5334", "迪庆藏族自治州", listOf(
                District("533401", "香格里拉市"), District("533422", "德钦县"),
                District("533423", "维西县")
            ))
        )),
        // 西藏自治区 (54) - 7个地市
        Province(code = "54", name = "西藏自治区", cities = listOf(
            // 拉萨市 - 3个区、5个县
            City("5401", "拉萨市", listOf(
                District("540102", "城关区"), District("540103", "堆龙德庆区"),
                District("540104", "达孜区"), District("540121", "林周县"),
                District("540122", "当雄县"), District("540123", "尼木县"),
                District("540124", "曲水县"), District("540127", "墨竹工卡县")
            )),
            // 日喀则市 - 1个区、17个县
            City("5402", "日喀则市", listOf(
                District("540202", "桑珠孜区"), District("540221", "南木林县"),
                District("540222", "江孜县"), District("540223", "定日县"),
                District("540224", "萨迦县"), District("540225", "拉孜县"),
                District("540226", "昂仁县"), District("540227", "谢通门县"),
                District("540228", "白朗县"), District("540229", "仁布县"),
                District("540230", "康马县"), District("540231", "定结县"),
                District("540232", "仲巴县"), District("540233", "亚东县"),
                District("540234", "吉隆县"), District("540235", "聂拉木县"),
                District("540236", "萨嘎县"), District("540237", "岗巴县")
            )),
            // 昌都市 - 1个区、10个县
            City("5403", "昌都市", listOf(
                District("540302", "卡若区"), District("540321", "江达县"),
                District("540322", "贡觉县"), District("540323", "类乌齐县"),
                District("540324", "丁青县"), District("540325", "察雅县"),
                District("540326", "八宿县"), District("540327", "左贡县"),
                District("540328", "芒康县"), District("540329", "洛隆县"),
                District("540330", "边坝县")
            )),
            // 林芝市 - 1个区、5个县、1个自治县
            City("5404", "林芝市", listOf(
                District("540402", "巴宜区"), District("540421", "工布江达县"),
                District("540422", "米林县"), District("540423", "墨脱县"),
                District("540424", "波密县"), District("540425", "察隅县"),
                District("540426", "朗县")
            )),
            // 山南市 - 1个区、10个县、1个自治县
            City("5405", "山南市", listOf(
                District("540502", "乃东区"), District("540521", "扎囊县"),
                District("540522", "贡嘎县"), District("540523", "桑日县"),
                District("540524", "琼结县"), District("540525", "曲松县"),
                District("540526", "措美县"), District("540527", "洛扎县"),
                District("540528", "加查县"), District("540529", "隆子县"),
                District("540530", "错那县"), District("540531", "浪卡子县")
            )),
            // 那曲市 - 1个区、10个县
            City("5406", "那曲市", listOf(
                District("540602", "色尼区"), District("540621", "嘉黎县"),
                District("540622", "比如县"), District("540623", "聂荣县"),
                District("540624", "安多县"), District("540625", "申扎县"),
                District("540626", "索县"), District("540627", "班戈县"),
                District("540628", "巴青县"), District("540629", "尼玛县"),
                District("540630", "双湖县")
            )),
            // 阿里地区 - 7个县
            City("5425", "阿里地区", listOf(
                District("542521", "普兰县"), District("542522", "札达县"),
                District("542523", "噶尔县"), District("542524", "日土县"),
                District("542525", "革吉县"), District("542526", "改则县"),
                District("542527", "措勤县")
            ))
        )),
        // 陕西省 (61) - 10个地级市
        Province(code = "61", name = "陕西省", cities = listOf(
            // 西安市 - 11个区、2个县
            City("6101", "西安市", listOf(
                District("610102", "新城区"), District("610103", "碑林区"),
                District("610104", "莲湖区"), District("610111", "灞桥区"),
                District("610112", "未央区"), District("610113", "雁塔区"),
                District("610114", "阎良区"), District("610115", "临潼区"),
                District("610116", "长安区"), District("610117", "高陵区"),
                District("610118", "鄠邑区"), District("610122", "蓝田县"),
                District("610124", "周至县")
            )),
            // 铜川市 - 3个区、1个县
            City("6102", "铜川市", listOf(
                District("610202", "王益区"), District("610203", "印台区"),
                District("610204", "耀州区"), District("610222", "宜君县")
            )),
            // 宝鸡市 - 4个区、8个县
            City("6103", "宝鸡市", listOf(
                District("610302", "渭滨区"), District("610303", "金台区"),
                District("610304", "陈仓区"), District("610305", "凤翔区"),
                District("610323", "岐山县"), District("610324", "扶风县"),
                District("610326", "眉县"), District("610327", "陇县"),
                District("610328", "千阳县"), District("610329", "麟游县"),
                District("610330", "凤县"), District("610331", "太白县")
            )),
            // 咸阳市 - 3个区、9个县、2个县级市
            City("6104", "咸阳市", listOf(
                District("610402", "秦都区"), District("610403", "杨陵区"),
                District("610404", "渭城区"), District("610422", "三原县"),
                District("610423", "泾阳县"), District("610424", "乾县"),
                District("610425", "礼泉县"), District("610426", "永寿县"),
                District("610428", "长武县"), District("610429", "旬邑县"),
                District("610430", "淳化县"), District("610431", "武功县"),
                District("610481", "兴平市"), District("610482", "彬州市")
            )),
            // 渭南市 - 2个区、7个县、2个县级市
            City("6105", "渭南市", listOf(
                District("610502", "临渭区"), District("610503", "华州区"),
                District("610522", "潼关县"), District("610523", "大荔县"),
                District("610524", "合阳县"), District("610525", "澄城县"),
                District("610526", "蒲城县"), District("610527", "白水县"),
                District("610528", "富平县"), District("610581", "韩城市"),
                District("610582", "华阴市")
            )),
            // 延安市 - 2个区、10个县、1个县级市
            City("6106", "延安市", listOf(
                District("610602", "宝塔区"), District("610603", "安塞区"),
                District("610621", "延长县"), District("610622", "延川县"),
                District("610625", "志丹县"), District("610626", "吴起县"),
                District("610627", "甘泉县"), District("610628", "富县"),
                District("610629", "洛川县"), District("610630", "宜川县"),
                District("610631", "黄龙县"), District("610632", "黄陵县"),
                District("610681", "子长市")
            )),
            // 汉中市 - 2个区、9个县
            City("6107", "汉中市", listOf(
                District("610702", "汉台区"), District("610703", "南郑区"),
                District("610722", "城固县"), District("610723", "洋县"),
                District("610724", "西乡县"), District("610725", "勉县"),
                District("610726", "宁强县"), District("610727", "略阳县"),
                District("610728", "镇巴县"), District("610729", "留坝县"),
                District("610730", "佛坪县")
            )),
            // 榆林市 - 2个区、9个县、1个县级市
            City("6108", "榆林市", listOf(
                District("610802", "榆阳区"), District("610803", "横山区"),
                District("610822", "府谷县"), District("610824", "靖边县"),
                District("610825", "定边县"), District("610826", "绥德县"),
                District("610827", "米脂县"), District("610828", "佳县"),
                District("610829", "吴堡县"), District("610830", "清涧县"),
                District("610831", "子洲县"), District("610881", "神木市")
            )),
            // 安康市 - 1个区、8个县、1个县级市
            City("6109", "安康市", listOf(
                District("610902", "汉滨区"), District("610921", "汉阴县"),
                District("610922", "石泉县"), District("610923", "宁陕县"),
                District("610924", "紫阳县"), District("610925", "岚皋县"),
                District("610926", "平利县"), District("610927", "镇坪县"),
                District("610928", "旬阳县"), District("610929", "白河县")
            )),
            // 商洛市 - 1个区、6个县
            City("6110", "商洛市", listOf(
                District("611002", "商州区"), District("611021", "洛南县"),
                District("611022", "丹凤县"), District("611023", "商南县"),
                District("611024", "山阳县"), District("611025", "镇安县"),
                District("611026", "柞水县")
            ))
        )),
        // 甘肃省 (62) - 14个市州
        Province(code = "62", name = "甘肃省", cities = listOf(
            // 兰州市 - 5个区、3个县
            City("6201", "兰州市", listOf(
                District("620102", "城关区"), District("620103", "七里河区"),
                District("620104", "西固区"), District("620105", "安宁区"),
                District("620111", "红古区"), District("620121", "永登县"),
                District("620122", "皋兰县"), District("620123", "榆中县")
            )),
            // 嘉峪关市
            City("6202", "嘉峪关市", listOf(
                District("620200", "嘉峪关市")
            )),
            // 金昌市 - 1个区、1个县
            City("6203", "金昌市", listOf(
                District("620302", "金川区"), District("620321", "永昌县")
            )),
            // 白银市 - 2个区、3个县
            City("6204", "白银市", listOf(
                District("620402", "白银区"), District("620403", "平川区"),
                District("620421", "靖远县"), District("620422", "会宁县"),
                District("620423", "景泰县")
            )),
            // 天水市 - 2个区、4个县、1个自治县
            City("6205", "天水市", listOf(
                District("620502", "秦州区"), District("620503", "麦积区"),
                District("620521", "清水县"), District("620522", "秦安县"),
                District("620523", "甘谷县"), District("620524", "武山县"),
                District("620525", "张家川县")
            )),
            // 武威市 - 1个区、2个县、1个自治县
            City("6206", "武威市", listOf(
                District("620602", "凉州区"), District("620621", "民勤县"),
                District("620622", "古浪县"), District("620623", "天祝县")
            )),
            // 张掖市 - 1个区、4个县、1个自治县
            City("6207", "张掖市", listOf(
                District("620702", "甘州区"), District("620721", "肃南县"),
                District("620722", "民乐县"), District("620723", "临泽县"),
                District("620724", "高台县"), District("620725", "山丹县")
            )),
            // 平凉市 - 1个区、5个县、1个县级市
            City("6208", "平凉市", listOf(
                District("620802", "崆峒区"), District("620821", "泾川县"),
                District("620822", "灵台县"), District("620823", "崇信县"),
                District("620825", "庄浪县"), District("620826", "静宁县"),
                District("620881", "华亭市")
            )),
            // 酒泉市 - 1个区、2个县、2个自治县、2个县级市
            City("6209", "酒泉市", listOf(
                District("620902", "肃州区"), District("620921", "金塔县"),
                District("620922", "瓜州县"), District("620923", "肃北县"),
                District("620924", "阿克塞县"), District("620981", "玉门市"),
                District("620982", "敦煌市")
            )),
            // 庆阳市 - 1个区、7个县
            City("6210", "庆阳市", listOf(
                District("621002", "西峰区"), District("621021", "庆城县"),
                District("621022", "环县"), District("621023", "华池县"),
                District("621024", "合水县"), District("621025", "正宁县"),
                District("621026", "宁县"), District("621027", "镇原县")
            )),
            // 定西市 - 1个区、6个县
            City("6211", "定西市", listOf(
                District("621102", "安定区"), District("621121", "通渭县"),
                District("621122", "陇西县"), District("621123", "渭源县"),
                District("621124", "临洮县"), District("621125", "漳县"),
                District("621126", "岷县")
            )),
            // 陇南市 - 1个区、8个县
            City("6212", "陇南市", listOf(
                District("621202", "武都区"), District("621221", "成县"),
                District("621222", "文县"), District("621223", "宕昌县"),
                District("621224", "康县"), District("621225", "西和县"),
                District("621226", "礼县"), District("621227", "徽县"),
                District("621228", "两当县")
            )),
            // 临夏回族自治州 - 1个县级市、5个县、2个自治县
            City("6229", "临夏回族自治州", listOf(
                District("622901", "临夏市"), District("622921", "临夏县"),
                District("622922", "康乐县"), District("622923", "永靖县"),
                District("622924", "广河县"), District("622925", "和政县"),
                District("622926", "东乡县"), District("622927", "积石山县")
            )),
            // 甘南藏族自治州 - 1个县级市、7个县
            City("6230", "甘南藏族自治州", listOf(
                District("623001", "合作市"), District("623021", "临潭县"),
                District("623022", "卓尼县"), District("623023", "舟曲县"),
                District("623024", "迭部县"), District("623025", "玛曲县"),
                District("623026", "碌曲县"), District("623027", "夏河县")
            ))
        )),
        // 青海省 (63) - 8个市州
        Province(code = "63", name = "青海省", cities = listOf(
            // 西宁市 - 5个区、2个县、1个自治县
            City("6301", "西宁市", listOf(
                District("630102", "城东区"), District("630103", "城中区"),
                District("630104", "城西区"), District("630105", "城北区"),
                District("630106", "湟中区"), District("630121", "大通县"),
                District("630123", "湟源县")
            )),
            // 海东市 - 2个区、4个自治县
            City("6302", "海东市", listOf(
                District("630202", "乐都区"), District("630203", "平安区"),
                District("630222", "民和县"), District("630223", "互助县"),
                District("630224", "化隆县"), District("630225", "循化县")
            )),
            // 海北藏族自治州 - 3个县、1个自治县
            City("6322", "海北藏族自治州", listOf(
                District("632221", "门源县"), District("632222", "祁连县"),
                District("632223", "海晏县"), District("632224", "刚察县")
            )),
            // 黄南藏族自治州 - 1个县级市、2个县、1个自治县
            City("6323", "黄南藏族自治州", listOf(
                District("632301", "同仁市"), District("632322", "尖扎县"),
                District("632323", "泽库县"), District("632324", "河南县")
            )),
            // 海南藏族自治州 - 5个县
            City("6325", "海南藏族自治州", listOf(
                District("632521", "共和县"), District("632522", "同德县"),
                District("632523", "贵德县"), District("632524", "兴海县"),
                District("632525", "贵南县")
            )),
            // 果洛藏族自治州 - 6个县
            City("6326", "果洛藏族自治州", listOf(
                District("632621", "玛沁县"), District("632622", "班玛县"),
                District("632623", "甘德县"), District("632624", "达日县"),
                District("632625", "久治县"), District("632626", "玛多县")
            )),
            // 玉树藏族自治州 - 1个县级市、5个县
            City("6327", "玉树藏族自治州", listOf(
                District("632701", "玉树市"), District("632722", "杂多县"),
                District("632723", "称多县"), District("632724", "治多县"),
                District("632725", "囊谦县"), District("632726", "曲麻莱县")
            )),
            // 海西蒙古族藏族自治州 - 3个县级市、3个县、1个自治县
            City("6328", "海西蒙古族藏族自治州", listOf(
                District("632801", "格尔木市"), District("632802", "德令哈市"),
                District("632803", "茫崖市"), District("632821", "乌兰县"),
                District("632822", "都兰县"), District("632823", "天峻县"),
                District("632857", "大柴旦行委")
            ))
        )),
        // 宁夏回族自治区 (64) - 5个地级市
        Province(code = "64", name = "宁夏回族自治区", cities = listOf(
            // 银川市 - 3个区、2个县、1个县级市
            City("6401", "银川市", listOf(
                District("640104", "兴庆区"), District("640105", "西夏区"),
                District("640106", "金凤区"), District("640121", "永宁县"),
                District("640122", "贺兰县"), District("640181", "灵武市")
            )),
            // 石嘴山市 - 2个区、1个县
            City("6402", "石嘴山市", listOf(
                District("640202", "大武口区"), District("640205", "惠农区"),
                District("640221", "平罗县")
            )),
            // 吴忠市 - 2个区、2个县、1个县级市
            City("6403", "吴忠市", listOf(
                District("640302", "利通区"), District("640303", "红寺堡区"),
                District("640323", "盐池县"), District("640324", "同心县"),
                District("640381", "青铜峡市")
            )),
            // 固原市 - 1个区、4个县
            City("6404", "固原市", listOf(
                District("640402", "原州区"), District("640422", "西吉县"),
                District("640423", "隆德县"), District("640424", "泾源县"),
                District("640425", "彭阳县")
            )),
            // 中卫市 - 1个区、2个县
            City("6405", "中卫市", listOf(
                District("640502", "沙坡头区"), District("640521", "中宁县"),
                District("640522", "海原县")
            ))
        )),
        // 新疆维吾尔自治区 (65) - 14个地州市
        Province(code = "65", name = "新疆维吾尔自治区", cities = listOf(
            // 乌鲁木齐市 - 7个区、1个县
            City("6501", "乌鲁木齐市", listOf(
                District("650102", "天山区"), District("650103", "沙依巴克区"),
                District("650104", "新市区"), District("650105", "水磨沟区"),
                District("650106", "头屯河区"), District("650107", "达坂城区"),
                District("650109", "米东区"), District("650121", "乌鲁木齐县")
            )),
            // 克拉玛依市 - 4个区
            City("6502", "克拉玛依市", listOf(
                District("650202", "独山子区"), District("650203", "克拉玛依区"),
                District("650204", "白碱滩区"), District("650205", "乌尔禾区")
            )),
            // 吐鲁番市 - 1个区、2个县
            City("6504", "吐鲁番市", listOf(
                District("650402", "高昌区"), District("650421", "鄯善县"),
                District("650422", "托克逊县")
            )),
            // 哈密市 - 1个区、1个县、1个自治县
            City("6505", "哈密市", listOf(
                District("650502", "伊州区"), District("650521", "巴里坤县"),
                District("650522", "伊吾县")
            )),
            // 昌吉回族自治州 - 2个县级市、4个县、1个自治县
            City("6523", "昌吉回族自治州", listOf(
                District("652301", "昌吉市"), District("652302", "阜康市"),
                District("652323", "呼图壁县"), District("652324", "玛纳斯县"),
                District("652325", "奇台县"), District("652327", "吉木萨尔县"),
                District("652328", "木垒县")
            )),
            // 博尔塔拉蒙古自治州 - 2个县级市、2个县
            City("6527", "博尔塔拉蒙古自治州", listOf(
                District("652701", "博乐市"), District("652702", "阿拉山口市"),
                District("652722", "精河县"), District("652723", "温泉县")
            )),
            // 巴音郭楞蒙古自治州 - 1个县级市、7个县、1个自治县
            City("6528", "巴音郭楞蒙古自治州", listOf(
                District("652801", "库尔勒市"), District("652822", "轮台县"),
                District("652823", "尉犁县"), District("652824", "若羌县"),
                District("652825", "且末县"), District("652826", "焉耆县"),
                District("652827", "和静县"), District("652828", "和硕县"),
                District("652829", "博湖县")
            )),
            // 阿克苏地区 - 2个县级市、7个县
            City("6529", "阿克苏地区", listOf(
                District("652901", "阿克苏市"), District("652902", "库车市"),
                District("652922", "温宿县"), District("652924", "沙雅县"),
                District("652925", "新和县"), District("652926", "拜城县"),
                District("652927", "乌什县"), District("652928", "阿瓦提县"),
                District("652929", "柯坪县")
            )),
            // 克孜勒苏柯尔克孜自治州 - 1个县级市、3个县
            City("6530", "克孜勒苏柯尔克孜自治州", listOf(
                District("653001", "阿图什市"), District("653022", "阿克陶县"),
                District("653023", "阿合奇县"), District("653024", "乌恰县")
            )),
            // 喀什地区 - 1个县级市、10个县、1个自治县
            City("6531", "喀什地区", listOf(
                District("653101", "喀什市"), District("653121", "疏附县"),
                District("653122", "疏勒县"), District("653123", "英吉沙县"),
                District("653124", "泽普县"), District("653125", "莎车县"),
                District("653126", "叶城县"), District("653127", "麦盖提县"),
                District("653128", "岳普湖县"), District("653129", "伽师县"),
                District("653130", "巴楚县"), District("653131", "塔什库尔干县")
            )),
            // 和田地区 - 1个县级市、9个县
            City("6532", "和田地区", listOf(
                District("653201", "和田市"), District("653221", "和田县"),
                District("653222", "墨玉县"), District("653223", "皮山县"),
                District("653224", "洛浦县"), District("653225", "策勒县"),
                District("653226", "于田县"), District("653227", "民丰县")
            )),
            // 伊犁哈萨克自治州 - 3个县级市、7个县、1个自治县
            City("6540", "伊犁哈萨克自治州", listOf(
                District("654002", "伊宁市"), District("654003", "奎屯市"),
                District("654004", "霍尔果斯市"), District("654021", "伊宁县"),
                District("654022", "察布查尔县"), District("654023", "霍城县"),
                District("654024", "巩留县"), District("654025", "新源县"),
                District("654026", "昭苏县"), District("654027", "特克斯县"),
                District("654028", "尼勒克县")
            )),
            // 塔城地区 - 3个县级市、3个县、1个自治县
            City("6542", "塔城地区", listOf(
                District("654201", "塔城市"), District("654202", "乌苏市"),
                District("654203", "沙湾市"), District("654221", "额敏县"),
                District("654223", "裕民县"), District("654224", "和布克赛尔县")
            )),
            // 阿勒泰地区 - 1个县级市、6个县
            City("6543", "阿勒泰地区", listOf(
                District("654301", "阿勒泰市"), District("654321", "布尔津县"),
                District("654322", "富蕴县"), District("654323", "福海县"),
                District("654324", "哈巴河县"), District("654325", "青河县"),
                District("654326", "吉木乃县")
            )),
            // 自治区直辖县级行政区划 - 12个县级市
            City("6590", "自治区直辖县级行政区划", listOf(
                District("659001", "石河子市"), District("659002", "阿拉尔市"),
                District("659003", "图木舒克市"), District("659004", "五家渠市"),
                District("659005", "北屯市"), District("659006", "铁门关市"),
                District("659007", "双河市"), District("659008", "可克达拉市"),
                District("659009", "昆玉市"), District("659010", "胡杨河市"),
                District("659011", "新星市"), District("659012", "白杨市")
            ))
        )),
        // 台湾省 (71) - 中国不可分割的一部分
        Province(code = "71", name = "台湾省", cities = listOf(
            // 台北市 (7101) - 12个区
            City("7101", "台北市", listOf(
                District("710101", "中正区"), District("710102", "大同区"),
                District("710103", "中山区"), District("710104", "松山区"),
                District("710105", "大安区"), District("710106", "万华区"),
                District("710107", "信义区"), District("710108", "士林区"),
                District("710109", "北投区"), District("710110", "内湖区"),
                District("710111", "南港区"), District("710112", "文山区")
            )),
            // 新北市 (7102)
            City("7102", "新北市", listOf(
                District("710201", "板桥区"), District("710202", "三重区"),
                District("710203", "中和区"), District("710204", "永和区"),
                District("710205", "新庄区"), District("710206", "新店区"),
                District("710207", "土城区"), District("710208", "芦洲区"),
                District("710209", "树林区"), District("710210", "汐止区"),
                District("710211", "莺歌区"), District("710212", "三峡区"),
                District("710213", "淡水区"), District("710214", "瑞芳区"),
                District("710215", "五股区"), District("710216", "泰山区"),
                District("710217", "林口区"), District("710218", "深坑区"),
                District("710219", "石碇区"), District("710220", "坪林区"),
                District("710221", "三芝区"), District("710222", "石门区"),
                District("710223", "八里区"), District("710224", "平溪区"),
                District("710225", "双溪区"), District("710226", "贡寮区"),
                District("710227", "金山区"), District("710228", "万里区"),
                District("710229", "乌来区")
            )),
            // 桃园市 (7103)
            City("7103", "桃园市", listOf(
                District("710301", "桃园区"), District("710302", "中坜区"),
                District("710303", "大溪区"), District("710304", "杨梅区"),
                District("710305", "芦竹区"), District("710306", "大园区"),
                District("710307", "龟山区"), District("710308", "八德区"),
                District("710309", "龙潭区"), District("710310", "平镇区"),
                District("710311", "新屋区"), District("710312", "观音区"),
                District("710313", "复兴区")
            )),
            // 台中市 (7104)
            City("7104", "台中市", listOf(
                District("710401", "中区"), District("710402", "东区"),
                District("710403", "南区"), District("710404", "西区"),
                District("710405", "北区"), District("710406", "北屯区"),
                District("710407", "西屯区"), District("710408", "南屯区"),
                District("710409", "太平区"), District("710410", "大里区"),
                District("710411", "雾峰区"), District("710412", "乌日区"),
                District("710413", "丰原区"), District("710414", "后里区"),
                District("710415", "石冈区"), District("710416", "东势区"),
                District("710417", "和平区"), District("710418", "新社区"),
                District("710419", "潭子区"), District("710420", "大雅区"),
                District("710421", "神冈区"), District("710422", "大肚区"),
                District("710423", "沙鹿区"), District("710424", "龙井区"),
                District("710425", "梧栖区"), District("710426", "清水区"),
                District("710427", "大甲区"), District("710428", "外埔区"),
                District("710429", "大安区")
            )),
            // 台南市 (7105)
            City("7105", "台南市", listOf(
                District("710501", "中西区"), District("710502", "东区"),
                District("710503", "南区"), District("710504", "北区"),
                District("710505", "安平区"), District("710506", "安南区"),
                District("710507", "永康区"), District("710508", "归仁区"),
                District("710509", "新化区"), District("710510", "左镇区"),
                District("710511", "玉井区"), District("710512", "楠西区"),
                District("710513", "南化区"), District("710514", "仁德区"),
                District("710515", "关庙区"), District("710516", "龙崎区"),
                District("710517", "官田区"), District("710518", "麻豆区"),
                District("710519", "佳里区"), District("710520", "西港区"),
                District("710521", "七股区"), District("710522", "将军区"),
                District("710523", "学甲区"), District("710524", "北门区"),
                District("710525", "新营区"), District("710526", "后壁区"),
                District("710527", "白河区"), District("710528", "东山区"),
                District("710529", "六甲区"), District("710530", "下营区"),
                District("710531", "柳营区"), District("710532", "盐水区"),
                District("710533", "善化区"), District("710534", "大内区"),
                District("710535", "山上区"), District("710536", "新市区"),
                District("710537", "安定区")
            )),
            // 高雄市 (7106)
            City("7106", "高雄市", listOf(
                District("710601", "楠梓区"), District("710602", "左营区"),
                District("710603", "鼓山区"), District("710604", "三民区"),
                District("710605", "盐埕区"), District("710606", "前金区"),
                District("710607", "新兴区"), District("710608", "苓雅区"),
                District("710609", "前镇区"), District("710610", "旗津区"),
                District("710611", "小港区"), District("710612", "凤山区"),
                District("710613", "林园区"), District("710614", "大寮区"),
                District("710615", "大树区"), District("710616", "大社区"),
                District("710617", "仁武区"), District("710618", "鸟松区"),
                District("710619", "冈山区"), District("710620", "桥头区"),
                District("710621", "燕巢区"), District("710622", "田寮区"),
                District("710623", "阿莲区"), District("710624", "路竹区"),
                District("710625", "湖内区"), District("710626", "茄萣区"),
                District("710627", "永安区"), District("710628", "弥陀区"),
                District("710629", "梓官区"), District("710630", "旗山区"),
                District("710631", "美浓区"), District("710632", "六龟区"),
                District("710633", "甲仙区"), District("710634", "杉林区"),
                District("710635", "内门区"), District("710636", "茂林区"),
                District("710637", "桃源区"), District("710638", "那玛夏区")
            )),
            // 基隆市 (7107)
            City("7107", "基隆市", listOf(
                District("710701", "仁爱区"), District("710702", "信义区"),
                District("710703", "中正区"), District("710704", "中山区"),
                District("710705", "安乐区"), District("710706", "暖暖区"),
                District("710707", "七堵区")
            )),
            // 新竹市 (7108)
            City("7108", "新竹市", listOf(
                District("710801", "东区"), District("710802", "北区"),
                District("710803", "香山区")
            )),
            // 嘉义市 (7109)
            City("7109", "嘉义市", listOf(
                District("710901", "东区"), District("710902", "西区")
            )),
            // 新竹县 (7110)
            City("7110", "新竹县", listOf(
                District("711001", "竹北市"), District("711002", "竹东镇"),
                District("711003", "新埔镇"), District("711004", "关西镇"),
                District("711005", "湖口乡"), District("711006", "新丰乡"),
                District("711007", "芎林乡"), District("711008", "横山乡"),
                District("711009", "北埔乡"), District("711010", "宝山乡"),
                District("711011", "峨眉乡"), District("711012", "尖石乡"),
                District("711013", "五峰乡")
            )),
            // 苗栗县 (7111)
            City("7111", "苗栗县", listOf(
                District("711101", "苗栗市"), District("711102", "苑里镇"),
                District("711103", "通霄镇"), District("711104", "竹南镇"),
                District("711105", "头份市"), District("711106", "后龙镇"),
                District("711107", "卓兰镇"), District("711108", "大湖乡"),
                District("711109", "公馆乡"), District("711110", "铜锣乡"),
                District("711111", "南庄乡"), District("711112", "头屋乡"),
                District("711113", "三义乡"), District("711114", "西湖乡"),
                District("711115", "造桥乡"), District("711116", "三湾乡"),
                District("711117", "狮潭乡"), District("711118", "泰安乡")
            )),
            // 彰化县 (7112)
            City("7112", "彰化县", listOf(
                District("711201", "彰化市"), District("711202", "鹿港镇"),
                District("711203", "和美镇"), District("711204", "线西乡"),
                District("711205", "伸港乡"), District("711206", "福兴乡"),
                District("711207", "秀水乡"), District("711208", "花坛乡"),
                District("711209", "芬园乡"), District("711210", "员林市"),
                District("711211", "溪湖镇"), District("711212", "田中镇"),
                District("711213", "大村乡"), District("711214", "埔盐乡"),
                District("711215", "埔心乡"), District("711216", "永靖乡"),
                District("711217", "社头乡"), District("711218", "二水乡"),
                District("711219", "北斗镇"), District("711220", "二林镇"),
                District("711221", "田尾乡"), District("711222", "埤头乡"),
                District("711223", "芳苑乡"), District("711224", "大城乡"),
                District("711225", "竹塘乡"), District("711226", "溪州乡")
            )),
            // 南投县 (7113)
            City("7113", "南投县", listOf(
                District("711301", "南投市"), District("711302", "埔里镇"),
                District("711303", "草屯镇"), District("711304", "竹山镇"),
                District("711305", "集集镇"), District("711306", "名间乡"),
                District("711307", "鹿谷乡"), District("711308", "中寮乡"),
                District("711309", "鱼池乡"), District("711310", "国姓乡"),
                District("711311", "水里乡"), District("711312", "信义乡"),
                District("711313", "仁爱乡")
            )),
            // 云林县 (7114)
            City("7114", "云林县", listOf(
                District("711401", "斗六市"), District("711402", "斗南镇"),
                District("711403", "虎尾镇"), District("711404", "西螺镇"),
                District("711405", "土库镇"), District("711406", "北港镇"),
                District("711407", "古坑乡"), District("711408", "大埤乡"),
                District("711409", "莿桐乡"), District("711410", "林内乡"),
                District("711411", "二仑乡"), District("711412", "仑背乡"),
                District("711413", "麦寮乡"), District("711414", "东势乡"),
                District("711415", "褒忠乡"), District("711416", "台西乡"),
                District("711417", "元长乡"), District("711418", "四湖乡"),
                District("711419", "口湖乡"), District("711420", "水林乡")
            )),
            // 嘉义县 (7115)
            City("7115", "嘉义县", listOf(
                District("711501", "太保市"), District("711502", "朴子市"),
                District("711503", "布袋镇"), District("711504", "大林镇"),
                District("711505", "民雄乡"), District("711506", "溪口乡"),
                District("711507", "新港乡"), District("711508", "六脚乡"),
                District("711509", "东石乡"), District("711510", "义竹乡"),
                District("711511", "鹿草乡"), District("711512", "水上乡"),
                District("711513", "中埔乡"), District("711514", "竹崎乡"),
                District("711515", "梅山乡"), District("711516", "番路乡"),
                District("711517", "大埔乡"), District("711518", "阿里山乡")
            )),
            // 屏东县 (7116)
            City("7116", "屏东县", listOf(
                District("711601", "屏东市"), District("711602", "潮州镇"),
                District("711603", "东港镇"), District("711604", "恒春镇"),
                District("711605", "万丹乡"), District("711606", "长治乡"),
                District("711607", "麟洛乡"), District("711608", "九如乡"),
                District("711609", "里港乡"), District("711610", "盐埔乡"),
                District("711611", "高树乡"), District("711612", "万峦乡"),
                District("711613", "内埔乡"), District("711614", "竹田乡"),
                District("711615", "新埤乡"), District("711616", "枋寮乡"),
                District("711617", "新园乡"), District("711618", "崁顶乡"),
                District("711619", "林边乡"), District("711620", "南州乡"),
                District("711621", "佳冬乡"), District("711622", "琉球乡"),
                District("711623", "车城乡"), District("711624", "满州乡"),
                District("711625", "枋山乡"), District("711626", "三地门乡"),
                District("711627", "雾台乡"), District("711628", "玛家乡"),
                District("711629", "泰武乡"), District("711630", "来义乡"),
                District("711631", "春日乡"), District("711632", "狮子乡"),
                District("711633", "牡丹乡")
            )),
            // 宜兰县 (7117)
            City("7117", "宜兰县", listOf(
                District("711701", "宜兰市"), District("711702", "罗东镇"),
                District("711703", "苏澳镇"), District("711704", "头城镇"),
                District("711705", "礁溪乡"), District("711706", "壮围乡"),
                District("711707", "员山乡"), District("711708", "冬山乡"),
                District("711709", "五结乡"), District("711710", "三星乡"),
                District("711711", "大同乡"), District("711712", "南澳乡")
            )),
            // 花莲县 (7118)
            City("7118", "花莲县", listOf(
                District("711801", "花莲市"), District("711802", "凤林镇"),
                District("711803", "玉里镇"), District("711804", "新城乡"),
                District("711805", "吉安乡"), District("711806", "寿丰乡"),
                District("711807", "光复乡"), District("711808", "丰滨乡"),
                District("711809", "瑞穗乡"), District("711810", "富里乡"),
                District("711811", "秀林乡"), District("711812", "万荣乡"),
                District("711813", "卓溪乡")
            )),
            // 台东县 (7119)
            City("7119", "台东县", listOf(
                District("711901", "台东市"), District("711902", "成功镇"),
                District("711903", "关山镇"), District("711904", "卑南乡"),
                District("711905", "鹿野乡"), District("711906", "池上乡"),
                District("711907", "东河乡"), District("711908", "长滨乡"),
                District("711909", "太麻里乡"), District("711910", "大武乡"),
                District("711911", "绿岛乡"), District("711912", "海端乡"),
                District("711913", "延平乡"), District("711914", "金峰乡"),
                District("711915", "达仁乡"), District("711916", "兰屿乡")
            )),
            // 澎湖县 (7120)
            City("7120", "澎湖县", listOf(
                District("712001", "马公市"), District("712002", "湖西乡"),
                District("712003", "白沙乡"), District("712004", "西屿乡"),
                District("712005", "望安乡"), District("712006", "七美乡")
            ))
        ))
    )

    /**
     * 根据省份名称获取省份
     * @param name 省份名称
     * @return 省份对象，找不到返回null
     */
    fun getProvinceByName(name: String): Province? {
        return provinces.find { it.name == name }
    }

    /**
     * 根据省份代码获取省份
     * @param code 省份代码
     * @return 省份对象，找不到返回null
     */
    fun getProvinceByCode(code: String): Province? {
        return provinces.find { it.code == code }
    }

    /**
     * 根据城市名称获取城市
     * @param provinceName 省份名称（可选，不提供则搜索所有省份）
     * @param cityName 城市名称
     * @return 城市对象，找不到返回null
     */
    fun getCityByName(provinceName: String? = null, cityName: String): City? {
        val provincesToSearch = if (provinceName != null) {
            listOfNotNull(getProvinceByName(provinceName))
        } else {
            provinces
        }
        for (province in provincesToSearch) {
            val city = province.cities.find { it.name == cityName }
            if (city != null) return city
        }
        return null
    }

    /**
     * 根据城市代码获取城市
     * @param code 城市代码
     * @return 城市对象，找不到返回null
     */
    fun getCityByCode(code: String): City? {
        for (province in provinces) {
            val city = province.cities.find { it.code == code }
            if (city != null) return city
        }
        return null
    }

    /**
     * 根据区县名称获取区县
     * @param provinceName 省份名称（可选）
     * @param cityName 城市名称（可选）
     * @param districtName 区县名称
     * @return 区县对象，找不到返回null
     */
    fun getDistrictByName(
        provinceName: String? = null,
        cityName: String? = null,
        districtName: String
    ): District? {
        val provincesToSearch = if (provinceName != null) {
            listOfNotNull(getProvinceByName(provinceName))
        } else {
            provinces
        }
        for (province in provincesToSearch) {
            val citiesToSearch = if (cityName != null) {
                listOfNotNull(province.cities.find { it.name == cityName })
            } else {
                province.cities
            }
            for (city in citiesToSearch) {
                val district = city.districts.find { it.name == districtName }
                if (district != null) return district
            }
        }
        return null
    }

    /**
     * 根据区县代码获取区县
     * @param code 区县代码
     * @return 区县对象，找不到返回null
     */
    fun getDistrictByCode(code: String): District? {
        for (province in provinces) {
            for (city in province.cities) {
                val district = city.districts.find { it.code == code }
                if (district != null) return district
            }
        }
        return null
    }

    /**
     * 获取所有省份名称列表
     * @return 省份名称列表
     */
    fun getAllProvinceNames(): List<String> {
        return provinces.map { it.name }
    }

    /**
     * 获取指定省份的所有城市名称
     * @param provinceName 省份名称
     * @return 城市名称列表，省份不存在返回空列表
     */
    fun getCityNamesByProvince(provinceName: String): List<String> {
        return getProvinceByName(provinceName)?.cities?.map { it.name } ?: emptyList()
    }

    /**
     * 获取指定城市的所有区县名称
     * @param provinceName 省份名称（可选）
     * @param cityName 城市名称
     * @return 区县名称列表，城市不存在返回空列表
     */
    fun getDistrictNamesByCity(provinceName: String? = null, cityName: String): List<String> {
        return getCityByName(provinceName, cityName)?.districts?.map { it.name } ?: emptyList()
    }

    /**
     * 搜索省份（支持模糊匹配）
     * @param keyword 关键词
     * @return 匹配的省份列表
     */
    fun searchProvinces(keyword: String): List<Province> {
        return provinces.filter { it.name.contains(keyword) }
    }

    /**
     * 搜索城市（支持模糊匹配）
     * @param keyword 关键词
     * @return 匹配的城市列表
     */
    fun searchCities(keyword: String): List<City> {
        val result = mutableListOf<City>()
        for (province in provinces) {
            result.addAll(province.cities.filter { it.name.contains(keyword) })
        }
        return result
    }

    /**
     * 搜索区县（支持模糊匹配）
     * @param keyword 关键词
     * @return 匹配的区县列表
     */
    fun searchDistricts(keyword: String): List<District> {
        val result = mutableListOf<District>()
        for (province in provinces) {
            for (city in province.cities) {
                result.addAll(city.districts.filter { it.name.contains(keyword) })
            }
        }
        return result
    }
}
