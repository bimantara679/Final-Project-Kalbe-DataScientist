select s.storename, sum(t.qty) as total_qty 
from store s 
join "transaction" t 
on s.storeid = t.storeid 
group by s.storename 
order by total_qty desc 



select s.storename, sum(t.qty) as total_qty 
from store s 
join "transaction" t 
on s.storeid = t.storeid 
group by s.storename 
order by total_qty desc 
limit 1



select "Marital Status", AVG(age) AS AverageAge
from customer 
group by "Marital Status" 



select gender, AVG(age) AS AverageAge
from customer 
group by gender


select p."Product Name", sum(t.totalamount) as sum_totalamount 
from product p 
join "transaction" t 
on p.productid = t.productid 
group by p."Product Name" 
order by sum_totalamount desc 