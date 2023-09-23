CREATE TABLE "会计期间表" (
	"id"	INTEGER NOT NULL UNIQUE,
	"名称"	TEXT NOT NULL,
	"开始"	DATE NOT NULL  UNIQUE,
	"结束"	DATE NOT NULL  UNIQUE,
	"结账"	INTEGER NOT NULL DEFAULT 0,
	PRIMARY KEY("id" AUTOINCREMENT)
);
CREATE TABLE "会计要素表" (
	"id"	INTEGER NOT NULL  UNIQUE,
	"uuid"	TEXT NOT NULL UNIQUE,
	"编码"	TEXT NOT NULL UNIQUE,
	"名称"	TEXT NOT NULL UNIQUE,
	"描述"	TEXT NOT NULL DEFAULT '',
	PRIMARY KEY("id" AUTOINCREMENT)
);
CREATE TABLE "凭证表" (
	"id"	INTEGER NOT NULL UNIQUE,
	"uuid"	TEXT NOT NULL UNIQUE,
	"凭证号"	INTEGER NOT NULL,
	"凭证日期"	INTEGER NOT NULL,
	"摘要"	INTEGER NOT NULL,
	"编辑时间"	TEXT NOT NULL,
	"附件数"	INTEGER NOT NULL DEFAULT 0,
	"电子付件数"	INTEGER NOT NULL DEFAULT 0,
	"审核人"	TEXT NOT NULL DEFAULT '',
	"记账人"	TEXT NOT NULL DEFAULT '',
	"记账"	INTEGER NOT NULL DEFAULT 0,
	PRIMARY KEY("id" AUTOINCREMENT)
);
CREATE TABLE "分录表" (
	"id"	INTEGER NOT NULL UNIQUE,
	"uuid"	TEXT NOT NULL UNIQUE,
	"凭证uuid"	TEXT NOT NULL,
	"摘要"	TEXT NOT NULL,
	"科目uuid"	TEXT NOT NULL,
	"借方金额"	INTEGER NOT NULL DEFAULT 0,
	"贷方金额"	INTEGER NOT NULL DEFAULT 0,
	"辅助"	TEXT NOT NULL DEFAULT '',
	PRIMARY KEY("id" AUTOINCREMENT)
);
CREATE TABLE "参数表" (
	"id"	INTEGER NOT NULL,
	"key"	TEXT NOT NULL UNIQUE,
	"data"	TEXT NOT NULL DEFAULT '',
	PRIMARY KEY("id" AUTOINCREMENT)
);
CREATE TABLE "明细表" (
	"id"	INTEGER NOT NULL UNIQUE,
	"凭证号"	INTEGER NOT NULL,
	"凭证uuid"	TEXT NOT NULL,
	"凭证日期"	DATE NOT NULL,
	"分录摘要"	TEXT NOT NULL DEFAULT '',
	"科目uuid"	TEXT NOT NULL,
	"借方金额"	INTEGER NOT NULL DEFAULT 0,
	"贷方金额"	INTEGER NOT NULL DEFAULT 0,
	"辅助"	TEXT NOT NULL DEFAULT '',
	PRIMARY KEY("id" AUTOINCREMENT)
);
CREATE TABLE "电子附件表" (
	"id"	INTEGER NOT NULL UNIQUE,
	"凭证uuid"	TEXT NOT NULL,
	"文件名"	TEXT,
	"格式"	TEXT,
	"数据"	BLOB NOT NULL,
	PRIMARY KEY("id" AUTOINCREMENT)
);
CREATE TABLE "科目表" (
	"id"	INTEGER NOT NULL UNIQUE,
	"uuid"	TEXT NOT NULL UNIQUE,
	"类别"	TEXT NOT NULL,
	"代码"	TEXT NOT NULL UNIQUE,
	"名称"	TEXT NOT NULL UNIQUE,
	"父uuid"	TEXT NOT NULL DEFAULT '',
	"有子级"	INTEGER DEFAULT 0,
	"辅助"	TEXT NOT NULL DEFAULT '',
	PRIMARY KEY("id" AUTOINCREMENT)
);
CREATE TABLE "辅助类别表" (
	"id"	INTEGER NOT NULL UNIQUE,
	"辅助类"	TEXT NOT NULL UNIQUE,
	"说明"	TEXT NOT NULL DEFAULT '',
	PRIMARY KEY("id" AUTOINCREMENT)
);
CREATE TABLE "辅助项目表" (
	"id"	INTEGER NOT NULL UNIQUE,
	"类别"	TEXT NOT NULL,
	"辅助"	TEXT NOT NULL,
	"说明"	TEXT NOT NULL DEFAULT '',
	PRIMARY KEY("id" AUTOINCREMENT)
);
INSERT INTO "参数表" ("key","data") VALUES ('单位名称','');
INSERT INTO "参数表" ("key","data") VALUES ('会计准则','');
INSERT INTO "参数表" ("key","data") VALUES ('会计期间','');
INSERT INTO "参数表" ("key","data") VALUES ('启用时间','');
INSERT INTO "参数表" ("key","data") VALUES ('编码方案','');
INSERT INTO "参数表" ("key","data") VALUES ('财务主管','');
INSERT INTO "参数表" ("key","data") VALUES ('会计','');
INSERT INTO "参数表" ("key","data") VALUES ('出纳','');











