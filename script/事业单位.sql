
INSERT INTO "会计要素表" ("uuid", "编码", "名称", "描述") VALUES ('2de1b788-425d-11ee-8fbb-1063c8523004', '1', '资产类', '');
INSERT INTO "会计要素表" ("uuid", "编码", "名称", "描述") VALUES ('3d657c49-425d-11ee-ae75-1063c8523004', '2', '负债类', '');
INSERT INTO "会计要素表" ("uuid", "编码", "名称", "描述") VALUES ('595670db-425d-11ee-9b57-1063c8523004', '3', '净资产类', '');
INSERT INTO "会计要素表" ("uuid", "编码", "名称", "描述") VALUES ('5cc1d68e-425d-11ee-943e-1063c8523004', '4', '收入类', '');
INSERT INTO "会计要素表" ("uuid", "编码", "名称", "描述") VALUES ('5fd32e90-425d-11ee-aac8-1063c8523004', '5', '费用类', '');
INSERT INTO "科目表" ("uuid", "类别", "代码", "名称","有子级", "辅助") VALUES ('ccdf5c5c-425d-11ee-a4da-1063c8523004', '资产类', '1001', '库存现金','0', '');
INSERT INTO "科目表" ("uuid", "类别", "代码", "名称","有子级", "辅助") VALUES ('cd86a457-425d-11ee-b0f1-1063c8523004', '资产类', '1002', '银行存款', '0', '');
INSERT INTO "科目表" ("uuid", "类别", "代码", "名称","有子级", "辅助") VALUES ('cc36d9c8-425d-11ee-a43a-1063c8523004', '资产类', '1218', '其他应收款','0', '');
INSERT INTO "科目表" ("uuid", "类别", "代码", "名称","有子级", "辅助") VALUES ('b8980067-47fd-11ee-9447-1063c8523004', '资产类', '1302', '库存物品', '0', '');
INSERT INTO "科目表" ("uuid", "类别", "代码", "名称","有子级", "辅助") VALUES ('caaffd59-425d-11ee-9d81-1063c8523004', '负债类', '2302', '应付账款', '0', '');
INSERT INTO "科目表" ("uuid", "类别", "代码", "名称","有子级", "辅助") VALUES ('bd7f8b22-47fd-11ee-bcf0-1063c8523004', '负债类', '2307', '其他应付款','0', '');
INSERT INTO "科目表" ("uuid", "类别", "代码", "名称","有子级", "辅助") VALUES ('be2de5a2-47fd-11ee-a59b-1063c8523004', '净资产类', '3001', '累计盈余','0', '');
INSERT INTO "科目表" ("uuid", "类别", "代码", "名称","有子级", "辅助") VALUES ('beb539a6-47fd-11ee-ad05-1063c8523004', '净资产类', '3301', '本期盈余','0', '');
INSERT INTO "科目表" ("uuid", "类别", "代码", "名称","有子级", "辅助") VALUES ('bf2a585c-47fd-11ee-9a7d-1063c8523004', '收入类', '4201', '上级补助收入','0', '');
INSERT INTO "科目表" ("uuid", "类别", "代码", "名称","有子级", "辅助") VALUES ('bf93374f-47fd-11ee-94d1-1063c8523004', '收入类', '4401', '主营业务收入','0', '');
INSERT INTO "科目表" ("uuid", "类别", "代码", "名称","有子级", "辅助") VALUES ('c0082140-47fd-11ee-8ce1-1063c8523004', '收入类', '4609', '其他收入','0', '');
INSERT INTO "科目表" ("uuid", "类别", "代码", "名称","有子级", "辅助") VALUES ('c569641d-425d-11ee-a6e5-1063c8523004', '费用类', '5201', '主营业务费用','0', '');
INSERT INTO "科目表" ("uuid", "类别", "代码", "名称","有子级", "辅助") VALUES ('c06ffe01-47fd-11ee-a977-1063c8523004', '费用类', '5901', '其他费用','0', '');
INSERT INTO "辅助类别表" ("辅助类", "说明") VALUES ('部门', '用于核算不同部门的费用');
INSERT INTO "辅助类别表" ("辅助类", "说明") VALUES ('供应商', '用于不同供应商');




