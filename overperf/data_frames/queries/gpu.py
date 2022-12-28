def gpu_query_mali(tp):
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
    return {
        'GPU_utilization_data': GPU_utilization_data,
        'GPU_utilization_details': GPU_utilization_details,
    }

def gpu_query_adreno(tp):
    print("Querying to tp: GPU")
    GPU_utilization_data = tp.query("""SELECT ts, value FROM counter as c
        left join counter_track as ct on c.track_id = ct.id
        where ct.name="GPU % Utilization"
        order by ct.id and c.id""")
    GPU_utilization_details = tp.query("""SELECT name, description FROM counter as c
        left join counter_track as ct on c.track_id = ct.id
        where ct.name="GPU % Utilization"
        LIMIT 1""")
    GPU_time_alus_working_data = tp.query("""SELECT * FROM counter as c
        left join counter_track as ct on c.track_id = ct.id
        where ct.name="% Time ALUs Working"
        order by ct.id and c.id""")
    GPU_time_alus_working_details = tp.query("""SELECT name, description FROM counter as c
        left join counter_track as ct on c.track_id = ct.id
        where ct.name="% Time ALUs Working"
        LIMIT 1""")
    print("Querying to tp is complete: GPU")
    return {
        'GPU_utilization_data': GPU_utilization_data,
        'GPU_utilization_details': GPU_utilization_details,
        'GPU_time_alus_working_data': GPU_time_alus_working_data,
        'GPU_time_alus_working_details': GPU_time_alus_working_details,
    }
