

select count(*) from dbo.nba_stats





select top 10
    [FIRST LAST NAME],
    sum(points) as total_points,
    count(*) as total_games
from 
	dbo.[data_stats_2024-03-12]
WHERE
    [date] > '2024-03-01'
group by 
	[FIRST LAST NAME]
order by
    total_points desc;





