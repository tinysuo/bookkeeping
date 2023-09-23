BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "辅助项目表" (
	"id"	INTEGER NOT NULL UNIQUE,
	"类别"	TEXT NOT NULL,
	"辅助"	TEXT NOT NULL,
	"说明"	TEXT,
	PRIMARY KEY("id" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "会计要素表" (
	"id"	INTEGER NOT NULL,
	"uuid"	TEXT NOT NULL,
	"编码"	TEXT NOT NULL UNIQUE,
	"名称"	TEXT NOT NULL UNIQUE,
	"描述"	TEXT,
	PRIMARY KEY("id" AUTOINCREMENT)
);
INSERT INTO "辅助项目表" ("id","类别","辅助","说明") VALUES (1,'伙食费用辅助','粮食费用','粮食费用挂此项辅助，方便核算 ');
INSERT INTO "辅助项目表" ("id","类别","辅助","说明") VALUES (2,'伙食费用辅助','食油费用',NULL);
INSERT INTO "会计要素表" ("id","uuid","编码","名称","描述") VALUES (1,'2de1b788-425d-11ee-8fbb-1063c8523004','1','资产类',NULL);
INSERT INTO "会计要素表" ("id","uuid","编码","名称","描述") VALUES (2,'3d657c49-425d-11ee-ae75-1063c8523004','2','负债类',NULL);
INSERT INTO "会计要素表" ("id","uuid","编码","名称","描述") VALUES (3,'595670db-425d-11ee-9b57-1063c8523004','3','净资产类',NULL);
INSERT INTO "会计要素表" ("id","uuid","编码","名称","描述") VALUES (4,'5cc1d68e-425d-11ee-943e-1063c8523004','4','收入类',NULL);
INSERT INTO "会计要素表" ("id","uuid","编码","名称","描述") VALUES (5,'5fd32e90-425d-11ee-aac8-1063c8523004','5','费用类',NULL);
COMMIT;
