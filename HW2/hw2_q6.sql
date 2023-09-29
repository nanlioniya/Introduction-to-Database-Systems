
with "AvgStringencyIndex" as(
	select "CountryName",
			"Date", Avg("StringencyIndex_Average_ForDisplay") as "StringencyIndex_Average_ForDisplay"
	from "status" as s
	natural join "country"
	where "Date" in ('20200601', '20210601', '20220601')
	group by ("CountryName", "Date")
), "MaxStringencyIndex" as (
	select "Continent_Name",
			"Date", MAX("StringencyIndex_Average_ForDisplay") as "MaxStringencyIndex"
	from "AvgStringencyIndex" as asi
	natural join "country"
	group by ("Continent_Name", "Date")
)
select "CountryName", msi."Continent_Name",
			msi."Date", "MaxStringencyIndex"
from "MaxStringencyIndex" as msi
join ("AvgStringencyIndex" natural join "country") as avgc on
avgc."Date" = msi."Date" and avgc."StringencyIndex_Average_ForDisplay" = msi."MaxStringencyIndex"
and avgc."Continent_Name" = msi."Continent_Name"
order by "Continent_Name" asc, "Date" asc