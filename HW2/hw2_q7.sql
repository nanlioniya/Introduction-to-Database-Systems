with "AvgStringencyIndex" as(
	select "CountryName", "Date", 
		Avg("StringencyIndex_Average_ForDisplay") as "StringencyIndex_Average_ForDisplay"
	from "status" as s
	natural join "country"
	where "Date" in ('20200601', '20210601', '20220601')
	group by ("CountryName", "Date")
), "7dMovingAvg" as (
	select t1."CountryName", t1."Date", 
	(case when (t1."ConfirmedCases"-t2."ConfirmedCases")/7 = 0 then 0.1
	else (t1."ConfirmedCases"-t2."ConfirmedCases")/7 end) as "MovingAvg"
	from "status" as t1 join "status" as t2 
	using ("CountryName")
	where (t1."Date" = '20200601' and t2."Date" = '20200525') or (t1."Date" = '20210601' and t2."Date" = '20210525') or (t1."Date" = '20220601' and t2."Date" = '20220525')  
), 
"OverStringencyIndex" as (
	select "CountryName", "Date", 
		("StringencyIndex_Average_ForDisplay"/"MovingAvg") as "osi"
	from "7dMovingAvg" natural join "AvgStringencyIndex"
), "MaxOSI" as (
	select "Continent_Name",
			"Date", MAX("osi") as "MaxStringencyIndex"
	from "OverStringencyIndex" as osi
	natural join "country"
	group by ("Continent_Name", "Date")
)
select "CountryName", "MaxOSI"."Continent_Name",
			"MaxOSI"."Date", "MaxStringencyIndex"
from "MaxOSI"
join ("OverStringencyIndex" natural join "country") as osic on
osic."Date" = "MaxOSI"."Date" and osic."osi" = "MaxOSI"."MaxStringencyIndex"
and osic."Continent_Name" = "MaxOSI"."Continent_Name"
order by "Continent_Name" asc, "Date" asc