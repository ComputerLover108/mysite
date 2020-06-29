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
ALTER TABLE IF EXISTS "global" ADD CONSTRAINT global_unique UNIQUE ("update","continent","country");
ALTER TABLE IF EXISTS "country" ADD CONSTRAINT country_unique UNIQUE ("update","country","province");
ALTER TABLE IF EXISTS "province" ADD CONSTRAINT province_unique UNIQUE ("update","country","province","city");

CREATE TABLE IF NOT EXISTS "nameMap" (
    "name" VARCHAR NOT NULL,
    "EnglishName" VARCHAR NOT NULL
);
ALTER TABLE IF EXISTS "nameMap" ADD CONSTRAINT "nameMap_unique" UNIQUE ("name","EnglishName");

BEGIN;
DROP TABLE IF EXISTS rumors;
CREATE TABLE IF NOT EXISTS rumors (
    id serial,
    update date NOT null,
    title varchar NOT null,
    summary varchar,
    content varchar
) ;
ALTER TABLE IF EXISTS rumors ADD CONSTRAINT rumors_unique UNIQUE (update,title);
COMMIT;