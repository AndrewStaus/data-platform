
  
    

        create or replace transient table _dev_analytics.common__astaus.dim_test
         as
        (select * from _dev_analytics.accounts_db__astaus.accounts --noqa:all
        );
      
  