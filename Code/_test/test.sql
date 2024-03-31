

select 
    player_id,
    CONCAT(firstname,' ',lastname) as full_name
from 
    dbo.[data_stats_2024-03-12]



SELECT ROW_NUMBER() OVER (ORDER BY (SELECT NULL)) AS Row_Order, *
FROM dbo.[nba_players];


select top 10
    [FIRST LAST NAME],
    [team],
    [position],
    sum(points) as total_points,
    count(*) as total_games,
    sum(points) / count(*) as avg_points
from
	dbo.[data_stats_2024-03-12]
where
    [date] > '2024-03-01'
group by
	[FIRST LAST NAME],
    [team],
    [position]
having
    sum(points) > 100
order by
    avg_points desc;




with over_25 as (
    select
        [FIRST LAST NAME],
        round(cast(sum(points) as float) / cast(count(*) as float),1) as Avg_points,
        sum(points) as total_points
    from
        dbo.[data_stats_2024-03-12]
    where
        [date] > '2024-03-01'
    group by 
        [FIRST LAST NAME]
    having
        sum(points) > 150
)
select top 25
    [FIRST LAST NAME],
    Avg_points
from 
    over_25
order by
    Avg_Points desc;
    



select 
	a.product_account_id,
	a.entry_week,
	a.entry_sport,
	a.contest_type,
	a.entry_source,
	a.weekly_entry_fee,
	a.weely_total_entry_winnings,
	a.total_entries,
	a.avg_contest_size,
    b.registration_date,
	b.first_deposit_date,
	b.first_paid_entry_date,
	b.first_deposit_amount,
	b.registration_paid_media_partner_name,
	b.first_deposit_paid_media_partner_name,
	b.first_paid_entry_paid_media_partner_name,
	b.registration_state
into dbo.temp_matched
from dbo.analyst_manager_technical_assesment_entry_data a
inner join dbo.analyst_manager_technical_assesment_user_data b
on a.product_account_id = b.product_account_id;



SELECT
    a.team,
    a.player_id,
    b.[First Last Name]
into dbo.TEMP
from dbo.nba_stats a 
inner join dbo.nba_players b
on a.[First Last Name] = b.[First Last Name]



