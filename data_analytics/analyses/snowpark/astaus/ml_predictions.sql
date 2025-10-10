use _dev_analytics.open_data__astaus;

with results as (
    with mv as model titanic_survived -- noqa
    select
        survived,
        mv ! predict(sex, embarked, boat, age, pclass, fare, sibsp, parch):PRED pred
    from
        titanic
)

select
    count(case when survived = pred and survived = 1 then 1 end)  tp,
    count(case when survived = pred and survived = 0 then 1 end)  tn,
    count(case when survived != pred and survived = 0 then 1 end) fp,
    count(case when survived != pred and survived = 1 then 1 end) fn,
    tp / (tp + fp)                                                prec,
    tp / (tp + fn)                                                recall,
    (2 * prec * recall) / (prec + recall)                         f1
from results;
