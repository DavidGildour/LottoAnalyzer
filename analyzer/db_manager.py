from analyzer.postgres_db import get_db


def connection_handler(func):
    def wrapper(*args, **kwargs):
        with get_db() as conn:
            with conn.cursor() as cur:
                res = func(cur, *args, **kwargs)
        return res

    return wrapper


@connection_handler
def get_records_by_numbers(cur, numbers):
    param_dict = {str(k): v for k, v in enumerate(numbers)}
    sql = ("select id, date, concat_ws(' ', l1, l2, l3, l4, l5, l6) as lotto, "
           "concat_ws(' ', p1, p2, p3, p4, p5, p6) as plus, 'lotto' as typ from lotto where ")
    sql += " and ".join([f"%({i})s in (l1,l2,l3,l4,l5,l6)" for i, _ in enumerate(numbers)])
    sql += (" union select id, date, concat_ws(' ', l1, l2, l3, l4, l5, l6) as lotto, "
            "concat_ws(' ', p1, p2, p3, p4, p5, p6) as plus, 'plus' as typ from lotto where")
    sql += " and ".join([f"%({i})s in (p1,p2,p3,p4,p5,p6)" for i, _ in enumerate(numbers)])
    sql += ";"
    cur.execute(sql, param_dict)
    return cur.fetchall()
