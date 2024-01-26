import sqlite3

# Save results to a database instead of pickle file
conn = sqlite3.connect('results.db')
c = conn.cursor()

def save_results(results):
    c.execute('''INSERT INTO results (winner, score) VALUES (?, ?)''', 
              (results['winner'], results['score']))
    conn.commit()

def get_results():
    """Fetches results from the database table"""
    c.execute('SELECT * FROM results')
    return c.fetchall()
# Track and update results

""" def update_results():
   # 1. Get latest results   
   # 2. Update database """