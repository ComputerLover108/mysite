-- 中国统计
SELECT "update" as "日期",
       sum("currentConfirmedCount") as "确诊",
       SUM("confirmedCount") as "累计确诊", 
       SUM("deadCount") as "死亡", 
       SUM("curedCount") as "治愈"
FROM "NCP"
WHERE "countryName" ='中国' and "provinceName"=''
GROUP BY "update" 
ORDER BY "update" ;
-- 国外统计
SELECT "update",
       sum("currentConfirmedCount") as "确诊",
       SUM("confirmedCount") as "累计确诊", 
       SUM("deadCount") as "死亡", 
       SUM("curedCount") as "治愈"
FROM "NCP"
WHERE "countryName" !='中国'
GROUP BY "update" 
ORDER BY "update" ;
-- 全球统计
SELECT "update" ,
       sum("currentConfirmedCount") as "确诊",
       SUM("confirmedCount") as "累计确诊", 
       SUM("deadCount") as "死亡", 
       SUM("curedCount") as "治愈"
FROM "NCP"
WHERE "provinceName" = ''
GROUP BY "update"
ORDER BY "update" ;

CREATE DATABASE "COVID-19" OWNER "operator";

BEGIN;
ALTER TABLE IF EXISTS "global" DROP CONSTRAINT "global_unique";
ALTER TABLE IF EXISTS "globalTrend" DROP CONSTRAINT "globalTrend_unique";
ALTER TABLE IF EXISTS "globalSummary" DROP CONSTRAINT "globalSummary_unique";
ALTER TABLE IF EXISTS "country" DROP CONSTRAINT "country_unique";
ALTER TABLE IF EXISTS "province" DROP CONSTRAINT "province_unique";
ALTER TABLE IF EXISTS "news" DROP CONSTRAINT "news_unique";
ALTER TABLE IF EXISTS "rumors" DROP CONSTRAINT "rumors_unique";
ALTER TABLE IF EXISTS "nameMap" DROP CONSTRAINT "nameMap_unique";

DROP TABLE IF EXISTS "globalTrend" CASCADE;
DROP TABLE IF EXISTS "globalSummary" CASCADE;
DROP TABLE IF EXISTS "global" CASCADE;
DROP TABLE IF EXISTS "country" CASCADE;
DROP TABLE IF EXISTS "province" CASCADE;
DROP TABLE IF EXISTS "rumors" CASCADE;
DROP TABLE if EXISTS "news" CASCADE;
DROP TABLE IF EXISTS "nameMap" CASCADE;

CREATE TABLE IF NOT EXISTS "global"(
    "id" serial,
    "update" DATE NOT NULL,
    "continent" VARCHAR,
    "country" VARCHAR,
    "confirmation" INTEGER,
    "totalConfirmation" INTEGER,
    "suspect" INTEGER,
    "cure" INTEGER,
    "dead" INTEGER,
    "remark" VARCHAR    
);

CREATE TABLE IF NOT EXISTS "country" (
    "id" serial,
    "update" DATE NOT NULL,
    "country" VARCHAR,
    "province" VARCHAR,
    "confirmation" INTEGER,
    "totalConfirmation" INTEGER,
    "suspect" INTEGER,
    "cure" INTEGER,
    "dead" INTEGER,
    "remark" VARCHAR    
);

CREATE TABLE IF NOT EXISTS "province" (
    "id" serial,
    "update" DATE NOT NULL,
    "country" VARCHAR,
    "province" VARCHAR,
    "city" VARCHAR,
    "confirmation" INTEGER,
    "totalConfirmation" INTEGER,
    "suspect" INTEGER,
    "cure" INTEGER,
    "dead" INTEGER,
    "remark" VARCHAR  
);
CREATE TABLE IF NOT EXISTS "news" (
    "id" serial NOT NULL,
    "update" date NOT NULL,
    "title" varchar NOT NULL,
    "summary" varchar NULL,
    "infoSource" varchar NULL,
    "sourceUrl" varchar NULL
);
CREATE TABLE IF NOT EXISTS "rumors" (
    "id" serial,
    "update" date NOT null,
    "title" varchar NOT null,
    "summary" varchar,
    "content" varchar
);
CREATE TABLE IF NOT EXISTS "nameMap" (
    "id" serial,
    "name"  varchar not null,
    "EnglishName" varchar not null,
    "shortEnglishName" varchar    
);
CREATE TABLE IF NOT EXISTS "globalTrend" (
    "id" serial,
    "update" date NOT NULL,
    "continent" varchar NULL,
    "country" varchar NOT NULL,
    "currentConfirmedIncr" INTEGER,
    "confirmedIncr" INTEGER,
    "curedIncr" INTEGER,
    "deadIncr" INTEGER,
    "deadRate" real  
);
CREATE TABLE IF NOT EXISTS "globalSummary" (
    "id" serial,
    "update" date NOT NULL,
    "confirm" INTEGER,
    "totalConfirmation" INTEGER,
    "cure" INTEGER,
    "dead" INTEGER,
    "confirmAdd" INTEGER,
    "totalConfirmationAdd" INTEGER,
    "cureAdd" INTEGER,
    "deadAdd" INTEGER,
    "cureRate" REAL,
    "deadRate" REAL
);

ALTER TABLE IF EXISTS "global" ADD CONSTRAINT "global_unique" UNIQUE ("update","continent","country");
ALTER TABLE IF EXISTS "country" ADD CONSTRAINT "country_unique" UNIQUE ("update","country","province");
ALTER TABLE IF EXISTS "province" ADD CONSTRAINT "province_unique" UNIQUE ("update","country","province","city");
ALTER TABLE IF EXISTS "rumors" ADD CONSTRAINT "rumors_unique" UNIQUE ("title","summary","content");
ALTER TABLE IF EXISTS "nameMap" ADD CONSTRAINT "nameMap_unique" UNIQUE ("name","EnglishName","shortEnglishName");
ALTER TABLE IF EXISTS "news" ADD CONSTRAINT "news_unique" UNIQUE ("update","title");
ALTER TABLE IF EXISTS "globalTrend" ADD CONSTRAINT "globalTrend_unique" UNIQUE ("update","continent","country");
ALTER TABLE IF EXISTS "globalSummary" ADD CONSTRAINT "globalSummary_unique" UNIQUE ("update");
-- delete FROM rumors where id not in (SELECT max(id) FROM rumors GROUP by "title","summary","content");
COMMIT;