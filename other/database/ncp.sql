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