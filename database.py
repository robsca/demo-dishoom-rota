import sqlite3

def create_table():
    conn = sqlite3.connect('Constraints.db')
    c = conn.cursor()

    # constraints has site_code, departments, month, day, actual_hours, budget_hours, labour_model_hours
    c.execute('''CREATE TABLE constraints
                    (site_code text, departments text, month text, day text, actual_hours real, budget_hours real, labour_model_hours real)''')

    conn.commit()
    conn.close()

def insert_data_test():
    conn = sqlite3.connect('Constraints.db')
    c = conn.cursor()
    # insert data
    c.execute("INSERT INTO constraints VALUES ('site1', 'dept1', 'Jan', 'Mon', 1, 2, 3)")
    c.execute("INSERT INTO constraints VALUES ('site1', 'dept1', 'Jan', 'Tue', 1, 2, 3)")
    c.execute("INSERT INTO constraints VALUES ('site1', 'dept1', 'Jan', 'Wed', 1, 2, 3)")
    c.execute("INSERT INTO constraints VALUES ('site1', 'dept1', 'Jan', 'Thu', 1, 2, 3)")
    c.execute("INSERT INTO constraints VALUES ('site1', 'dept1', 'Jan', 'Fri', 1, 2, 3)")
    c.execute("INSERT INTO constraints VALUES ('site1', 'dept1', 'Jan', 'Sat', 1, 2, 3)")
    c.execute("INSERT INTO constraints VALUES ('site1', 'dept1', 'Jan', 'Sun', 1, 2, 3)")
    # commit changes
    conn.commit()
    conn.close()

def insert_data(site_code, departments, month, day, actual_hours, budget_hours, labour_model_hours):
    conn = sqlite3.connect('Constraints.db')
    c = conn.cursor()
    # insert data
    c.execute("INSERT INTO constraints VALUES (?, ?, ?, ?, ?, ?, ?)", (site_code, departments, month, day, actual_hours, budget_hours, labour_model_hours))
    # commit changes
    conn.commit()
    conn.close()

def get_data():
    conn = sqlite3.connect('Constraints.db')
    c = conn.cursor()

    # get data
    c.execute("SELECT * FROM constraints")
    all = c.fetchall()
    conn.commit()
    conn.close()
    return all

def delete_data():
    conn = sqlite3.connect('Constraints.db')
    c = conn.cursor()

    c.execute("DELETE FROM constraints")
    conn.commit()
    conn.close()

def create_shift_table():
    conn = sqlite3.connect('Shifts.db')
    c = conn.cursor()

    # constraints has site_code, departments, month, day, actual_hours, budget_hours, labour_model_hours
    c.execute('''CREATE TABLE shifts
                    (site_code text, departments text, month text, day text, start_time text, end_time text)''')

    conn.commit()
    conn.close()

def insert_shift_data(site_code, departments, month, day, start_time, end_time):
    conn = sqlite3.connect('Shifts.db')
    c = conn.cursor()
    # insert data
    c.execute("INSERT INTO shifts VALUES (?, ?, ?, ?, ?, ?)", (site_code, departments, month, day, start_time, end_time))
    # commit changes
    conn.commit()
    conn.close()

def get_shift_data():
    conn = sqlite3.connect('Shifts.db')
    c = conn.cursor()

    # get data
    c.execute("SELECT * FROM shifts")
    all = c.fetchall()
    conn.commit()
    conn.close()
    return all

def delete_shift_data():
    conn = sqlite3.connect('Shifts.db')
    c = conn.cursor()

    c.execute("DELETE FROM shifts")
    conn.commit()
    conn.close()

''''''
# create a table to store the rota day by day
def create_rota_table():
    conn = sqlite3.connect('Rota.db')
    c = conn.cursor()

    # constraints has site_code, departments, month, day, actual_hours, budget_hours, labour_model_hours
    c.execute('''CREATE TABLE rota
                    (site_code text, departments text, month text, day text, start_time text, end_time text)''')

    conn.commit()
    conn.close()

def insert_rota_data(site_code, departments, month, day, start_time, end_time):
    # if the rota for that day already exists, delete it
    conn = sqlite3.connect('Rota.db')
    c = conn.cursor()
    # insert data
    c.execute("INSERT INTO rota VALUES (?, ?, ?, ?, ?, ?)", (site_code, departments, month, day, start_time, end_time))
    # commit changes
    conn.commit()
    conn.close()

def get_rota_data():
    conn = sqlite3.connect('Rota.db')
    c = conn.cursor()

    # get data
    c.execute("SELECT * FROM rota")
    all = c.fetchall()
    conn.commit()
    conn.close()
    return all

def delete_rota_data():
    conn = sqlite3.connect('Rota.db')
    c = conn.cursor()

    c.execute("DELETE FROM rota")
    conn.commit()
    conn.close()

def delete_rota_data_same_day(day):
    conn = sqlite3.connect('Rota.db')
    c = conn.cursor()

    c.execute("DELETE FROM rota WHERE day = ?", (day,))
    conn.commit()
    conn.close()
# now same for shifts that contain 
if __name__ == '__main__':
    #create_table()
    #delete_data()
    #insert_data_test()
    #create_shift_table()
    create_rota_table()