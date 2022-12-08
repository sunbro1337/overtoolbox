def gpu_query(tp):
    print("Querying to tp: GPU")
    GPU_utilization_data = tp.query("""SELECT ts, value FROM counter as c
    left join counter_track as ct on c.track_id = ct.id
    where ct.name="GPU utilization"
    order by ct.id and c.id""")
    GPU_utilization_details = tp.query("""SELECT name, description FROM counter as c
    left join counter_track as ct on c.track_id = ct.id
    where ct.name="GPU utilization"
    LIMIT 1""")
    print("Querying to tp is complete: GPU")
    return (GPU_utilization_data, GPU_utilization_details)