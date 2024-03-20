--Check files
--select * from dbo.analyst_manager_technical_assesment_entry_data
select count(*) from dbo.analyst_manager_technical_assesment_entry_data

--select * from dbo.analyst_manager_technical_assesment_user_data
select count(*) from dbo.analyst_manager_technical_assesment_user_data

select count(*) from dbo.temp_matched

--Join
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

--------------------------------------------------------------------------------------
--1 Top top paid entry media partners
select top 10
    first_paid_entry_paid_media_partner_name,
    count(*) as total_users
from 
	dbo.temp_matched
group by 
	first_paid_entry_paid_media_partner_name
order by
    total_users desc;


--------------------------------------------------------------------------------------
--2 Top 10 First Paid entry credit.
-- Question, is the entry fee grouped by week? All i see is weekly_entry_fee
-- I did all Septembers but commented out if it was just like September of a specific year
select min(first_paid_entry_date),max(first_paid_entry_date)
from dbo.temp_matched

select top 10
    first_paid_entry_paid_media_partner_name,
    count(*) as total_users,
	format(sum(weekly_entry_fee),'C','en-US') as total_entry_fees,
	format(avg(weekly_entry_fee),'C','en-US') as avg_entry_fee
from 
	dbo.temp_matched
where
	month(first_paid_entry_date) = 9
	--first_paid_entry_date >= '2020-09-01' and
	--first_paid_entry_date < '2020-10-01'
group by 
	first_paid_entry_paid_media_partner_name
order by
    total_users desc;

--------------------------------------------------------------------------------------
--3 Most users with atleast $100
with over_100 as (
    select
        first_paid_entry_paid_media_partner_name,
        product_account_id,
        sum(weekly_entry_fee) as Total_Entry_Fees
    from
        dbo.temp_matched
    group by 
        first_paid_entry_paid_media_partner_name,
        product_account_id
    having
        sum(weekly_entry_fee) > 100
)
select top 10
    first_paid_entry_paid_media_partner_name,
    count(distinct product_account_id) as Users_Count
from
    over_100
group by
    first_paid_entry_paid_media_partner_name
order by
    Users_Count desc;

--------------------------------------------------------------------------------------

