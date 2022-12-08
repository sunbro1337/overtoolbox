# https://perfetto.dev/docs/data-sources/battery-counters
def batt_query(tp):
    print("Querying to tp: battery")
    # batt_all = tp.query("""SELECT ts, value, name, ct.id, c.id FROM counter as c
    # left join counter_track as ct on c.track_id = ct.id
    # where SUBSTRING(ct.name, 1, 4)="batt"
    # order by ct.id and c.id""")

    batt_charge_uah = tp.query("""SELECT ts, value, name, ct.id, c.id FROM counter as c
    left join counter_track as ct on c.track_id = ct.id
    where ct.name="batt.charge_uah"
    order by ct.id and c.id""")

    batt_current_ua = tp.query("""SELECT ts, value, name, ct.id, c.id FROM counter as c
    left join counter_track as ct on c.track_id = ct.id
    where ct.name="batt.current_ua"
    order by ct.id and c.id""")

    batt_capacity_pct = tp.query("""SELECT ts, value, name, ct.id, c.id FROM counter as c
    left join counter_track as ct on c.track_id = ct.id
    where ct.name="batt.capacity_pct"
    order by ct.id and c.id""")
    print("Querying to tp is complete: battery")
    return (None, batt_charge_uah, batt_current_ua, batt_capacity_pct)