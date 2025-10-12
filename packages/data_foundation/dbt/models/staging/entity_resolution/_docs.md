{% docs individual_party_key %}

Represents an individual as understood by the system of record as of the
time the interaction with the individual took place.  This is used in conjunction
with an individual_id to connect across multiple systems to understand
a single entity.

Records from seperate systems should use the non-unique party key to join to the
individual entity table, and then be agregated to on the entity id to understand
inteactions of the same customer.

*Example*:
``` sql
select
    e.individual_id,
    sum(t.revenue) revenue,
    count(distinct visit_id) visits 

from transactions t
left join individual_entity e
    on t.individual_party_key = e.individual_party_key
left join site_visits v
    on v.individual_party_key = e.individual_party_key
group by e.individual_entity_id
```

{% enddocs %}

{% docs individual_id %}

Represents an individual as understood by the entity resolution system.
A single individual will have multiple party keys, however they will all resolve to the
same entity id.

*Example*:
``` sql
select
    e.individual_id,
    sum(t.revenue) revenue,
    count(distinct visit_id) visits 

from transactions t
left join individual_entity e
    on t.individual_party_key = e.individual_party_key
left join site_visits v
    on v.individual_party_key = e.individual_party_key
group by e.individual_entity_id
```

{% enddocs %}