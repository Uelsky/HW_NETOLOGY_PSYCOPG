import psycopg2


def create_db(cur):
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS clients(
            id SERIAL PRIMARY KEY,
            first_name VARCHAR(30) NOT NULL,
            last_name VARCHAR(30) NOT NULL,
            email VARCHAR(60) NOT NULL
            );
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS phone_nums(
            id SERIAL PRIMARY KEY,
            phone_num VARCHAR(12) NOT NULL,
            client_id INTEGER REFERENCES clients(id)
        );
        """
    )


def add_client(cur, first_name, last_name, email, phones=None):
    cur.execute(
        """
        INSERT INTO clients (first_name, last_name, email)
        VALUES(%s, %s, %s)
        RETURNING id;
        """, (first_name, last_name, email)
    )
    client_id = cur.fetchone()[0]

    if phones is not None:
        for phone in phones:
            cur.execute(
                """
                INSERT INTO phone_nums (phone_num, client_id)
                VALUES(%s, %s);
                """, (phone, client_id)
            )


def add_phone(cur, client_id, phone):
    cur.execute(
        """
        INSERT INTO phone_nums (phone_num, client_id)
        VALUES(%s, %s);
        """, (phone, client_id)
    )


def change_client(cur, client_id, first_name=None, last_name=None, email=None, phones=None):
    if first_name is None:
        cur.execute(
            """
            SELECT first_name
            FROM clients
            WHERE id = %s;
            """, (client_id,)
        )
        first_name = cur.fetchone()[0]

    if last_name is None:
        cur.execute(
            """
            SELECT last_name
            FROM clients
            WHERE id = %s;
            """, (client_id,)
        )
        last_name = cur.fetchone()[0]

    if email is None:
        cur.execute(
            """
            SELECT email
            FROM clients
            WHERE id = %s;
            """, (client_id,)
        )
        email = cur.fetchone()[0]

    if phones is None:
        cur.execute(
            """
            SELECT phone_num
            FROM phone_nums
            WHERE client_id = %s;
            """, (client_id,)
        )
        phones = cur.fetchall()

    cur.execute(
        """
        UPDATE clients
        SET first_name = %s, last_name = %s, email = %s
        WHERE id = %s;
        """, (first_name, last_name, email, client_id)
    )

    cur.execute(
        """
        DELETE FROM phone_nums
        WHERE client_id = %s;
        """, (client_id,)
    )

    for phone in phones:
        cur.execute(
            """
            INSERT INTO phone_nums (phone_num, client_id)
            VALUES(%s, %s);
            """, (phone, client_id)
        )


def delete_phone(cur, client_id, phone):
    cur.execute(
        """
        DELETE FROM phone_nums
        WHERE client_id = %s
        AND phone_num = %s;
        """, (client_id, phone)
    )


def delete_client(cur, client_id):
    cur.execute(
        """
        SELECT phone_num
        FROM phone_nums
        WHERE client_id = %s;
        """, (client_id,)
    )
    phones = cur.fetchall()

    if len(phones) != 0:
        cur.execute(
            """
            DELETE FROM phone_nums
            WHERE client_id = %s;
            """, (client_id,)
        )

    cur.execute(
        """
        DELETE FROM clients
        WHERE id = %s; 
        """, (client_id,)
    )


def find_client(cur, first_name=None, last_name=None, email=None, phone=None):
    if email is not None:
        if (
                first_name is not None and
                last_name is not None
        ):
            cur.execute(
                """
                SELECT *
                FROM clients
                WHERE first_name = %s
                AND last_name = %s
                AND email = %s;
                """, (first_name, last_name, email)
            )
            print(cur.fetchone())

        elif (
                first_name is not None and
                last_name is None
        ):
            cur.execute(
                """
                SELECT *
                FROM clients
                WHERE first_name = %s
                AND email = %s;
                """, (first_name, email)
            )
            print(cur.fetchone())

        elif (
                first_name is None and
                last_name is not None
        ):
            cur.execute(
                """
                SELECT *
                FROM clients
                WHERE last_name = %s
                AND email = %s;
                """, (last_name, email)
            )
            print(cur.fetchone())

        elif (
                first_name is None and
                last_name is None
        ):
            cur.execute(
                """
                SELECT *
                FROM clients
                WHERE email = %s;
                """, (email,)
            )
            print(cur.fetchone())

    elif phone is not None:
        cur.execute(
            """
            SELECT c.id, c.first_name, c.last_name, c.email
            FROM phone_nums pn
            JOIN clients c ON c.id = pn.client_id
            WHERE phone_num = %s;
            """, (phone,)
        )
        print(cur.fetchone())


if __name__ == "__main__":
    print('\n'.join([
        "Enter name of your DB",
        "Enter username",
        "Enter password",
        "====================="
    ]))

    db = input()
    username = input()
    passwd = input()

    conn = psycopg2.connect(
        database = db,
        user = username,
        password = passwd
    )

    with conn.cursor() as cur:
        cur.execute(
            """
            DROP TABLE phone_nums;
            DROP TABLE clients;
            """
        )
        conn.commit()

        create_db(cur)
        conn.commit()

        add_client(
            cur, 'Rob',
            'Halford',
            'judas_priest@gmail.com',
            ['89991112233', '89267334231']
        )
        conn.commit()

        add_client(
            cur, 'Till',
            'Lindemann',
            'rammstein@gmail.com',
            ['89991112233']
        )
        conn.commit()

        add_client(
            cur, 'Udo',
            'Dirkschneider',
            'accept@gmail.com'
        )
        conn.commit()

        add_client(
            cur, 'Paul',
            'Stanley',
            'kiss_band@gmail.com',
            ['89991112233', '89267334231', '89777772727']
        )
        conn.commit()

        add_phone(
            cur, 3,
            '84993331212'
        )
        conn.commit()

        change_client(
            cur, 2,
            None,None,
            'lindemann@gmail.com'
        )
        conn.commit()

        delete_phone(
            cur, 4,
            '89267334231'
        )
        conn.commit()

        delete_client(cur, 1)
        conn.commit()

        find_client(
            cur, 'Paul',
            'Stanley',
            'kiss_band@gmail.com'
        )

        find_client(
            cur, None,
            None, None,
            '89991112233'
        )


    conn.close()